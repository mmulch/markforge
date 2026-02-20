"""Git integration logic for MarkForge – no Qt imports.

Uses *dulwich* (pure-Python git implementation) so no git executable is
required on the host system.  HTTPS auth embeds credentials in the URL;
SSH auth uses paramiko (pure Python) if installed, otherwise falls back
to the system ssh client.
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
from dataclasses import dataclass
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
    """Clone the repository into a fresh temp directory using dulwich.

    dulwich is a pure-Python git implementation — no git executable needed.
    Returns the temp directory path on success; cleans up and re-raises on error.
    """
    from dulwich import porcelain

    tmpdir = tempfile.mkdtemp(prefix="markforge_git_")
    errstream = _ProgressStream(progress_cb)

    try:
        auth_method = settings.value("git/auth_method", "https")

        if auth_method == "ssh":
            key_path   = settings.value("git/ssh_key_path",   "")
            passphrase = settings.value("git/ssh_passphrase", "")
            clone_url  = _ssh_clone_url(info)

            vendor = _make_paramiko_vendor(key_path, passphrase)
            if vendor is not None:
                # Pure-Python SSH via paramiko
                import dulwich.client as _dc
                _orig = _dc.get_ssh_vendor
                _dc.get_ssh_vendor = lambda: vendor
                try:
                    porcelain.clone(
                        clone_url, tmpdir,
                        branch=info.branch.encode(),
                        errstream=errstream,
                    )
                finally:
                    _dc.get_ssh_vendor = _orig
            else:
                # Fall back to system ssh client
                porcelain.clone(
                    clone_url, tmpdir,
                    branch=info.branch.encode(),
                    errstream=errstream,
                )
        else:
            user  = settings.value("git/https_username", "")
            token = settings.value("git/https_token",    "")
            clone_url = (
                _build_https_clone_url(info.clone_url, user, token)
                if user and token
                else info.clone_url
            )
            porcelain.clone(
                clone_url, tmpdir,
                branch=info.branch.encode(),
                errstream=errstream,
            )

        return tmpdir

    except Exception:
        shutil.rmtree(tmpdir, ignore_errors=True)
        raise


# ── Commit & push ─────────────────────────────────────────────────────────────

def commit_and_push(info: GitFileInfo, spec: CommitSpec, settings, progress_cb) -> None:
    """Stage info.file_path, commit, optionally switch branch, and push."""
    from dulwich import porcelain
    from dulwich.repo import Repo

    repo_path = info.local_repo_path
    errstream = _ProgressStream(progress_cb)

    # Stage the modified file (path is relative to repo root, forward slashes)
    porcelain.add(repo_path, paths=[info.file_path])

    # Build a commit author string; reuse whatever is in the repo's git config,
    # falling back to a neutral default so the commit always succeeds.
    author = _git_author(repo_path)
    porcelain.commit(
        repo_path,
        message=spec.message.encode("utf-8"),
        author=author,
        committer=author,
    )

    # Optionally create and switch to a new local branch
    push_branch = info.branch
    if spec.push_mode == "new_branch" and spec.new_branch:
        with Repo(repo_path) as repo:
            head_sha  = repo.head()
            new_ref   = b"refs/heads/" + spec.new_branch.encode()
            repo.refs[new_ref] = head_sha
            repo.refs.set_symbolic_ref(b"HEAD", new_ref)
        push_branch = spec.new_branch

    refspec   = f"refs/heads/{push_branch}:refs/heads/{push_branch}".encode()
    auth_method = settings.value("git/auth_method", "https")

    if auth_method == "ssh":
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
    else:
        user  = settings.value("git/https_username", "")
        token = settings.value("git/https_token",    "")
        push_url = (
            _build_https_clone_url(info.clone_url, user, token)
            if user and token
            else info.clone_url
        )
        porcelain.push(repo_path, remote_location=push_url,
                       refspecs=[refspec], errstream=errstream)

    if spec.create_pr:
        _create_pull_request(info, spec, settings)


def _git_author(repo_path: str) -> bytes:
    """Read name/email from the repo's git config; fall back to a safe default."""
    try:
        from dulwich.repo import Repo
        from dulwich.config import StackedConfig
        cfg = StackedConfig.default()
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
