"""
Tests for rendered post assets in posts/.

Posts are PNG files rendered by the automation pipeline and organized into
timestamp-named directories (YYYYMMDD-HHMMSS). The 'test/' subdirectory is
excluded from production checks.

Known issues surfaced by these tests:
  - Several existing posts have non-standard widths (e.g. 1587px instead of 1080px)
    because they were rendered before dimension constraints were enforced.
  - The carousel slides under 20260605-105635 use 1119/1482/1579 × 1366, which
    does not match any Instagram standard format.
"""

import os
import re
import unittest
from .utils import (
    POSTS_DIR,
    POST_DIR_PATTERN,
    FEED_DIMENSIONS,
    STORY_DIMENSIONS,
    read_png_dimensions,
    is_valid_png,
)

INSTAGRAM_STANDARD_DIMENSIONS = {FEED_DIMENSIONS, STORY_DIMENSIONS}

# Carousel slides share height with the feed format but may differ in width;
# a valid carousel slide must have standard height.
VALID_HEIGHTS = {FEED_DIMENSIONS[1], STORY_DIMENSIONS[1]}


def _production_post_dirs():
    """Return timestamp-named subdirectories under posts/ (excludes 'test/')."""
    return [
        os.path.join(POSTS_DIR, d)
        for d in os.listdir(POSTS_DIR)
        if POST_DIR_PATTERN.match(d) and os.path.isdir(os.path.join(POSTS_DIR, d))
    ]


def _all_post_pngs(include_test_dir: bool = False):
    """Yield (rel_path, abs_path) for every PNG under posts/."""
    for root, dirs, files in os.walk(POSTS_DIR):
        rel_root = os.path.relpath(root, POSTS_DIR)
        if not include_test_dir and rel_root.startswith("test"):
            continue
        for f in files:
            if f.lower().endswith(".png"):
                abs_path = os.path.join(root, f)
                rel_path = os.path.relpath(abs_path, POSTS_DIR)
                yield rel_path, abs_path


class TestPostDirectoryNaming(unittest.TestCase):
    """Production post directories must follow the YYYYMMDD-HHMMSS pattern."""

    def test_production_directories_match_timestamp_pattern(self):
        bad = []
        for name in os.listdir(POSTS_DIR):
            path = os.path.join(POSTS_DIR, name)
            if os.path.isdir(path) and name != "test":
                if not POST_DIR_PATTERN.match(name):
                    bad.append(name)
        self.assertEqual(bad, [], f"Directories with non-standard names: {bad}")

    def test_timestamp_directories_are_not_empty(self):
        empty = []
        for d in _production_post_dirs():
            pngs = [f for f in os.listdir(d) if f.lower().endswith(".png")]
            if not pngs:
                empty.append(os.path.basename(d))
        self.assertEqual(empty, [], f"Empty post directories: {empty}")


class TestPostFileValidity(unittest.TestCase):
    """Every post PNG must be a valid, non-empty file."""

    def test_all_posts_are_valid_pngs(self):
        corrupt = []
        for rel_path, abs_path in _all_post_pngs():
            if not is_valid_png(abs_path):
                corrupt.append(rel_path)
        self.assertEqual(corrupt, [], f"Corrupt or invalid PNG files: {corrupt}")

    def test_no_empty_post_files(self):
        empty = []
        for rel_path, abs_path in _all_post_pngs():
            if os.path.getsize(abs_path) == 0:
                empty.append(rel_path)
        self.assertEqual(empty, [], f"Empty post files: {empty}")


class TestPostDimensions(unittest.TestCase):
    """
    Rendered posts must use Instagram-standard dimensions.

    Standard formats:
      feed      → 1080 × 1350  (4:5 portrait)
      story     → 1080 × 1920  (9:16 portrait)
      square    → 1080 × 1080  (1:1) — not currently used but allowed

    Carousel slides must at least have 1080px width.

    NOTE: Several existing posts predate this constraint and will fail these
    tests — that is intentional. The failures document the technical debt and
    should be resolved by re-rendering those assets.
    """

    ALLOWED_DIMENSIONS = {
        (1080, 1080),   # square
        (1080, 1350),   # feed portrait
        (1080, 1920),   # story
    }

    def test_all_posts_have_standard_dimensions(self):
        non_standard = []
        for rel_path, abs_path in _all_post_pngs():
            dims = read_png_dimensions(abs_path)
            if dims not in self.ALLOWED_DIMENSIONS:
                non_standard.append(f"{rel_path}: {dims}")
        self.assertEqual(
            non_standard,
            [],
            "Posts with non-standard dimensions (re-render required):\n  "
            + "\n  ".join(non_standard),
        )

    def test_all_posts_have_standard_width(self):
        """Width must always be exactly 1080px for all Instagram formats."""
        wrong_width = []
        for rel_path, abs_path in _all_post_pngs():
            w, h = read_png_dimensions(abs_path)
            if w != 1080:
                wrong_width.append(f"{rel_path}: width={w}")
        self.assertEqual(
            wrong_width,
            [],
            "Posts with non-1080px width:\n  " + "\n  ".join(wrong_width),
        )

    def test_all_posts_have_valid_height(self):
        """Height must be one of the standard Instagram heights."""
        bad_height = []
        for rel_path, abs_path in _all_post_pngs():
            w, h = read_png_dimensions(abs_path)
            if h not in VALID_HEIGHTS:
                bad_height.append(f"{rel_path}: height={h}")
        self.assertEqual(
            bad_height,
            [],
            "Posts with non-standard height:\n  " + "\n  ".join(bad_height),
        )


class TestTestDirectory(unittest.TestCase):
    """
    The posts/test/ directory holds sample assets for pipeline integration
    tests. It has relaxed rules but must still contain valid PNGs.
    """

    TEST_DIR = os.path.join(POSTS_DIR, "test")

    def test_test_directory_exists(self):
        self.assertTrue(
            os.path.isdir(self.TEST_DIR),
            "posts/test/ directory is missing",
        )

    def test_test_directory_pngs_are_valid(self):
        if not os.path.isdir(self.TEST_DIR):
            self.skipTest("posts/test/ does not exist")
        corrupt = []
        for f in os.listdir(self.TEST_DIR):
            if f.lower().endswith(".png"):
                path = os.path.join(self.TEST_DIR, f)
                if not is_valid_png(path):
                    corrupt.append(f)
        self.assertEqual(corrupt, [], f"Corrupt test fixtures: {corrupt}")


if __name__ == "__main__":
    unittest.main()
