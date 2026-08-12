from pathlib import Path
import re
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ManuscriptArtifactTests(unittest.TestCase):
    def test_certificate_table_is_reproducible(self):
        table = ROOT / "manuscript" / "generated_certificate_table.tex"
        before = table.read_bytes()
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "render_certificate_table.py")],
            check=True,
            cwd=ROOT,
        )
        self.assertEqual(table.read_bytes(), before)

    def test_no_stale_conditional_claim_remains(self):
        manuscript = (ROOT / "manuscript" / "main.tex").read_text(encoding="utf-8")
        self.assertNotIn("Conditional all-orders", manuscript)
        self.assertNotIn("The remaining task is", manuscript)
        self.assertIn("\\input{generated_certificate_table}", manuscript)

    def test_every_citation_has_a_bibtex_entry(self):
        manuscript = (ROOT / "manuscript" / "main.tex").read_text(encoding="utf-8")
        bibliography = (ROOT / "manuscript" / "references.bib").read_text(
            encoding="utf-8"
        )
        cited = {
            key.strip()
            for group in re.findall(r"\\cite\{([^}]+)\}", manuscript)
            for key in group.split(",")
        }
        entries = set(re.findall(r"@[A-Za-z]+\{([^,]+),", bibliography))
        self.assertEqual(cited - entries, set())

    def test_tex_braces_are_balanced(self):
        for name in ("main.tex", "generated_certificate_table.tex"):
            text = (ROOT / "manuscript" / name).read_text(encoding="utf-8")
            depth = 0
            for character in text:
                if character == "{":
                    depth += 1
                elif character == "}":
                    depth -= 1
                    self.assertGreaterEqual(depth, 0, name)
            self.assertEqual(depth, 0, name)


if __name__ == "__main__":
    unittest.main()
