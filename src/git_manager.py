"""Git integration logic for MarkForge – no Qt imports."""

from __future__ import annotations

import base64
import os
import shutil
import sys
import tempfile
import urllib.request
import urllib.error
import json
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs


# ── Git executable discovery ───────────────────────────────────────────────────

# Candidate paths searched on Windows when git is not in PATH
_WINDOWS_GIT_CANDIDATES = [
    r"C:\Program Files\Git\cmd\git.exe",
    r"C:\Program Files\Git\bin\git.exe",
    r"C:\Program Files (x86)\Git\cmd\git.exe",
    r"C:\Program Files (x86)\Git\bin\git.exe",
]

def _ensure_git() -> None:
    """Make sure GitPython can find the git executable.

    On Windows git.exe is often only on the Git-internal PATH and not visible
    to processes launched from a GUI.  We probe well-known install locations
    as a fallback and call git.refresh() so all subsequent calls succeed.
    """
    import git as gitpython

    try:
        gitpython.refresh()
        return  # already works
    except gitpython.exc.InvalidGitRepositoryError:
        return  # refresh() raised for a different reason; git itself is fine
    except Exception:
        pass  # git not found in PATH – fall through to manual search

    if sys.platform != "win32":
        raise RuntimeError(
            "git executable not found. Make sure git is installed and in your PATH."
        )

    # Search common Windows installation directories
    for candidate in _WINDOWS_GIT_CANDIDATES:
        if os.path.isfile(candidate):
            gitpython.refresh(candidate)
            return

    # Also check the user's local AppData (GitHub Desktop, scoop, etc.)
    local_app = os.environ.get("LOCALAPPDATA", "")
    extra = [
        os.path.join(local_app, "Programs", "Git", "cmd", "git.exe"),
        os.path.join(local_app, "Programs", "Git", "bin", "git.exe"),
    ]
    for candidate in extra:
        if os.path.isfile(candidate):
            gitpython.refresh(candidate)
            return

    raise RuntimeError(
        "git executable not found on this system.\n"
        "Please install Git for Windows (https://git-scm.com/) "
        "and make sure git.exe is in your PATH."
    )


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclass
class GitFileInfo:
    platform:        str   # "github" | "github_enterprise" | "bitbucket" | "bitbucket_server"
    owner:           str   # GitHub: owner login; Bitbucket Server: project key
    repo:            str
    branch:          str
    file_path:       str   # relative path inside repo
    clone_url:       str   # https clone URL (no credentials)
    base_url:        str   # scheme + host, e.g. "https://bitbucket.mycompany.com"
    local_repo_path: str = ""
    local_file_path: str = ""


@dataclass
class CommitSpec:
    message:   str
    push_mode: str        # "current_branch" | "new_branch"
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
    parsed = urlparse(url.strip())
    host   = parsed.hostname or ""
    scheme = parsed.scheme or "https"
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

        # Branch from ?at= query param; strip refs/heads/ prefix if present
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
        # Bitbucket Server SSH: ssh://git@host/scm/project/repo.git
        return f"ssh://git@{host}/scm/{info.owner.lower()}/{info.repo}.git"
    else:
        # GitHub / GHE / Bitbucket Cloud: git@host:owner/repo.git
        return f"git@{host}:{info.owner}/{info.repo}.git"


def build_auth_env(settings) -> dict:
    """Build the environment dict for git operations (SSH only; HTTPS uses URL auth)."""
    auth_method = settings.value("git/auth_method", "https")
    if auth_method != "ssh":
        return {}

    key_path   = settings.value("git/ssh_key_path",   "")
    passphrase = settings.value("git/ssh_passphrase", "")

    ssh_cmd = f'ssh -i "{key_path}" -o StrictHostKeyChecking=no'
    env = dict(os.environ)
    env["GIT_SSH_COMMAND"] = ssh_cmd

    if passphrase:
        # Write a tiny askpass script so git can supply the passphrase
        askpass = tempfile.NamedTemporaryFile(
            mode="w", suffix=".sh", delete=False, prefix="markforge_askpass_"
        )
        askpass.write(f'#!/bin/sh\necho "{passphrase}"\n')
        askpass.flush()
        os.chmod(askpass.name, 0o700)
        env["SSH_ASKPASS"]         = askpass.name
        env["SSH_ASKPASS_REQUIRE"] = "force"

    return env


# ── Progress helper ───────────────────────────────────────────────────────────

class _GitProgress:
    """Adapter from GitPython's RemoteProgress to a simple callback."""

    def __init__(self, callback):
        self._cb = callback

    def __call__(self, op_code, cur_count, max_count=None, message=""):
        if self._cb is None:
            return
        pct = int(cur_count / max_count * 100) if max_count else 0
        self._cb(pct, message or "")

    def update(self, op_code, cur_count, max_count=None, message=""):
        self.__call__(op_code, cur_count, max_count, message)


# ── Clone ─────────────────────────────────────────────────────────────────────

def clone_repo(info: GitFileInfo, settings, progress_cb) -> str:
    """Clone *info.clone_url* into a temporary directory.

    Returns the path to the temp directory on success.
    Raises on any error (and cleans up the temp dir).
    """
    _ensure_git()
    import git as gitpython

    tmpdir = tempfile.mkdtemp(prefix="markforge_git_")
    try:
        auth_method = settings.value("git/auth_method", "https")

        if auth_method == "ssh":
            clone_url = _ssh_clone_url(info)
            env       = build_auth_env(settings)
            gitpython.Repo.clone_from(
                clone_url,
                tmpdir,
                branch=info.branch,
                single_branch=True,
                depth=1,
                env=env,
                progress=_GitProgress(progress_cb),
            )
        else:
            user  = settings.value("git/https_username", "")
            token = settings.value("git/https_token",    "")
            clone_url = (
                _build_https_clone_url(info.clone_url, user, token)
                if user and token
                else info.clone_url   # public repo – no credentials
            )
            gitpython.Repo.clone_from(
                clone_url,
                tmpdir,
                branch=info.branch,
                single_branch=True,
                depth=1,
                progress=_GitProgress(progress_cb),
            )

        return tmpdir

    except Exception:
        shutil.rmtree(tmpdir, ignore_errors=True)
        raise


# ── Commit & push ─────────────────────────────────────────────────────────────

def commit_and_push(info: GitFileInfo, spec: CommitSpec, settings, progress_cb) -> None:
    """Stage info.file_path, commit, optionally switch branch, and push."""
    _ensure_git()
    import git as gitpython

    repo   = gitpython.Repo(info.local_repo_path)
    origin = repo.remotes.origin

    repo.index.add([info.file_path])
    repo.index.commit(spec.message)

    push_branch = info.branch
    if spec.push_mode == "new_branch" and spec.new_branch:
        repo.create_head(spec.new_branch).checkout()
        push_branch = spec.new_branch

    auth_method = settings.value("git/auth_method", "https")
    env = {}
    if auth_method == "ssh":
        env = build_auth_env(settings)
    else:
        user  = settings.value("git/https_username", "")
        token = settings.value("git/https_token",    "")
        if user and token:
            with origin.config_writer as cw:
                cw.set("url", _build_https_clone_url(info.clone_url, user, token))

    class _PushProgress:
        def __call__(self, op_code, cur_count, max_count=None, message=""):
            if progress_cb and max_count and max_count > 0:
                progress_cb(int(cur_count / max_count * 100), message or "")
        def update(self, op_code, cur_count, max_count=None, message=""):
            self.__call__(op_code, cur_count, max_count, message)

    push_info = origin.push(
        refspec=f"{push_branch}:{push_branch}",
        progress=_PushProgress(),
        **( {"env": env} if env else {} ),
    )

    for pi in push_info:
        import git as _g
        if pi.flags & _g.PushInfo.ERROR:
            raise RuntimeError(f"Push rejected: {pi.summary.strip()}")

    if spec.create_pr:
        _create_pull_request(info, spec, settings)


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
        # GitHub Enterprise Server REST API lives at /api/v3/
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
        # Bitbucket Server / Data Center REST API 1.0
        api_url = (
            f"{info.base_url}/rest/api/1.0"
            f"/projects/{info.owner}/repos/{info.repo}/pull-requests"
        )
        payload = json.dumps({
            "title": spec.pr_title,
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
