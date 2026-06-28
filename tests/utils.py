import struct
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(REPO_ROOT, "templates")
POSTS_DIR = os.path.join(REPO_ROOT, "posts")

FEED_DIMENSIONS = (1080, 1350)
STORY_DIMENSIONS = (1080, 1920)

# Timestamp-named directories created by the automation pipeline
POST_DIR_PATTERN = re.compile(r"^\d{8}-\d{6}$")

EXPECTED_TEMPLATE_CATEGORIES = ["DICA", "QUARTO", "SERVICO", "VAGA"]
EXPECTED_TEMPLATE_FORMATS = ["feed", "story"]


def read_png_dimensions(path: str) -> tuple[int, int]:
    """Return (width, height) from a PNG file header without external dependencies."""
    with open(path, "rb") as f:
        signature = f.read(8)
        if signature != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"Not a valid PNG file: {path}")
        f.read(4)  # IHDR chunk length
        chunk_type = f.read(4)
        if chunk_type != b"IHDR":
            raise ValueError(f"Missing IHDR chunk: {path}")
        ihdr = f.read(13)
        width = struct.unpack(">I", ihdr[0:4])[0]
        height = struct.unpack(">I", ihdr[4:8])[0]
    return width, height


def is_valid_png(path: str) -> bool:
    try:
        read_png_dimensions(path)
        return True
    except (ValueError, struct.error, OSError):
        return False
