"""Command-line interface for readability-meter."""
import argparse
import json
import re

from .core import analyze, hardest_sentences


def split_sections(text):
    """Split Markdown (# ...) or LaTeX (\\section{...}) documents into (title, text) pairs."""
    pat = re.compile(r"^#{1,3}\s+(.+)$|\\section\*?\{([^}]*)\}", re.M)
    marks = list(pat.finditer(text))
    if not marks:
        return [("document", text)]
    out = [("(preamble)", text[:marks[0].start()])] if text[:marks[0].start()].strip() else []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        out.append(((m.group(1) or m.group(2)).strip(), text[m.end():end]))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="readability-meter", description="Readability scores for a manuscript.")
    ap.add_argument("file", help=".txt, .md or .tex")
    ap.add_argument("--sections", action="store_true", help="score each section separately")
    ap.add_argument("--hardest", type=int, default=3, help="show the N hardest sentences")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    with open(args.file, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    res = analyze(text)
    if args.sections:
        res["sections"] = {t: analyze(body)["scores"] for t, body in split_sections(text)}
    res["hardest"] = hardest_sentences(text, args.hardest)
    if args.json:
        print(json.dumps(res, indent=2))
        return 0
    st, sc = res["stats"], res["scores"]
    print("%d sentences, %d words, %.1f words/sentence" % (st["sentences"], st["words"], sc["avg_sentence_length"]))
    for k in ("flesch_reading_ease", "flesch_kincaid_grade", "gunning_fog", "smog", "coleman_liau", "ari", "lix"):
        print("  %-22s %6.1f" % (k, sc[k]))
    print("  -> %s" % sc["interpretation"])
    for title, s in res.get("sections", {}).items():
        print("  [%s] FRE %.1f, grade %.1f, %.1f words/sentence" % (title[:30], s["flesch_reading_ease"],
                                                                   s["flesch_kincaid_grade"], s["avg_sentence_length"]))
    if res["hardest"]:
        print("\nHardest sentences:")
        for score, nw, s in res["hardest"]:
            print("  (%d words) %s" % (nw, s[:160]))
    return 0
