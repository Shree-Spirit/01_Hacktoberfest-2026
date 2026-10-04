import re
import time

import streamlit as st

from explain import explain, hallucinated_files, load_friend, repo_file_paths

st.set_page_config(page_title="Issue Explainer")
friend = load_friend()
st.sidebar.header("Friend profile")
st.sidebar.write(f"**{friend.get('name', '')}**")
st.sidebar.write(", ".join(friend.get("skills") or []))
st.title("Issue Explainer")
with st.form("explain_form"):
    url = st.text_input("GitHub issue URL")
    model = st.selectbox("Model", ["gemma3:4b", "qwen2.5:3b", "qwen2.5:7b"])
    submitted = st.form_submit_button("Explain")
if submitted and url.strip():
    m = re.search(r"github\.com/([^/]+)/([^/]+)/issues/(\d+)", url.strip())
    if not m:
        st.error("Use a URL like https://github.com/owner/repo/issues/123")
    else:
        owner, repo, number = m.group(1), m.group(2), int(m.group(3))
        with st.spinner("Explaining with local Ollama..."):
            start = time.perf_counter()
            result = explain(owner, repo, number, model)
            elapsed = time.perf_counter() - start
        st.markdown(result)
        st.caption(f"Time taken: {elapsed:.1f}s")
        tree, err = repo_file_paths(owner, repo)
        if not err:
            bad = hallucinated_files(result, tree)
            if bad:
                st.warning(
                    "File paths in Where to look that are not in the repo tree: "
                    + ", ".join(bad)
                )
