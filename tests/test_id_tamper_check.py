import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from id_tamper_check import compare_documents, save_result


class CompareDocumentsTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp_dir.name)
        self.reference = self.directory / "reference.png"
        self.candidate = self.directory / "candidate.png"

    def tearDown(self):
        self.temp_dir.cleanup()

    def _save(self, path: Path, pixels: np.ndarray) -> None:
        Image.fromarray(pixels.astype(np.uint8), mode="RGB").save(path)

    def test_identical_images_score_one_and_have_no_regions(self):
        pixels = np.full((120, 180, 3), 220, dtype=np.uint8)
        self._save(self.reference, pixels)
        self._save(self.candidate, pixels)

        result = compare_documents(self.reference, self.candidate)

        self.assertAlmostEqual(result.score, 1.0, places=6)
        self.assertEqual(result.regions, ())
        self.assertFalse(result.threshold.any())

    def test_changed_area_is_detected_and_outputs_are_saved(self):
        reference = np.full((120, 180, 3), 240, dtype=np.uint8)
        candidate = reference.copy()
        candidate[35:85, 60:125] = 25
        self._save(self.reference, reference)
        self._save(self.candidate, candidate)

        result = compare_documents(self.reference, self.candidate)
        output_dir = self.directory / "result"
        save_result(result, output_dir)

        self.assertLess(result.score, 1.0)
        self.assertGreaterEqual(len(result.regions), 1)
        self.assertTrue((output_dir / "difference.png").is_file())
        self.assertTrue((output_dir / "candidate_annotated.png").is_file())

    def test_invalid_area_ratio_is_rejected(self):
        with self.assertRaises(ValueError):
            compare_documents(self.reference, self.candidate, min_region_area_ratio=1.0)


if __name__ == "__main__":
    unittest.main()
