"""Git integration logic for MarkForge – no Qt imports.

HTTPS operations use each platform's REST API directly (GitHub Contents API,
Bitbucket Cloud src API, Bitbucket Server browse API).  This is more reliable
than dulwich's HTTP transport, which can fail on Windows due to TLS/proxy
differences with corporate Bitbucket Server instances.

SSH operations still use dulwich + paramiko (pure Python, no git executable).
"""

from __future__ import annotations

import base64
import io
import json
import os
import shutil
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclass
class GitFileInfo:
    platform:        str   # "github" | "github_enterprise" | "bitbucket" | "bitbucket_server"
    owner:           str   # GitHub: owner login; Bitbucket Server: project key
    repo:            str
    branch:          str
    file_path:       str   # relative path inside repo (forward slashes)
    clone_url:       str   # https clone URL (no credentials)
    base_url:        str   # scheme + host, e.g. "https://bitbucket.mycompany.com"
    local_repo_path: str = ""
    local_file_path: str = ""
    # Stored during download; required for some platform commit APIs:
    # GitHub/GHE → blob SHA; Bitbucket Server → latest commit ID
    file_sha:        str = ""


@dataclass
class CommitSpec:
    message:    str
    push_mode:  str        # "current_branch" | "new_branch"
    new_branch: str  = ""
    create_pr:  bool = False
    pr_title:   str  = ""
    pr_target:  str  = ""


# ── URL parsing ───────────────────────────────────────────────────────────────

def parse_git_url(url: str) -> GitFileInfo:
    """Parse a file URL from any GitHub/Bitbucket host into a GitFileInfo.

    Platform is detected from the URL *path structure*, not the hostname,
    so self-hosted GitHub Enterprise and Bitbucket Server instances work too.

    Supported path patterns
    -----------------------
    GitHub / GitHub Enterprise:
        /owner/repo/blob/branch/path/to/file.md

    Bitbucket Cloud:
        /owner/repo/src/branch/path/to/file.md

    Bitbucket Server / Data Center:
        /projects/PROJECT/repos/repo/browse/path/to/file.md?at=branch
        (the ?at= parameter may be omitted; defaults to "main")

    Raises ValueError with a human-readable message on any problem.
    """
    parsed   = urlparse(url.strip())
    host     = parsed.hostname or ""
    scheme   = parsed.scheme or "https"
    base_url = f"{scheme}://{host}"

    parts = [p for p in parsed.path.split("/") if p]

    # ── Bitbucket Server / Data Center ────────────────────────────────────────
    # Path: /projects/PROJECT/repos/REPO/browse/path/to/file[?at=branch]
    if (
        len(parts) >= 5
        and parts[0].lower() == "projects"
        and parts[2].lower() == "repos"
        and parts[4].lower() == "browse"
    ):
        project_key = parts[1]
        repo        = parts[3]
        file_path   = "/".join(parts[5:])

        if not file_path:
            raise ValueError("The URL does not point to a file (file path is empty).")

        # Branch from ?at= query param; strip refs/heads/ / refs/tags/ prefix
        qs = parse_qs(parsed.query)
        at = qs.get("at", ["main"])[0]
        branch = at
        for prefix in ("refs/heads/", "refs/tags/"):
            if branch.startswith(prefix):
                branch = branch[len(prefix):]
                break

        # Bitbucket Server clone URL uses /scm/project/repo.git
        clone_url = f"{base_url}/scm/{project_key.lower()}/{repo}.git"

        return GitFileInfo(
            platform="bitbucket_server",
            owner=project_key,
            repo=repo,
            branch=branch,
            file_path=file_path,
            clone_url=clone_url,
            base_url=base_url,
        )

    # ── GitHub / GitHub Enterprise ────────────────────────────────────────────
    # Path: /owner/repo/blob/branch/path/to/file.md
    if len(parts) >= 5 and parts[2].lower() == "blob":
        owner     = parts[0]
        repo      = parts[1]
        branch    = parts[3]
        file_path = "/".join(parts[4:])

        if not file_path:
            raise ValueError("The URL does not point to a file (file path is empty).")

        clone_url = f"{base_url}/{owner}/{repo}.git"
        platform  = "github" if host == "github.com" else "github_enterprise"

        return GitFileInfo(
            platform=platform,
            owner=owner,
            repo=repo,
            branch=branch,
            file_path=file_path,
            clone_url=clone_url,
            base_url=base_url,
        )

    # ── Bitbucket Cloud ───────────────────────────────────────────────────────
    # Path: /owner/repo/src/branch/path/to/file.md
    if len(parts) >= 5 and parts[2].lower() == "src":
        owner     = parts[0]
        repo      = parts[1]
        branch    = parts[3]
        file_path = "/".join(parts[4:])

        if not file_path:
            raise ValueError("The URL does not point to a file (file path is empty).")

        clone_url = f"https://bitbucket.org/{owner}/{repo}.git"

        return GitFileInfo(
            platform="bitbucket",
            owner=owner,
            repo=repo,
            branch=branch,
            file_path=file_path,
            clone_url=clone_url,
            base_url=base_url,
        )

    raise ValueError(
        "Could not recognise URL format. Supported patterns:\n"
        "  GitHub / GHE:          …/owner/repo/blob/branch/file.md\n"
        "  Bitbucket Cloud:       …/owner/repo/src/branch/file.md\n"
        "  Bitbucket Server/DC:   …/projects/PROJ/repos/repo/browse/file.md?at=branch"
    )


# ── Auth helpers ──────────────────────────────────────────────────────────────

def _build_https_clone_url(base: str, user: str, token: str) -> str:
    """Embed credentials into an HTTPS clone URL."""
    scheme = base.split("://")[0]
    return base.replace(f"{scheme}://", f"{scheme}://{user}:{token}@", 1)


def _ssh_clone_url(info: GitFileInfo) -> str:
    """Return the SSH clone URL for *info*."""
    host = urlparse(info.base_url).hostname or ""
    if info.platform == "bitbucket_server":
        return f"ssh://git@{host}/scm/{info.owner.lower()}/{info.repo}.git"
    else:
        return f"git@{host}:{info.owner}/{info.repo}.git"


# ── HTTPS REST API helpers ─────────────────────────────────────────────────────

def _https_headers(settings, platform: str) -> dict[str, str]:
    """Return request headers with Authorization for HTTPS REST API calls."""
    user  = settings.value("git/https_username", "")
    token = settings.value("git/https_token",    "")
    headers: dict[str, str] = {"User-Agent": "MarkForge", "Accept": "application/json"}
    if user and token:
        if platform in ("github", "github_enterprise"):
            headers["Authorization"] = f"token {token}"
        else:
            creds = base64.b64encode(f"{user}:{token}".encode()).decode()
            headers["Authorization"] = f"Basic {creds}"
    return headers


def _http_get(url: str, headers: dict) -> bytes:
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        if exc.code == 401:
            raise RuntimeError("Authentication failed (HTTP 401). Check credentials.") from exc
        raise RuntimeError(f"HTTP {exc.code}: {exc.reason}") from exc


def _http_json(url: str, headers: dict, payload: dict, method: str = "POST") -> bytes:
    data = json.dumps(payload).encode()
    h = {**headers, "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        if exc.code == 401:
            raise RuntimeError("Authentication failed (HTTP 401). Check credentials.") from exc
        raise RuntimeError(f"HTTP {exc.code}: {exc.reason}\n{body[:300]}") from exc


def _http_multipart(url: str, headers: dict,
                    fields: list[tuple[str, str, bytes]],
                    method: str = "PUT") -> bytes:
    """Send a multipart/form-data request.

    *fields* is a list of (name, filename, data) tuples.
    Leave *filename* empty for plain text fields.
    """
    boundary = b"----------MarkForgeBoundary7MA4YWxkTrZu0gW"
    parts = []
    for name, filename, data in fields:
        disp = f'form-data; name="{name}"'
        if filename:
            disp += f'; filename="{filename}"'
        parts.append(
            b"--" + boundary + b"\r\n"
            + f"Content-Disposition: {disp}\r\n\r\n".encode()
            + data + b"\r\n"
        )
    parts.append(b"--" + boundary + b"--\r\n")
    body = b"".join(parts)
    h = {**headers, "Content-Type": f"multipart/form-data; boundary={boundary.decode()}"}
    req = urllib.request.Request(url, data=body, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace")
        if exc.code == 401:
            raise RuntimeError("Authentication failed (HTTP 401). Check credentials.") from exc
        raise RuntimeError(f"HTTP {exc.code}: {exc.reason}\n{body_text[:300]}") from exc


# ── HTTPS: download / upload file ─────────────────────────────────────────────

def _download_file(info: GitFileInfo, settings) -> tuple[bytes, str]:
    """Fetch the file via the platform REST API.

    Returns *(content_bytes, sha_or_commit_id)*.
    The second element is stored in info.file_sha and passed back to
    _upload_file when committing (GitHub needs the blob SHA; Bitbucket Server
    accepts an optional sourceCommitId).
    """
    h = _https_headers(settings, info.platform)

    if info.platform == "github":
        url = (f"https://api.github.com/repos/{info.owner}/{info.repo}"
               f"/contents/{info.file_path}?ref={info.branch}")
        raw = json.loads(_http_get(url, h))
        return base64.b64decode(raw["content"].replace("\n", "")), raw["sha"]

    if info.platform == "github_enterprise":
        url = (f"{info.base_url}/api/v3/repos/{info.owner}/{info.repo}"
               f"/contents/{info.file_path}?ref={info.branch}")
        raw = json.loads(_http_get(url, h))
        return base64.b64decode(raw["content"].replace("\n", "")), raw["sha"]

    if info.platform == "bitbucket":
        url = (f"https://api.bitbucket.org/2.0/repositories/{info.owner}/{info.repo}"
               f"/src/{info.branch}/{info.file_path}")
        return _http_get(url, h), ""

    if info.platform == "bitbucket_server":
        raw_url = (f"{info.base_url}/rest/api/1.0/projects/{info.owner}"
                   f"/repos/{info.repo}/raw/{info.file_path}?at={info.branch}")
        content = _http_get(raw_url, h)
        # Fetch the latest commit ID (used as sourceCommitId to avoid conflicts)
        commit_url = (f"{info.base_url}/rest/api/1.0/projects/{info.owner}"
                      f"/repos/{info.repo}/commits?until={info.branch}&limit=1")
        try:
            commit_data = json.loads(_http_get(commit_url, h))
            commit_id = commit_data["values"][0]["id"]
        except Exception:
            commit_id = ""
        return content, commit_id

    raise ValueError(f"Unknown platform: {info.platform!r}")


def _upload_file(info: GitFileInfo, spec: CommitSpec,
                 settings, new_content: bytes) -> None:
    """Commit the file (and optionally a new branch) via the platform REST API."""
    h = _https_headers(settings, info.platform)
    push_branch = (spec.new_branch
                   if spec.push_mode == "new_branch" and spec.new_branch
                   else info.branch)

    # ── GitHub / GitHub Enterprise ────────────────────────────────────────────
    if info.platform in ("github", "github_enterprise"):
        base = ("https://api.github.com" if info.platform == "github"
                else f"{info.base_url}/api/v3")

        if spec.push_mode == "new_branch" and spec.new_branch:
            # Resolve current branch tip SHA, then create the new branch
            ref_url  = f"{base}/repos/{info.owner}/{info.repo}/git/refs/heads/{info.branch}"
            ref_data = json.loads(_http_get(ref_url, h))
            tip_sha  = ref_data["object"]["sha"]
            _http_json(f"{base}/repos/{info.owner}/{info.repo}/git/refs", h, {
                "ref": f"refs/heads/{spec.new_branch}",
                "sha": tip_sha,
            })

        payload: dict = {
            "message": spec.message,
            "content": base64.b64encode(new_content).decode(),
            "branch":  push_branch,
        }
        if info.file_sha:
            payload["sha"] = info.file_sha   # required when updating an existing file

        url = f"{base}/repos/{info.owner}/{info.repo}/contents/{info.file_path}"
        _http_json(url, h, payload, method="PUT")

    # ── Bitbucket Cloud ───────────────────────────────────────────────────────
    elif info.platform == "bitbucket":
        if spec.push_mode == "new_branch" and spec.new_branch:
            tip_url  = (f"https://api.bitbucket.org/2.0/repositories/{info.owner}/{info.repo}"
                        f"/refs/branches/{info.branch}")
            tip_data = json.loads(_http_get(tip_url, h))
            tip_hash = tip_data["target"]["hash"]
            _http_json(
                f"https://api.bitbucket.org/2.0/repositories/{info.owner}/{info.repo}/refs/branches",
                h,
                {"name": spec.new_branch, "target": {"hash": tip_hash}},
            )

        # POST to /src/; the file field name IS the file path
        fields = [
            ("message",        "",                              spec.message.encode()),
            ("branch",         "",                              push_branch.encode()),
            (info.file_path,   os.path.basename(info.file_path), new_content),
        ]
        url = f"https://api.bitbucket.org/2.0/repositories/{info.owner}/{info.repo}/src"
        _http_multipart(url, h, fields, method="POST")

    # ── Bitbucket Server / Data Center ────────────────────────────────────────
    elif info.platform == "bitbucket_server":
        if spec.push_mode == "new_branch" and spec.new_branch:
            branch_url = (f"{info.base_url}/rest/api/1.0/projects/{info.owner}"
                          f"/repos/{info.repo}/branches")
            _http_json(branch_url, h, {
                "name":       spec.new_branch,
                "startPoint": f"refs/heads/{info.branch}",
            })

        url = (f"{info.base_url}/rest/api/1.0/projects/{info.owner}"
               f"/repos/{info.repo}/browse/{info.file_path}")
        fields = [
            ("content",  "file",  new_content),
            ("message",  "",      spec.message.encode()),
            ("branch",   "",      push_branch.encode()),
        ]
        if info.file_sha:
            fields.append(("sourceCommitId", "", info.file_sha.encode()))
        _http_multipart(url, h, fields, method="PUT")

    else:
        raise ValueError(f"Unknown platform: {info.platform!r}")


# ── Progress stream ───────────────────────────────────────────────────────────

class _ProgressStream(io.RawIOBase):
    """File-like object that forwards dulwich progress lines to a callback."""

    def __init__(self, callback) -> None:
        self._cb  = callback
        self._buf = b""

    def write(self, data) -> int:  # type: ignore[override]
        if isinstance(data, str):
            data = data.encode("utf-8", errors="replace")
        self._buf += data
        while b"\n" in self._buf:
            line, self._buf = self._buf.split(b"\n", 1)
            text = line.decode("utf-8", errors="replace").strip()
            if text and self._cb:
                self._cb(0, text)
        return len(data)

    def flush(self) -> None:
        if self._buf.strip() and self._cb:
            self._cb(0, self._buf.decode("utf-8", errors="replace").strip())
        self._buf = b""


# ── SSH vendor (paramiko) ─────────────────────────────────────────────────────

def _make_paramiko_vendor(key_path: str, passphrase: str):
    """Return a dulwich ParamikoSSHVendor configured with *key_path*.

    Returns None if paramiko is not installed (dulwich falls back to
    the system ssh client in that case).
    """
    try:
        import paramiko  # noqa: F401
        from dulwich.contrib.paramiko_vendor import ParamikoSSHVendor

        class _KeyedVendor(ParamikoSSHVendor):
            def run_command(self, host, command, username=None, port=None,
                            password=None, key_filename=None, **kwargs):
                return super().run_command(
                    host, command,
                    username=username,
                    port=port,
                    password=passphrase or None,
                    key_filename=key_path or None,
                    **kwargs,
                )

        return _KeyedVendor()
    except ImportError:
        return None


# ── Clone ─────────────────────────────────────────────────────────────────────

def clone_repo(info: GitFileInfo, settings, progress_cb) -> str:
    """Fetch the repository file into a fresh temp directory.

    HTTPS: downloads just the target file via the platform REST API —
    no dulwich HTTP transport involved, so Windows TLS/proxy issues are avoided.

    SSH: full clone via dulwich + optional paramiko (no git executable needed).

    Returns the temp directory path on success; cleans up and re-raises on error.
    """
    auth_method = settings.value("git/auth_method", "https")

    if auth_method != "ssh":
        return _clone_via_api(info, settings, progress_cb)

    # ── SSH path (dulwich) ────────────────────────────────────────────────────
    from dulwich import porcelain

    tmpdir    = tempfile.mkdtemp(prefix="markforge_git_")
    errstream = _ProgressStream(progress_cb)

    try:
        key_path   = settings.value("git/ssh_key_path",   "")
        passphrase = settings.value("git/ssh_passphrase", "")
        clone_url  = _ssh_clone_url(info)

        vendor = _make_paramiko_vendor(key_path, passphrase)
        if vendor is not None:
            import dulwich.client as _dc
            _orig = _dc.get_ssh_vendor
            _dc.get_ssh_vendor = lambda: vendor
            try:
                porcelain.clone(clone_url, tmpdir,
                                branch=info.branch.encode(),
                                errstream=errstream)
            finally:
                _dc.get_ssh_vendor = _orig
        else:
            porcelain.clone(clone_url, tmpdir,
                            branch=info.branch.encode(),
                            errstream=errstream)

        return tmpdir

    except Exception:
        shutil.rmtree(tmpdir, ignore_errors=True)
        raise


def _clone_via_api(info: GitFileInfo, settings, progress_cb) -> str:
    """Download just the target file via the platform REST API."""
    progress_cb(20, "Downloading file …")
    content, sha = _download_file(info, settings)
    info.file_sha = sha

    tmpdir = tempfile.mkdtemp(prefix="markforge_git_")
    try:
        local_path = os.path.join(tmpdir, *info.file_path.split("/"))
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(content)
        progress_cb(100, "File downloaded.")
        return tmpdir
    except Exception:
        shutil.rmtree(tmpdir, ignore_errors=True)
        raise


# ── Commit & push ─────────────────────────────────────────────────────────────

def commit_and_push(info: GitFileInfo, spec: CommitSpec, settings, progress_cb) -> None:
    """Stage info.file_path, commit, optionally switch branch, and push.

    HTTPS: uses the platform REST API — no dulwich HTTP transport.
    SSH:   uses dulwich + optional paramiko.
    """
    auth_method = settings.value("git/auth_method", "https")

    if auth_method != "ssh":
        _push_via_api(info, spec, settings, progress_cb)
        if spec.create_pr:
            _create_pull_request(info, spec, settings)
        return

    # ── SSH path (dulwich) ────────────────────────────────────────────────────
    from dulwich import porcelain
    from dulwich.repo import Repo

    repo_path = info.local_repo_path
    errstream = _ProgressStream(progress_cb)

    porcelain.add(repo_path, paths=[info.file_path])
    author = _git_author(repo_path)
    porcelain.commit(repo_path,
                     message=spec.message.encode("utf-8"),
                     author=author,
                     committer=author)

    push_branch = info.branch
    if spec.push_mode == "new_branch" and spec.new_branch:
        with Repo(repo_path) as repo:
            head_sha = repo.head()
            new_ref  = b"refs/heads/" + spec.new_branch.encode()
            repo.refs[new_ref] = head_sha
            repo.refs.set_symbolic_ref(b"HEAD", new_ref)
        push_branch = spec.new_branch

    refspec    = f"refs/heads/{push_branch}:refs/heads/{push_branch}".encode()
    key_path   = settings.value("git/ssh_key_path",   "")
    passphrase = settings.value("git/ssh_passphrase", "")
    push_url   = _ssh_clone_url(info)

    vendor = _make_paramiko_vendor(key_path, passphrase)
    if vendor is not None:
        import dulwich.client as _dc
        _orig = _dc.get_ssh_vendor
        _dc.get_ssh_vendor = lambda: vendor
        try:
            porcelain.push(repo_path, remote_location=push_url,
                           refspecs=[refspec], errstream=errstream)
        finally:
            _dc.get_ssh_vendor = _orig
    else:
        porcelain.push(repo_path, remote_location=push_url,
                       refspecs=[refspec], errstream=errstream)

    if spec.create_pr:
        _create_pull_request(info, spec, settings)


def _push_via_api(info: GitFileInfo, spec: CommitSpec, settings, progress_cb) -> None:
    progress_cb(20, "Pushing changes …")
    with open(info.local_file_path, "rb") as f:
        new_content = f.read()
    _upload_file(info, spec, settings, new_content)
    progress_cb(100, "Done.")


def _git_author(repo_path: str) -> bytes:
    """Read name/email from the repo's git config; fall back to a safe default."""
    try:
        from dulwich.config import StackedConfig
        cfg   = StackedConfig.default()
        name  = cfg.get(b"user", b"name")
        email = cfg.get(b"user", b"email")
        return f"{name.decode()} <{email.decode()}>".encode()
    except Exception:
        return b"MarkForge <markforge@local>"


# ── Pull request creation ─────────────────────────────────────────────────────

def _create_pull_request(info: GitFileInfo, spec: CommitSpec, settings) -> None:
    """Create a PR on GitHub, GitHub Enterprise, Bitbucket Cloud, or Bitbucket Server."""
    user  = settings.value("git/https_username", "")
    token = settings.value("git/https_token",    "")

    head_branch   = spec.new_branch or info.branch
    target_branch = spec.pr_target  or info.branch

    if info.platform == "github":
        api_url = f"https://api.github.com/repos/{info.owner}/{info.repo}/pulls"
        payload = json.dumps({
            "title": spec.pr_title,
            "head":  head_branch,
            "base":  target_branch,
            "body":  "",
        }).encode()
        req = urllib.request.Request(
            api_url, data=payload,
            headers={
                "Authorization": f"token {token}",
                "Accept":        "application/vnd.github+json",
                "Content-Type":  "application/json",
                "User-Agent":    "MarkForge",
            },
            method="POST",
        )

    elif info.platform == "github_enterprise":
        api_url = f"{info.base_url}/api/v3/repos/{info.owner}/{info.repo}/pulls"
        payload = json.dumps({
            "title": spec.pr_title,
            "head":  head_branch,
            "base":  target_branch,
            "body":  "",
        }).encode()
        req = urllib.request.Request(
            api_url, data=payload,
            headers={
                "Authorization": f"token {token}",
                "Accept":        "application/vnd.github+json",
                "Content-Type":  "application/json",
                "User-Agent":    "MarkForge",
            },
            method="POST",
        )

    elif info.platform == "bitbucket":
        api_url = (
            f"https://api.bitbucket.org/2.0/repositories/"
            f"{info.owner}/{info.repo}/pullrequests"
        )
        payload = json.dumps({
            "title": spec.pr_title,
            "source":      {"branch": {"name": head_branch}},
            "destination": {"branch": {"name": target_branch}},
        }).encode()
        credentials = base64.b64encode(f"{user}:{token}".encode()).decode()
        req = urllib.request.Request(
            api_url, data=payload,
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type":  "application/json",
                "User-Agent":    "MarkForge",
            },
            method="POST",
        )

    elif info.platform == "bitbucket_server":
        api_url = (
            f"{info.base_url}/rest/api/1.0"
            f"/projects/{info.owner}/repos/{info.repo}/pull-requests"
        )
        payload = json.dumps({
            "title":   spec.pr_title,
            "fromRef": {"id": f"refs/heads/{head_branch}"},
            "toRef":   {"id": f"refs/heads/{target_branch}"},
        }).encode()
        credentials = base64.b64encode(f"{user}:{token}".encode()).decode()
        req = urllib.request.Request(
            api_url, data=payload,
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type":  "application/json",
                "User-Agent":    "MarkForge",
            },
            method="POST",
        )

    else:
        raise ValueError(f"Unknown platform: {info.platform!r}")

    try:
        with urllib.request.urlopen(req) as resp:
            resp.read()
    except urllib.error.HTTPError as exc:
        if exc.code == 401:
            raise RuntimeError("Authentication failed (HTTP 401). Check your token.") from exc
        raise RuntimeError(f"PR creation failed (HTTP {exc.code}): {exc.reason}") from exc
