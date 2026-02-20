"""Git integration logic for MarkForge – no Qt imports."""

from __future__ import annotations

import base64
import os
import shutil
import tempfile
import urllib.request
import urllib.error
import json
from dataclasses import dataclass, field
from urllib.parse import urlparse


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclass
class GitFileInfo:
    platform:        str   # "github" | "bitbucket"
    owner:           str
    repo:            str
    branch:          str
    file_path:       str   # relative path inside repo
    clone_url:       str   # https clone URL (no credentials)
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
    """Parse a GitHub or Bitbucket file URL into a GitFileInfo.

    Raises ValueError with a human-readable message on any problem.
    """
    parsed = urlparse(url.strip())
    host   = parsed.hostname or ""

    if "github.com" in host:
        platform  = "github"
        clone_fmt = "https://github.com/{owner}/{repo}.git"
    elif "bitbucket.org" in host:
        platform  = "bitbucket"
        clone_fmt = "https://bitbucket.org/{owner}/{repo}.git"
    else:
        raise ValueError(
            f"Unsupported host '{host}'. Only github.com and bitbucket.org are supported."
        )

    parts = [p for p in parsed.path.split("/") if p]
    # Expected path structures:
    #   GitHub:     /owner/repo/blob/branch/path/to/file.md
    #   Bitbucket:  /owner/repo/src/branch/path/to/file.md
    if len(parts) < 5:
        raise ValueError(
            "URL must point to a specific file, e.g. "
            "https://github.com/owner/repo/blob/main/README.md"
        )

    owner     = parts[0]
    repo      = parts[1]
    # parts[2] is "blob" (GitHub) or "src" (Bitbucket) — skip it
    branch    = parts[3]
    file_path = "/".join(parts[4:])

    if not file_path:
        raise ValueError("The URL does not point to a file (file path is empty).")

    clone_url = clone_fmt.format(owner=owner, repo=repo)

    return GitFileInfo(
        platform=platform,
        owner=owner,
        repo=repo,
        branch=branch,
        file_path=file_path,
        clone_url=clone_url,
    )


# ── Auth helpers ──────────────────────────────────────────────────────────────

def _build_https_clone_url(base: str, user: str, token: str) -> str:
    """Embed credentials into an HTTPS clone URL."""
    return base.replace("https://", f"https://{user}:{token}@", 1)


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
        env["SSH_ASKPASS"]       = askpass.name
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
        if max_count and max_count > 0:
            pct = int(cur_count / max_count * 100)
        else:
            pct = 0
        self._cb(pct, message or "")

    # GitPython calls update() on progress objects
    def update(self, op_code, cur_count, max_count=None, message=""):
        self.__call__(op_code, cur_count, max_count, message)


# ── Clone ─────────────────────────────────────────────────────────────────────

def clone_repo(info: GitFileInfo, settings, progress_cb) -> str:
    """Clone *info.clone_url* into a temporary directory.

    Returns the path to the temp directory on success.
    Raises on any error (and cleans up the temp dir).
    """
    import git as gitpython

    tmpdir = tempfile.mkdtemp(prefix="markforge_git_")
    try:
        auth_method = settings.value("git/auth_method", "https")

        if auth_method == "ssh":
            clone_url = info.clone_url.replace("https://github.com/", "git@github.com:", 1)
            clone_url = clone_url.replace("https://bitbucket.org/", "git@bitbucket.org:", 1)
            env = build_auth_env(settings)
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
            if user and token:
                clone_url = _build_https_clone_url(info.clone_url, user, token)
            else:
                clone_url = info.clone_url  # public repo – no credentials
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
    import git as gitpython

    repo   = gitpython.Repo(info.local_repo_path)
    origin = repo.remotes.origin

    # Stage the file
    repo.index.add([info.file_path])
    repo.index.commit(spec.message)

    # Optionally create and switch to a new branch
    push_branch = info.branch
    if spec.push_mode == "new_branch" and spec.new_branch:
        repo.create_head(spec.new_branch).checkout()
        push_branch = spec.new_branch

    # Fix remote URL for HTTPS auth
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

    # Check for push rejection
    for pi in push_info:
        import git as _g
        if pi.flags & _g.PushInfo.ERROR:
            raise RuntimeError(
                f"Push rejected: {pi.summary.strip()}"
            )

    if spec.create_pr:
        _create_pull_request(info, spec, settings)


# ── Pull request creation ─────────────────────────────────────────────────────

def _create_pull_request(info: GitFileInfo, spec: CommitSpec, settings) -> None:
    """Create a PR on GitHub or Bitbucket using only urllib."""
    user  = settings.value("git/https_username", "")
    token = settings.value("git/https_token",    "")

    head_branch   = spec.new_branch or info.branch
    target_branch = spec.pr_target  or info.branch

    if info.platform == "github":
        api_url = (
            f"https://api.github.com/repos/{info.owner}/{info.repo}/pulls"
        )
        payload = json.dumps({
            "title": spec.pr_title,
            "head":  head_branch,
            "base":  target_branch,
            "body":  "",
        }).encode()
        req = urllib.request.Request(
            api_url,
            data=payload,
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
            "source": {"branch": {"name": head_branch}},
            "destination": {"branch": {"name": target_branch}},
        }).encode()
        credentials = base64.b64encode(f"{user}:{token}".encode()).decode()
        req = urllib.request.Request(
            api_url,
            data=payload,
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
