#!/usr/bin/env python3
"""Create one safely named, empty Markdown note file for each CCNA course day."""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DAY_RE = re.compile(r"\bday\s+(\d+)\b", re.IGNORECASE)
PART_RE = re.compile(r"\s*[\[(]?part\s*\d+[\])]?", re.IGNORECASE)
LAB_RE = re.compile(r"\blab\b", re.IGNORECASE)
EXTRA_RE = re.compile(r"\bextra\b|anki flashcards", re.IGNORECASE)


def extract_topic(title: str) -> str:
    """Remove playlist boilerplate and return the human topic from a title."""
    pieces = [piece.strip() for piece in title.split("|")]
    candidates = [
        piece
        for piece in pieces
        if piece
        and piece.lower() != "free ccna"
        and not DAY_RE.search(piece)
        and "ccna 200-301" not in piece.lower()
    ]
    topic = candidates[0] if candidates else title
    # Titles without pipes often end in forms such as "CCNA Day 3".
    topic = re.sub(r"\s*[/|:-]*\s*CCNA(?:\s+200-301)?\s+Day\s+\d+.*$", "", topic, flags=re.IGNORECASE)
    topic = PART_RE.sub("", topic)
    return re.sub(r"\s+", " ", topic).strip(" -_/()") or "ccna"


def slugify(value: str, max_length: int = 80) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", normalized).strip("_").lower()
    return (slug or "ccna")[:max_length].rstrip("_")


def main() -> int:
    raw_root = ROOT / "videos_raw"
    if not raw_root.exists():
        print("videos_raw does not exist. Run download_playlist.py first.", file=sys.stderr)
        return 1

    by_day: dict[int, list[str]] = defaultdict(list)
    for metadata_path in sorted(raw_root.glob("*/local_metadata.json")):
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Skipping invalid metadata {metadata_path}: {exc}", file=sys.stderr)
            continue
        title = metadata.get("title", "")
        course_day = metadata.get("course_day")
        if course_day is None:
            match = DAY_RE.search(title)
            course_day = int(match.group(1)) if match else None
        if course_day is None:
            continue
        # Core lecture topics produce clean daily filenames. Lab/Extra material
        # still belongs in that day's note, but does not make the name unwieldy.
        if not LAB_RE.search(title) and not EXTRA_RE.search(title):
            topic = extract_topic(title)
            if topic.casefold() not in {item.casefold() for item in by_day[int(course_day)]}:
                by_day[int(course_day)].append(topic)

    notes_root = ROOT / "notes"
    notes_root.mkdir(exist_ok=True)
    created = existing = 0
    for day, topics in sorted(by_day.items()):
        # Three core topics are enough to identify a day without producing
        # comically long Windows filenames on multi-part course days.
        topic_slug = slugify(" ".join(topics[:3]) if topics else "ccna")
        path = notes_root / f"day_{day:03d}_{topic_slug}.md"
        if path.exists():
            existing += 1
            continue
        prior_empty = [candidate for candidate in notes_root.glob(f"day_{day:03d}_*.md") if candidate.stat().st_size == 0]
        if len(prior_empty) == 1:
            prior_empty[0].rename(path)
            created += 1
            continue
        path.touch()
        created += 1
    print(f"Notes ready: {created} created, {existing} already existed, {len(by_day)} days total")
    return 0 if by_day else 1


if __name__ == "__main__":
    sys.exit(main())
