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

from credentials import get_secret


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
class CommitInfo:
    sha:     str   # full SHA
    message: str   # first line
    author:  str
    date:    str   # human-readable


@dataclass
class CommitSpec:
    message:    str
    push_mode:  str        # "current_branch" | "new_branch"
    new_branch: str  = ""
    create_pr:  bool = False
    pr_title:   str  = ""
    pr_target:  str  = ""
    amend:      bool = False   # amend the previous MarkForge commit (SSH only)


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
    token = get_secret("git/https_token")
    headers: dict[str, str] = {"User-Agent": "MarkForge", "Accept": "application/json"}
    if user and token:
        if platform in ("github", "github_enterprise"):
            headers["Authorization"] = f"token {token}"
        else:
            creds = base64.b64encode(f"{user}:{token}".encode()).decode()
            headers["Authorization"] = f"Basic {creds}"
    return headers


def _apply_proxy(settings) -> None:
    """Install a urllib opener with the configured proxy (if any).

    If a proxy URL is set in settings, that proxy is used for all subsequent
    urllib.request.urlopen() calls in this process.  If a username is also
    provided, ProxyBasicAuthHandler supplies the credentials automatically.

    If no proxy URL is configured, the system's default proxy settings are
    used (Windows registry / environment variables).
    """
    proxy_url  = (settings.value("proxy/url",      "") or "").strip()
    proxy_user = (settings.value("proxy/username", "") or "").strip()
    proxy_pass = get_secret("proxy/password").strip()

    if not proxy_url:
        return   # keep default urllib behaviour (reads system/env proxies)

    handlers: list = [urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})]

    if proxy_user:
        pwd_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        pwd_mgr.add_password(None, proxy_url, proxy_user, proxy_pass)
        handlers.append(urllib.request.ProxyBasicAuthHandler(pwd_mgr))

    urllib.request.install_opener(urllib.request.build_opener(*handlers))


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
    except urllib.error.URLError as exc:
        _raise_network_error(url, exc)


def _raise_network_error(url: str, exc: urllib.error.URLError) -> None:
    """Convert urllib network errors into human-readable messages."""
    import socket
    from urllib.parse import urlparse
    host = urlparse(url).hostname or url
    reason = exc.reason
    if isinstance(reason, socket.gaierror):
        raise RuntimeError(
            f"Could not resolve host '{host}'.\n"
            "Check that you are connected to the correct network or VPN."
        )
    if isinstance(reason, TimeoutError) or "timed out" in str(reason).lower():
        raise RuntimeError(
            f"Connection to '{host}' timed out.\n"
            "Check your network connection and that the server is reachable."
        )
    raise RuntimeError(f"Network error: {reason}")


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
    except urllib.error.URLError as exc:
        _raise_network_error(url, exc)


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
    except urllib.error.URLError as exc:
        _raise_network_error(url, exc)


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

    HTTPS (API):    downloads just the target file via the platform REST API.
    HTTPS (git):    full clone via the system git binary.
    SSH (dulwich):  full clone via dulwich + optional paramiko.

    Returns the temp directory path on success; cleans up and re-raises on error.
    """
    auth_method = settings.value("git/auth_method", "https")

    if auth_method == "git":
        return _clone_via_git_binary(info, settings, progress_cb)

    if auth_method != "ssh":
        return _clone_via_api(info, settings, progress_cb)

    # ── SSH path (dulwich) ────────────────────────────────────────────────────
    from dulwich import porcelain

    tmpdir    = tempfile.mkdtemp(prefix="markforge_git_")
    errstream = _ProgressStream(progress_cb)

    try:
        key_path   = settings.value("git/ssh_key_path", "")
        passphrase = get_secret("git/ssh_passphrase")
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
    _apply_proxy(settings)
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


# ── Git binary helpers ────────────────────────────────────────────────────────

def _git_env(settings) -> dict:
    """Build the subprocess environment for git commands.

    Forwards the proxy configured in MarkForge settings via the standard
    http_proxy / https_proxy environment variables that git respects.
    If no proxy is configured, the system environment is passed through
    unchanged (so git uses whatever proxy the OS or git config provides).
    GIT_TERMINAL_PROMPT is always disabled to prevent hanging on auth prompts.
    """
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    proxy_url  = (settings.value("proxy/url",      "") or "").strip()
    proxy_user = (settings.value("proxy/username", "") or "").strip()
    proxy_pass = get_secret("proxy/password").strip()
    if proxy_url:
        if proxy_user:
            scheme, rest = proxy_url.split("://", 1)
            proxy_url = f"{scheme}://{proxy_user}:{proxy_pass}@{rest}"
        env["http_proxy"]  = proxy_url
        env["https_proxy"] = proxy_url
        env["HTTP_PROXY"]  = proxy_url   # some git builds read uppercase
        env["HTTPS_PROXY"] = proxy_url
    return env


def _clone_via_git_binary(info: GitFileInfo, settings, progress_cb) -> str:
    """Full clone via the system git binary over HTTPS."""
    import subprocess

    user  = settings.value("git/https_username", "")
    token = get_secret("git/https_token")
    clone_url = _build_https_clone_url(info.clone_url, user, token)
    env = _git_env(settings)

    tmpdir = tempfile.mkdtemp(prefix="markforge_git_")
    try:
        progress_cb(10, "Cloning repository …")
        result = subprocess.run(
            ["git", "clone", "--branch", info.branch,
             "--single-branch", "--depth", "1", clone_url, tmpdir],
            env=env, capture_output=True, text=True,
        )
        if result.returncode != 0:
            err = result.stderr.strip()
            if user and token:
                err = err.replace(f"{user}:{token}@", "")
            raise RuntimeError(f"git clone failed:\n{err}")
        progress_cb(100, "Repository cloned.")
        return tmpdir
    except FileNotFoundError:
        shutil.rmtree(tmpdir, ignore_errors=True)
        raise RuntimeError(
            "git executable not found.\nPlease install Git and make sure it is on PATH."
        )
    except Exception:
        shutil.rmtree(tmpdir, ignore_errors=True)
        raise


def _push_via_git_binary(info: GitFileInfo, spec: CommitSpec,
                         settings, progress_cb) -> None:
    """Stage, commit (optionally amend), and push via the system git binary."""
    import subprocess

    user  = settings.value("git/https_username", "")
    token = get_secret("git/https_token")
    name  = (settings.value("git/user_name",  "") or "").strip()
    email = (settings.value("git/user_email", "") or "").strip()
    repo_path = info.local_repo_path
    env = _git_env(settings)

    def _run(*cmd, step_msg: str) -> None:
        progress_cb(0, step_msg)
        result = subprocess.run(list(cmd), cwd=repo_path, env=env,
                                capture_output=True, text=True)
        if result.returncode != 0:
            err = (result.stderr or result.stdout).strip()
            if user and token:
                err = err.replace(f"{user}:{token}@", "")
            raise RuntimeError(f"{cmd[0]} {cmd[1]} failed:\n{err}")

    # Build identity flags for git commit (-c user.name=… -c user.email=…)
    identity: list[str] = []
    if name:
        identity += ["-c", f"user.name={name}"]
    if email:
        identity += ["-c", f"user.email={email}"]

    _run("git", "add", info.file_path, step_msg="Staging …")

    if spec.amend:
        _run("git", *identity, "commit", "--amend", "-m", spec.message,
             step_msg="Amending commit …")
    else:
        _run("git", *identity, "commit", "-m", spec.message,
             step_msg="Committing …")

    if spec.amend:
        _run("git", "push", "--force-with-lease", step_msg="Force-pushing …")
    elif spec.push_mode == "new_branch" and spec.new_branch:
        _run("git", "push", "origin",
             f"HEAD:refs/heads/{spec.new_branch}",
             step_msg="Pushing new branch …")
    else:
        _run("git", "push", step_msg="Pushing …")

    if spec.create_pr:
        _create_pull_request(info, spec, settings)

    progress_cb(100, "Done.")


# ── Branch commit listing & squash ────────────────────────────────────────────

def get_branch_commits(info: GitFileInfo, settings,
                        base_branch: str = "main") -> list[CommitInfo]:
    """Return commits on HEAD that are not in *base_branch*, newest first.

    Compares HEAD against origin/<base_branch> so that commits which were
    already on the feature branch before cloning are included.

    Works for both the git-binary and SSH/dulwich auth paths.
    Returns an empty list for the HTTPS-API path (no local repo).
    """
    auth_method = settings.value("git/auth_method", "https")

    if auth_method == "git":
        return _branch_commits_git(info, settings, base_branch)
    if auth_method == "ssh":
        return _branch_commits_ssh(info, base_branch)
    return []


def _branch_commits_git(info: GitFileInfo, settings,
                         base_branch: str) -> list[CommitInfo]:
    import subprocess
    from datetime import datetime

    env       = _git_env(settings)
    repo_path = info.local_repo_path

    # Fetch the base-branch tip so origin/<base_branch> exists locally.
    # Errors are silently ignored (e.g. branch does not exist on remote).
    subprocess.run(
        ["git", "fetch", "origin", f"{base_branch}:refs/remotes/origin/{base_branch}",
         "--depth=1", "--no-tags"],
        cwd=repo_path, env=env, capture_output=True, text=True,
    )
    # Deepen the current branch so the divergence point is reachable.
    subprocess.run(
        ["git", "fetch", "--deepen=100", "--no-tags"],
        cwd=repo_path, env=env, capture_output=True, text=True,
    )

    fmt    = "%H%x09%s%x09%an%x09%ci"
    result = subprocess.run(
        ["git", "log", f"--format={fmt}",
         f"origin/{base_branch}..HEAD"],
        cwd=repo_path, env=env, capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or
                           f"'origin/{base_branch}' not found – "
                           "check the base branch name.")

    commits: list[CommitInfo] = []
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        sha, msg, author, raw_date = parts[0], parts[1], parts[2], parts[3]
        try:
            dt   = datetime.fromisoformat(raw_date.strip())
            date = dt.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            date = raw_date.strip()
        commits.append(CommitInfo(sha=sha, message=msg, author=author, date=date))
    return commits


def _branch_commits_ssh(info: GitFileInfo, base_branch: str) -> list[CommitInfo]:
    from datetime import datetime, timezone
    from dulwich.repo import Repo

    commits: list[CommitInfo] = []
    with Repo(info.local_repo_path) as repo:
        # Prefer base branch ref; fall back to current branch's remote ref
        for ref_candidate in (
            b"refs/remotes/origin/" + base_branch.encode(),
            b"refs/remotes/origin/" + info.branch.encode(),
        ):
            try:
                exclude_sha = repo.refs[ref_candidate]
                exclude     = [exclude_sha]
                break
            except KeyError:
                continue
        else:
            exclude = []

        for entry in repo.get_walker(include=[repo.head()], exclude=exclude):
            c   = entry.commit
            msg = c.message.decode("utf-8", errors="replace").splitlines()[0].strip()
            author = c.author.decode("utf-8", errors="replace")
            dt     = datetime.fromtimestamp(c.commit_time, tz=timezone.utc)
            date   = dt.strftime("%Y-%m-%d %H:%M")
            commits.append(CommitInfo(
                sha     = c.id.decode("ascii"),
                message = msg,
                author  = author,
                date    = date,
            ))
    return commits


def squash_and_push(info: GitFileInfo, squash_count: int,
                    message: str, settings, progress_cb) -> None:
    """Squash the top *squash_count* commits into one and force-push.

    The squash target is always HEAD~squash_count (contiguous from HEAD).
    Works for both the git-binary and SSH/dulwich auth paths.
    """
    auth_method = settings.value("git/auth_method", "https")
    if auth_method == "git":
        _squash_via_git_binary(info, squash_count, message, settings, progress_cb)
    elif auth_method == "ssh":
        _squash_via_ssh(info, squash_count, message, settings, progress_cb)
    else:
        raise RuntimeError("Squash is only supported for SSH and git-binary auth methods.")


def _squash_via_git_binary(info: GitFileInfo, squash_count: int,
                            message: str, settings, progress_cb) -> None:
    import subprocess

    user  = settings.value("git/https_username", "")
    token = get_secret("git/https_token")
    name  = (settings.value("git/user_name",  "") or "").strip()
    email = (settings.value("git/user_email", "") or "").strip()

    repo_path = info.local_repo_path
    env       = _git_env(settings)
    identity: list[str] = []
    if name:  identity += ["-c", f"user.name={name}"]
    if email: identity += ["-c", f"user.email={email}"]

    def _run(*cmd, step_msg: str) -> None:
        progress_cb(0, step_msg)
        result = subprocess.run(list(cmd), cwd=repo_path, env=env,
                                capture_output=True, text=True)
        if result.returncode != 0:
            err = (result.stderr or result.stdout).strip()
            if user and token:
                err = err.replace(f"{user}:{token}@", "")
            raise RuntimeError(f"{cmd[1]} failed:\n{err}")

    _run("git", "reset", "--soft", f"HEAD~{squash_count}",
         step_msg="Squashing commits …")
    _run("git", *identity, "commit", "-m", message,
         step_msg="Creating squash commit …")
    _run("git", "push", "--force-with-lease",
         step_msg="Force-pushing …")
    progress_cb(100, "Done.")


def _squash_via_ssh(info: GitFileInfo, squash_count: int,
                    message: str, settings, progress_cb) -> None:
    from dulwich import porcelain
    from dulwich.objects import Commit as _Commit
    from dulwich.repo import Repo
    from time import time as _time

    repo_path = info.local_repo_path
    author    = _git_author(repo_path)

    progress_cb(20, "Squashing commits …")
    with Repo(repo_path) as repo:
        # Walk back squash_count steps to find the target parent
        head_sha   = repo.head()
        head_obj   = repo.get_object(head_sha)
        target_parent = head_sha
        current       = head_obj
        for _ in range(squash_count):
            if not current.parents:
                break
            target_parent = current.parents[0]
            current       = repo.get_object(target_parent)

        now = int(_time())
        c = _Commit()
        c.tree            = head_obj.tree   # keep final working-tree state
        c.author          = author
        c.committer       = author
        c.author_time     = now
        c.commit_time     = now
        c.author_timezone = 0
        c.commit_timezone = 0
        c.encoding        = b"UTF-8"
        msg = message.encode("utf-8")
        c.message         = msg if msg.endswith(b"\n") else msg + b"\n"
        c.parents         = [target_parent]

        repo.object_store.add_object(c)
        branch_ref = b"refs/heads/" + info.branch.encode()
        repo.refs[branch_ref] = c.id

    progress_cb(60, "Force-pushing …")
    errstream  = _ProgressStream(progress_cb)
    key_path   = settings.value("git/ssh_key_path", "")
    passphrase = get_secret("git/ssh_passphrase")
    push_url   = _ssh_clone_url(info)
    refspec    = f"+refs/heads/{info.branch}:refs/heads/{info.branch}".encode()

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
    progress_cb(100, "Done.")


# ── Commit & push ─────────────────────────────────────────────────────────────

def commit_and_push(info: GitFileInfo, spec: CommitSpec, settings, progress_cb) -> None:
    """Stage info.file_path, commit, optionally switch branch, and push.

    HTTPS: uses the platform REST API — no dulwich HTTP transport.
    SSH:   uses dulwich + optional paramiko.
    """
    auth_method = settings.value("git/auth_method", "https")

    if auth_method == "git":
        _push_via_git_binary(info, spec, settings, progress_cb)
        return

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
    author    = _git_author(repo_path)

    if spec.amend:
        # Amend the previous MarkForge commit: replace it with a new commit
        # that has the same parents, so history stays linear.
        from dulwich.objects import Commit as _Commit
        from time import time as _time

        porcelain.add(repo_path, paths=[info.file_path])
        with Repo(repo_path) as _repo:
            old_commit = _repo.get_object(_repo.head())
            index      = _repo.open_index()
            tree_sha   = index.commit(_repo.object_store)

            now = int(_time())
            c = _Commit()
            c.tree             = tree_sha
            c.author           = author
            c.committer        = author
            c.author_time      = now
            c.commit_time      = now
            c.author_timezone  = 0
            c.commit_timezone  = 0
            c.encoding         = b"UTF-8"
            msg = spec.message.encode("utf-8")
            c.message          = msg if msg.endswith(b"\n") else msg + b"\n"
            c.parents          = old_commit.parents  # skip the amended commit

            _repo.object_store.add_object(c)
            branch_ref = b"refs/heads/" + info.branch.encode()
            _repo.refs[branch_ref] = c.id
    else:
        porcelain.add(repo_path, paths=[info.file_path])
        porcelain.commit(repo_path,
                         message=spec.message.encode("utf-8"),
                         author=author,
                         committer=author)

    push_branch = info.branch
    if not spec.amend and spec.push_mode == "new_branch" and spec.new_branch:
        with Repo(repo_path) as repo:
            head_sha = repo.head()
            new_ref  = b"refs/heads/" + spec.new_branch.encode()
            repo.refs[new_ref] = head_sha
            repo.refs.set_symbolic_ref(b"HEAD", new_ref)
        push_branch = spec.new_branch

    # Use '+' prefix for force-push when amending (rewrites remote history)
    force_prefix = "+" if spec.amend else ""
    refspec    = f"{force_prefix}refs/heads/{push_branch}:refs/heads/{push_branch}".encode()
    key_path   = settings.value("git/ssh_key_path", "")
    passphrase = get_secret("git/ssh_passphrase")
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
    _apply_proxy(settings)
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
    token = get_secret("git/https_token")

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
