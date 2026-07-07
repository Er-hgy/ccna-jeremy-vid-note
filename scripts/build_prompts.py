#!/usr/bin/env python3
"""Combine local transcripts and chapters with reusable prompt templates."""

from __future__ import annotations

import html
import json
import logging
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VTT_TIMING = re.compile(r"^\s*\d{2}:\d{2}(?::\d{2})?\.\d{3}\s+-->\s+")
VTT_TAG = re.compile(r"<[^>]+>")
COURSE_DAY = re.compile(r"\bday\s+(?P<day>\d+)\b", re.IGNORECASE)


def setup_logging() -> None:
    log_dir = ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(log_dir / "build_prompts.log", encoding="utf-8")],
    )


def vtt_to_text(path: Path) -> str:
    """Convert VTT captions to readable, de-duplicated text with cue timestamps."""
    output: list[str] = []
    pending_time: str | None = None
    previous = ""
    for raw in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = raw.strip()
        if not line or line == "WEBVTT" or line.startswith(("Kind:", "Language:", "NOTE", "STYLE")):
            continue
        if VTT_TIMING.match(line):
            pending_time = line.split("-->", 1)[0].strip().split(".", 1)[0]
            continue
        if line.isdigit():
            continue
        clean = html.unescape(VTT_TAG.sub("", line)).strip()
        if not clean or clean == previous:
            continue
        # Auto-captions often contain the prior cue plus a few new words.
        if previous and clean.startswith(previous):
            clean = clean[len(previous) :].strip()
        if not clean:
            continue
        output.append(f"[{pending_time}] {clean}" if pending_time else clean)
        previous = html.unescape(VTT_TAG.sub("", line)).strip()
        pending_time = None
    return "\n".join(output)


def render(template: str, material: str) -> str:
    marker = "{{VIDEO_MATERIAL}}"
    if marker not in template:
        raise ValueError(f"Template is missing required marker: {marker}")
    return template.replace(marker, material)


def main() -> int:
    setup_logging()
    raw_root = ROOT / "videos_raw"
    if not raw_root.exists():
        logging.error("videos_raw does not exist. Run download_playlist.py first.")
        return 1
    try:
        chapter_template = (ROOT / "prompts" / "chapter_note_prompt.md").read_text(encoding="utf-8")
        quiz_template = (ROOT / "prompts" / "quiz_prompt.md").read_text(encoding="utf-8")
    except OSError as exc:
        logging.error("Could not read prompt templates: %s", exc)
        return 1

    output = ROOT / "generated_prompts"
    output.mkdir(exist_ok=True)
    # Remove files made by the old implementation, which incorrectly used the
    # playlist position as the course Day number. The patterns are deliberately
    # narrow so unrelated Markdown files are never touched.
    for old_path in output.glob("day_[0-9][0-9][0-9]_chapter_notes_prompt.md"):
        old_path.unlink()
    for old_path in output.glob("day_[0-9][0-9][0-9]_quiz_prompt.md"):
        old_path.unlink()
    made = skipped = 0
    for folder in sorted(path for path in raw_root.iterdir() if path.is_dir()):
        metadata_path = folder / "local_metadata.json"
        chapters_path = folder / "chapters.txt"
        subtitles = sorted(folder.glob("source.en*.vtt"))
        if not metadata_path.exists():
            logging.warning("Skipping %s: local_metadata.json is missing", folder.name)
            skipped += 1
            continue
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logging.warning("Skipping %s: invalid metadata (%s)", folder.name, exc)
            skipped += 1
            continue
        playlist_index = int(metadata.get("playlist_index", 0))
        course_day = metadata.get("course_day")
        if course_day is None:
            match = COURSE_DAY.search(metadata.get("title", ""))
            course_day = int(match.group("day")) if match else None
        label = f"Video {playlist_index:03d}" + (f" / Day {course_day}" if course_day is not None else "")
        if not chapters_path.exists():
            logging.warning("Skipping %s: chapters.txt is missing", label)
            skipped += 1
            continue
        if not subtitles:
            logging.warning("Skipping %s: English subtitle is missing", label)
            skipped += 1
            continue
        try:
            chapters = chapters_path.read_text(encoding="utf-8", errors="replace").strip()
            transcript = vtt_to_text(subtitles[0]).strip()
        except OSError as exc:
            logging.warning("Skipping %s: could not read source files (%s)", label, exc)
            skipped += 1
            continue
        if not chapters or not transcript:
            logging.warning("Skipping %s: chapters or transcript is empty", label)
            skipped += 1
            continue
        material = (
            f'# Video: {metadata.get("title", "Unknown")}\n\n'
            f'URL: {metadata.get("url", "Unknown")}\n\n'
            f'## Chapters\n\n{chapters}\n\n'
            f'## English transcript\n\n{transcript}\n'
        )
        try:
            day_slug = f"day_{int(course_day):03d}" if course_day is not None else "day_unknown"
            prefix = f"video_{playlist_index:03d}_{day_slug}"
            (output / f"{prefix}_chapter_notes_prompt.md").write_text(render(chapter_template, material), encoding="utf-8")
            (output / f"{prefix}_quiz_prompt.md").write_text(render(quiz_template, material), encoding="utf-8")
        except (OSError, ValueError) as exc:
            logging.error("%s prompt generation failed: %s", label, exc)
            skipped += 1
            continue
        logging.info("Generated prompts for %s", label)
        made += 1
    logging.info("Finished: %d generated, %d skipped", made, skipped)
    return 0 if made else 1


if __name__ == "__main__":
    sys.exit(main())
