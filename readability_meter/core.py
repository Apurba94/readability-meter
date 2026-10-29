"""Sentence/word/syllable statistics and classic readability formulas."""
import math
import re

_ABBREV = ("e.g.", "i.e.", "et al.", "etc.", "Fig.", "Figs.", "Eq.", "Eqs.", "vs.", "cf.", "Dr.", "Prof.",
           "approx.", "No.", "Ref.", "Refs.", "Sec.", "Tab.", "ca.", "resp.")
_WORD = re.compile(r"[A-Za-z]+(?:['\u2019-][A-Za-z]+)*")


def syllables(word):
    """Heuristic English syllable count: vowel groups after removing silent endings."""
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    if len(w) <= 3:
        return 1
    if w.endswith("es") and not w.endswith(("ses", "zes", "ces", "ges", "xes")):
        w = w[:-2]
    elif w.endswith("ed") and not w.endswith(("ted", "ded")):
        w = w[:-2]
    elif w.endswith("e") and not w.endswith("le"):
        w = w[:-1]
    n = len(re.findall(r"[aeiouy]+", w))
    n += len(re.findall(r"i[ao]|eo|ua|iu", w))  # vowel pairs usually pronounced separately
    return max(1, n)


def clean_text(text):
    """Strip Markdown/LaTeX markup, URLs, citations and numbers in brackets."""
    text = re.sub(r"(?<!\\)%.*", "", text)
    text = re.sub(r"\\(?:cite\w*|ref|eqref|label|url)\s*(?:\[[^\]]*\])?\{[^}]*\}", "", text)
    text = re.sub(r"\$[^$]*\$", "x", text)
    text = re.sub(r"\\[a-zA-Z]+\*?", " ", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"\[[0-9,\-\u2013 ]+\]", "", text)
    text = re.sub(r"[#*_`>{}]", " ", text)
    return text


def sentences(text):
    t = clean_text(text)
    for a in _ABBREV:
        t = t.replace(a, a.replace(".", "\u2024"))
    t = re.sub(r"(\d)\.(\d)", "\\1\u2024\\2", t)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])|\n\s*\n", t)
    return [p.replace("\u2024", ".").strip() for p in parts if _WORD.search(p)]


def text_stats(text):
    sents = sentences(text)
    words = [w for s in sents for w in _WORD.findall(s)]
    syl = [syllables(w) for w in words]
    return {
        "sentences": len(sents),
        "words": len(words),
        "syllables": sum(syl),
        "letters": sum(len(re.sub(r"[^A-Za-z]", "", w)) for w in words),
        "complex_words": sum(1 for w, s in zip(words, syl) if s >= 3 and not w[0].isupper() and "-" not in w),
        "polysyllables": sum(1 for s in syl if s >= 3),
        "long_words": sum(1 for w in words if len(w) > 6),
    }


def scores(st):
    """Return the standard formulas computed from text_stats output."""
    s, w = max(st["sentences"], 1), max(st["words"], 1)
    return {
        "flesch_reading_ease": round(206.835 - 1.015 * w / s - 84.6 * st["syllables"] / w, 1),
        "flesch_kincaid_grade": round(0.39 * w / s + 11.8 * st["syllables"] / w - 15.59, 1),
        "gunning_fog": round(0.4 * (w / s + 100 * st["complex_words"] / w), 1),
        "smog": round(1.0430 * math.sqrt(st["polysyllables"] * 30 / s) + 3.1291, 1),
        "coleman_liau": round(0.0588 * 100 * st["letters"] / w - 0.296 * 100 * s / w - 15.8, 1),
        "ari": round(4.71 * st["letters"] / w + 0.5 * w / s - 21.43, 1),
        "lix": round(w / s + 100 * st["long_words"] / w, 1),
        "avg_sentence_length": round(w / s, 1),
    }


def interpret(fre):
    for limit, label in ((90, "very easy"), (70, "easy"), (60, "plain English"), (50, "fairly difficult"),
                         (30, "difficult (typical academic)"), (-1e9, "very difficult")):
        if fre >= limit:
            return label


def hardest_sentences(text, n=5):
    """The n sentences with the most words x mean syllables per word (good editing targets)."""
    out = []
    for s in sentences(text):
        ws = _WORD.findall(s)
        if ws:
            out.append((len(ws) * sum(map(syllables, ws)) / len(ws), len(ws), s))
    return [(round(sc, 1), nw, s) for sc, nw, s in sorted(out, reverse=True)[:n]]


def analyze(text):
    st = text_stats(text)
    sc = scores(st)
    sc["interpretation"] = interpret(sc["flesch_reading_ease"])
    return {"stats": st, "scores": sc}
