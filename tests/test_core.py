import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from readability_meter.cli import main, split_sections
from readability_meter.core import analyze, hardest_sentences, scores, sentences, syllables, text_stats

SIMPLE = "The cat sat on the mat. The dog ran. It was fun."
HARD = ("The heterogeneous methodological considerations underlying contemporary computational "
        "epidemiological investigations necessitate comprehensive interdisciplinary collaboration.")


class SyllableTests(unittest.TestCase):
    def test_known_words(self):
        for word, n in {"cat": 1, "table": 2, "readability": 5, "computer": 3, "the": 1, "wanted": 2,
                        "beautiful": 3, "studio": 3, "jumped": 1, "makes": 1, "boxes": 2}.items():
            self.assertEqual(syllables(word), n, word)


class SentenceTests(unittest.TestCase):
    def test_abbreviations_and_decimals_do_not_split(self):
        s = sentences("As shown in Fig. 2, the value was 3.5 mm, e.g. large. Smith et al. agree. Done!")
        self.assertEqual(len(s), 3)

    def test_latex_and_citations_cleaned(self):
        st = text_stats(r"We use \emph{deep} models \cite{a,b} [1, 2]. % hidden words here")
        self.assertEqual(st["words"], 4)


class ScoreTests(unittest.TestCase):
    def test_simple_text_is_easier_than_hard_text(self):
        easy, hard = analyze(SIMPLE)["scores"], analyze(HARD)["scores"]
        self.assertGreater(easy["flesch_reading_ease"], 90)
        self.assertLess(hard["flesch_reading_ease"], 0)
        self.assertLess(easy["flesch_kincaid_grade"], hard["flesch_kincaid_grade"])
        self.assertEqual(analyze(HARD)["scores"]["interpretation"], "very difficult")

    def test_formula_values(self):
        st = {"sentences": 2, "words": 20, "syllables": 30, "letters": 100, "complex_words": 2,
              "polysyllables": 2, "long_words": 5}
        sc = scores(st)
        self.assertEqual(sc["flesch_reading_ease"], 69.8)   # 206.835 - 1.015*10 - 84.6*1.5
        self.assertEqual(sc["gunning_fog"], 8.0)
        self.assertEqual(sc["avg_sentence_length"], 10.0)

    def test_hardest_sentence_ranked_first(self):
        self.assertTrue(hardest_sentences(SIMPLE + " " + HARD, 1)[0][2].startswith("The heterogeneous"))


class CliTests(unittest.TestCase):
    def test_sections_and_json(self):
        md = "# Intro\n" + SIMPLE + "\n# Methods\n" + HARD + "\n"
        self.assertEqual([t for t, _ in split_sections(md)], ["Intro", "Methods"])
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "paper.md")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(md)
            with redirect_stdout(io.StringIO()) as buf:
                main([p, "--sections"])
            self.assertIn("[Methods]", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
