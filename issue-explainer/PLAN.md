# Plan: issue-explainer

Approve this, then implement in this order.

## What we will build
A beginner helper that takes a GitHub issue (`owner`, `repo`, `number`) and a `friend.json` skill profile, then asks a **local Ollama** model to explain the issue in plain language. No cloud LLM APIs.

## Files
| File | Role |
|------|------|
| `explain.py` | All logic in `explain(owner, repo, number, model)` + CLI (`--model`, default `gemma3:4b`) |
| `app.py` | Streamlit: issue URL, model dropdown, Explain, sidebar friend, markdown result, hallucinated-file warning, elapsed time |
| `compare.py` | Run three models, write `comparison_<repo>_<number>.md` |
| `friend.json` | Name, skills, fear |
| `requirements.txt` | `requests`, `ollama`, `streamlit` |
| `README.md` | Setup, usage, why open-source / local AI |

## Flow of `explain()`
1. GitHub REST: issue + first 5 comments (token from `GITHUB_TOKEN` if set).
2. Default branch + recursive file tree; paths only, truncated to 4000 chars.
3. Load `friend.json`.
4. One Ollama prompt: Summary (3 lines), Type, Difficulty for this friend + why, Skills needed, Where to look (only listed files), First 3 steps, One maintainer question.
5. Plain-language errors: missing/blocked token, 404, Ollama down, rate limit.

## Implementation order
1. CLI + `friend.json` + `requirements.txt`
2. Test: `python explain.py ollama ollama 1`
3. Streamlit UI; browser walkthrough of one real issue
4. `compare.py` + markdown output
5. Confirm Ollama inference is local (works without Wi-Fi for the model step)

## Tests (short)
- CLI end-to-end on `ollama/ollama#1`
- UI loads and explains a real issue URL
- `compare.py` writes the markdown file
- Model call hits local Ollama, not a cloud API
