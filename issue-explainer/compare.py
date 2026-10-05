"""Compare local models on the same GitHub issue."""
import sys
import time
from pathlib import Path

from explain import explain, hallucinated_files, repo_file_paths

ROOT = Path(__file__).resolve().parent
MODELS = ["gemma3:4b", "qwen2.5:3b", "qwen2.5:7b"]


def main():
    if len(sys.argv) != 4:
        print("Usage: python compare.py owner repo number")
        return 1
    owner, repo, number = sys.argv[1], sys.argv[2], int(sys.argv[3])
    tree, _ = repo_file_paths(owner, repo)
    lines = [
        f"# Comparison for {owner}/{repo}#{number}",
        "",
        "| Model | Time (s) |",
        "| --- | ---: |",
    ]
    bodies = []
    for model in MODELS:
        start = time.perf_counter()
        output = explain(owner, repo, number, model)
        elapsed = time.perf_counter() - start
        lines.append(f"| {model} | {elapsed:.1f} |")
        bad = hallucinated_files(output, tree or "")
        check = ", ".join(bad) if bad else "none"
        bodies.append(
            f"## {model} ({elapsed:.1f}s)\n\n{output}\n\n"
            f"**Hallucinated files:** {check}\n"
        )
    lines.extend(["", *bodies])
    path = ROOT / f"comparison_{repo}_{number}.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
