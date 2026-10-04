"""Fetch a GitHub issue and explain it locally with Ollama."""
import argparse
import json
import os
import re
import sys
from pathlib import Path

import ollama
import requests

ROOT = Path(__file__).resolve().parent
API = "https://api.github.com"
DEFAULT_MODEL = "gemma3:4b"


def _headers():
    h = {"Accept": "application/vnd.github+json", "User-Agent": "issue-explainer"}
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def _get(url, params=None):
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    try:
        r = requests.get(url, headers=_headers(), params=params, timeout=30)
    except requests.RequestException as exc:
        return None, f"Could not reach GitHub ({exc}). Check your network."
    if r.status_code == 404:
        return None, "That issue or repository was not found (404). Check owner, repo, and number."
    if r.status_code == 403 and "rate limit" in r.text.lower():
        return None, "GitHub rate limit reached. Set a GITHUB_TOKEN environment variable and retry."
    if r.status_code in (401, 403) and not token:
        return None, "GitHub blocked the request. Set a GITHUB_TOKEN environment variable (do not hardcode it)."
    if r.status_code in (401, 403):
        return None, "GitHub rejected GITHUB_TOKEN. Check that the token is valid."
    if r.status_code >= 400:
        return None, f"GitHub error {r.status_code}."
    return r.json(), None


def repo_file_paths(owner, repo):
    data, err = _get(f"{API}/repos/{owner}/{repo}")
    if err:
        return "", err
    branch = data.get("default_branch", "main")
    tree, err = _get(f"{API}/repos/{owner}/{repo}/git/trees/{branch}", {"recursive": "1"})
    if err:
        return "", err
    paths = "\n".join(i["path"] for i in tree.get("tree", []) if i.get("type") == "blob")
    return paths[:4000], None


def load_friend():
    with (ROOT / "friend.json").open(encoding="utf-8") as f:
        return json.load(f)


def hallucinated_files(answer, tree_text):
    known = {p.strip() for p in tree_text.splitlines() if p.strip()}
    match = re.search(r"(?is)##?\s*Where to look\b.*?\n(.*?)(?=\n##?\s|\Z)", answer)
    chunk = match.group(1) if match else answer
    found = re.findall(r"`([^`]+)`|([A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+)", chunk)
    names = {a or b for a, b in found}
    return sorted(n.strip() for n in names if n.strip() and n.strip() not in known)


def explain(owner, repo, number, model):
    issue, err = _get(f"{API}/repos/{owner}/{repo}/issues/{number}")
    if err:
        return err
    comments, err = _get(
        f"{API}/repos/{owner}/{repo}/issues/{number}/comments", {"per_page": 5}
    )
    if err:
        return err
    tree, err = repo_file_paths(owner, repo)
    if err:
        return err
    friend = load_friend()
    comment_text = "\n".join(
        f"- {c.get('user', {}).get('login', '?')}: {(c.get('body') or '')[:800]}"
        for c in (comments or [])[:5]
    ) or "(no comments)"
    prompt = f"""You explain GitHub issues for a beginner friend. Use only facts below.

Friend: {friend.get('name')}
Skills: {', '.join(friend.get('skills') or [])}
Fear: {friend.get('fear')}

Issue #{number} in {owner}/{repo}: {issue.get('title')}
Body:
{(issue.get('body') or '')[:3500]}

Comments:
{comment_text}

Repo files (use ONLY these paths in Where to look; if unsure, say so):
{tree}

Reply in markdown with exactly these headings:
## Summary
(3 short lines)
## Type
## Difficulty
(for THIS friend and why)
## Skills needed
## Where to look
## First 3 steps
## One question to ask the maintainer
"""
    try:
        resp = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    except Exception as exc:
        text = str(exc).lower()
        if "connect" in text or "refused" in text or "10061" in text:
            return "Ollama does not appear to be running. Start Ollama and try again."
        return f"Ollama error: {exc}"
    return (resp.get("message") or {}).get("content") or str(resp)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Explain a GitHub issue for a friend")
    p.add_argument("owner")
    p.add_argument("repo")
    p.add_argument("number", type=int)
    p.add_argument("--model", default=DEFAULT_MODEL)
    args = p.parse_args()
    print(explain(args.owner, args.repo, args.number, args.model))
    return 0


if __name__ == "__main__":
    sys.exit(main())
