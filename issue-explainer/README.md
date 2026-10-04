# issue-explainer

Help a beginner understand a GitHub issue. You pass an issue; a **local** Ollama model writes a plain-language breakdown tailored to a friend’s skills in `friend.json`.

No paid or cloud LLM APIs. GitHub is used only to fetch the issue, comments, and file list.

## Setup

1. Install [Ollama](https://ollama.com) and pull at least the default model:

   ```text
   ollama pull gemma3:4b
   ```

   Optional models used by the UI and `compare.py`: `qwen2.5:3b`, `qwen2.5:7b`.

2. Create a virtualenv and install dependencies:

   ```text
   py -3 -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. (Recommended) Set a GitHub token so you are less likely to hit rate limits. **Never put the token in code.**

   ```text
   set GITHUB_TOKEN=ghp_your_token_here
   ```

   Public issues often work without a token. If GitHub returns 401/403, set `GITHUB_TOKEN`.

4. Edit `friend.json` (`name`, `skills`, `fear`) so difficulty advice matches your friend.

## Usage

CLI (default model `gemma3:4b`):

```text
python explain.py ollama ollama 1
python explain.py ollama ollama 1 --model qwen2.5:3b
```

Streamlit UI:

```text
streamlit run app.py
```

Paste a URL such as `https://github.com/ollama/ollama/issues/1`, pick a model, click **Explain**.

Compare three local models:

```text
python compare.py ollama ollama 1
```

Writes `comparison_<repo>_<number>.md` with times, full outputs, and a hallucinated-file check.

## Why open-source / local AI

The issue text never goes to a vendor chat API. Ollama runs the model on your machine, so you can explain issues on a flaky network (after GitHub fetch), swap models for free, and keep a beginner’s learning workflow independent of paid credits. Open-source models are inspectable and replaceable; this project is a thin, readable wrapper around GitHub’s public API plus one local prompt.
