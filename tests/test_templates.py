"""
Tests for template assets in templates/.

Templates are the base PNG files used by the automation pipeline to render
posts. Each category (DICA, QUARTO, SERVICO, VAGA) must have exactly one
feed and one story variant with Instagram-standard dimensions.
"""

import os
import unittest
from .utils import (
    TEMPLATES_DIR,
    FEED_DIMENSIONS,
    STORY_DIMENSIONS,
    EXPECTED_TEMPLATE_CATEGORIES,
    EXPECTED_TEMPLATE_FORMATS,
    read_png_dimensions,
    is_valid_png,
)

EXPECTED_DIMENSIONS = {
    "feed": FEED_DIMENSIONS,
    "story": STORY_DIMENSIONS,
}


def _template_path(category: str, fmt: str) -> str:
    return os.path.join(TEMPLATES_DIR, f"{category}-{fmt}.png")


class TestTemplateCompleteness(unittest.TestCase):
    """Every category/format combination must have a corresponding template file."""

    def test_all_expected_templates_exist(self):
        missing = []
        for category in EXPECTED_TEMPLATE_CATEGORIES:
            for fmt in EXPECTED_TEMPLATE_FORMATS:
                path = _template_path(category, fmt)
                if not os.path.isfile(path):
                    missing.append(f"{category}-{fmt}.png")
        self.assertEqual(
            missing,
            [],
            f"Missing templates: {missing}",
        )

    def test_no_unexpected_templates(self):
        """Guard against orphaned or misnamed template files."""
        expected_names = {
            f"{cat}-{fmt}.png"
            for cat in EXPECTED_TEMPLATE_CATEGORIES
            for fmt in EXPECTED_TEMPLATE_FORMATS
        }
        actual_names = set(os.listdir(TEMPLATES_DIR))
        unexpected = actual_names - expected_names
        self.assertEqual(
            unexpected,
            set(),
            f"Unexpected files in templates/: {unexpected}",
        )


class TestTemplateValidity(unittest.TestCase):
    """Each template must be a valid, uncorrupted PNG file."""

    def test_all_templates_are_valid_pngs(self):
        corrupt = []
        for category in EXPECTED_TEMPLATE_CATEGORIES:
            for fmt in EXPECTED_TEMPLATE_FORMATS:
                path = _template_path(category, fmt)
                if os.path.isfile(path) and not is_valid_png(path):
                    corrupt.append(f"{category}-{fmt}.png")
        self.assertEqual(corrupt, [], f"Corrupt or invalid PNG files: {corrupt}")

    def test_no_empty_templates(self):
        empty = []
        for category in EXPECTED_TEMPLATE_CATEGORIES:
            for fmt in EXPECTED_TEMPLATE_FORMATS:
                path = _template_path(category, fmt)
                if os.path.isfile(path) and os.path.getsize(path) == 0:
                    empty.append(f"{category}-{fmt}.png")
        self.assertEqual(empty, [], f"Empty template files: {empty}")


class TestTemplateDimensions(unittest.TestCase):
    """
    Templates must have Instagram-standard dimensions:
      feed  → 1080 × 1350  (4:5 portrait)
      story → 1080 × 1920  (9:16 portrait)
    """

    def _assert_dimensions(self, category: str, fmt: str):
        path = _template_path(category, fmt)
        if not os.path.isfile(path):
            self.skipTest(f"Template not found: {path}")
        actual = read_png_dimensions(path)
        expected = EXPECTED_DIMENSIONS[fmt]
        self.assertEqual(
            actual,
            expected,
            f"{category}-{fmt}.png: expected {expected}, got {actual}",
        )

    def test_dica_feed_dimensions(self):
        self._assert_dimensions("DICA", "feed")

    def test_dica_story_dimensions(self):
        self._assert_dimensions("DICA", "story")

    def test_quarto_feed_dimensions(self):
        self._assert_dimensions("QUARTO", "feed")

    def test_quarto_story_dimensions(self):
        self._assert_dimensions("QUARTO", "story")

    def test_servico_feed_dimensions(self):
        self._assert_dimensions("SERVICO", "feed")

    def test_servico_story_dimensions(self):
        self._assert_dimensions("SERVICO", "story")

    def test_vaga_feed_dimensions(self):
        self._assert_dimensions("VAGA", "feed")

    def test_vaga_story_dimensions(self):
        self._assert_dimensions("VAGA", "story")


class TestTemplateNamingConvention(unittest.TestCase):
    """Template filenames must follow the pattern {CATEGORY}-{format}.png."""

    def test_template_names_are_uppercase_category(self):
        """Category portion must be uppercase (DICA, not dica or Dica)."""
        for name in os.listdir(TEMPLATES_DIR):
            if name.endswith(".png"):
                parts = name[:-4].split("-")
                self.assertGreaterEqual(len(parts), 2, f"Unexpected filename: {name}")
                category = parts[0]
                self.assertEqual(
                    category,
                    category.upper(),
                    f"Category in '{name}' should be uppercase",
                )

    def test_template_format_is_lowercase(self):
        """Format portion (feed/story) must be lowercase."""
        for name in os.listdir(TEMPLATES_DIR):
            if name.endswith(".png"):
                parts = name[:-4].split("-")
                if len(parts) >= 2:
                    fmt = parts[-1]
                    self.assertEqual(
                        fmt,
                        fmt.lower(),
                        f"Format in '{name}' should be lowercase",
                    )


if __name__ == "__main__":
    unittest.main()
