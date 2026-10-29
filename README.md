# readability-meter

**Measure how readable your manuscript is (Flesch, Flesch-Kincaid, Gunning Fog, SMOG,
Coleman-Liau, ARI, LIX), section by section, and find the sentences worth rewriting first.**

Part of the *Research Automation Toolkit*: 100 open tools for daily research work.

## Why

Academic writing is notoriously hard to read, and readability affects how often papers are
read, understood and cited. Lay summaries, grant abstracts and patient information sheets often
have explicit readability targets. Word processors offer one score for plain text only; this tool
understands LaTeX and Markdown and points to concrete sentences.

## Features

- Seven classic formulas plus average sentence length and an interpretation band
- Sentence splitter aware of academic abbreviations (`Fig.`, `et al.`, `e.g.`, decimals)
- Cleans LaTeX commands, citations, inline math, URLs and numeric citation brackets
- Per-section scores (`# Heading` or `\section{}`) to compare Introduction vs Methods
- "Hardest sentences" list ranked by length x syllable density
- JSON output for tracking readability across drafts

## Usage

```bash
pip install .
readability-meter abstract.txt
readability-meter paper.tex --sections --hardest 5
readability-meter lay_summary.md --json
```

Formulas were designed for general English prose; use them to compare drafts, not as absolute truth.

## Testing

```bash
python -m unittest discover -s tests -t .
```

## License

MIT (c) JANIN A APURBA
