#!/usr/bin/env python3
"""Download playlist metadata, descriptions, and English subtitles only."""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_URL = "https://www.youtube.com/playlist?list=PLxbwE86jKRgMpuZuLBivzlM8s2Dk5lXBQ"
INVALID_WINDOWS_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
TIMESTAMP_LINE = re.compile(
    r"^\s*(?P<time>(?:\d{1,2}:)?\d{1,2}:\d{2})\s*(?:[-–—|:]\s*)?(?P<title>.*?)\s*$"
)
COURSE_DAY = re.compile(r"\bday\s+(?P<day>\d+)\b", re.IGNORECASE)


def safe_name(value: str, max_length: int = 120) -> str:
    """Return a deterministic Windows-safe path component."""
    value = INVALID_WINDOWS_CHARS.sub("_", value)
    value = re.sub(r"\s+", " ", value).strip().rstrip(". ")
    if not value:
        value = "untitled"
    # Avoid reserved DOS device names, even when an extension is present.
    stem = value.split(".", 1)[0].upper()
    if stem in {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}:
        value = f"_{value}"
    return value[:max_length].rstrip(". ")


def timestamp_seconds(value: str) -> int:
    parts = [int(part) for part in value.split(":")]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


def extract_course_day(title: str) -> int | None:
    """Extract Jeremy's course Day number from a video title."""
    match = COURSE_DAY.search(title)
    return int(match.group("day")) if match else None


def extract_chapters(description: str) -> list[dict[str, Any]]:
    """Extract a monotonic timestamp block from a YouTube description."""
    candidates: list[dict[str, Any]] = []
    for line in description.splitlines():
        match = TIMESTAMP_LINE.match(line)
        if not match:
            continue
        title = match.group("title").strip(" -–—|:") or "Untitled chapter"
        time_text = match.group("time")
        candidates.append({"time": time_text, "seconds": timestamp_seconds(time_text), "title": title})

    # Timestamps elsewhere in descriptions can be unrelated links. Keep the
    # longest monotonic run, which reliably captures the chapter block.
    runs: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    for item in candidates:
        if current and item["seconds"] <= current[-1]["seconds"]:
            runs.append(current)
            current = []
        current.append(item)
    if current:
        runs.append(current)
    return max(runs, key=len, default=[])


def format_duration(seconds: int | float | None) -> str:
    if seconds is None:
        return "Unknown"
    total = int(seconds)
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours else f"{minutes}:{secs:02d}"


def setup_logging() -> None:
    log_dir = ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    handlers = [logging.StreamHandler(), logging.FileHandler(log_dir / "download.log", encoding="utf-8")]
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", handlers=handlers)


def fetch_playlist(url: str) -> list[dict[str, Any]]:
    options = {"extract_flat": "in_playlist", "quiet": True, "ignoreerrors": True}
    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=False)
    if not info or not info.get("entries"):
        raise RuntimeError("The playlist contained no readable entries.")
    return [entry for entry in info["entries"] if entry]


def download_video(entry: dict[str, Any], index: int, total: int, output_root: Path) -> dict[str, Any] | None:
    title = entry.get("title") or entry.get("id") or "untitled"
    folder = output_root / f"{index:03d}_{safe_name(title)}"
    folder.mkdir(parents=True, exist_ok=True)
    video_url = entry.get("webpage_url") or entry.get("url")
    if video_url and not str(video_url).startswith("http"):
        video_url = f"https://www.youtube.com/watch?v={video_url}"
    if not video_url:
        logging.error("[%03d/%03d] No URL for %s; skipped", index, total, title)
        return None

    options = {
        "skip_download": True,
        "writeinfojson": True,
        "writedescription": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en", "en-orig", "en-US", "en-GB"],
        "subtitlesformat": "vtt",
        "outtmpl": str(folder / "source.%(ext)s"),
        "quiet": True,
        "no_warnings": False,
        "ignoreerrors": False,
        "windowsfilenames": True,
    }
    logging.info("[%03d/%03d] Fetching %s", index, total, title)
    try:
        with YoutubeDL(options) as ydl:
            info = ydl.extract_info(video_url, download=True)
    except DownloadError as exc:
        logging.error("[%03d] yt-dlp failed: %s", index, exc)
        return None
    except Exception:
        logging.exception("[%03d] Unexpected error", index)
        return None
    if not info:
        logging.error("[%03d] yt-dlp returned no metadata", index)
        return None

    # Add stable local bookkeeping without changing yt-dlp's source info JSON.
    local = {
        "playlist_index": index,
        "course_day": extract_course_day(info.get("title", title)),
        "title": info.get("title", title),
        "url": info.get("webpage_url", video_url),
        "duration": info.get("duration"),
        "folder": folder.name,
    }
    (folder / "local_metadata.json").write_text(json.dumps(local, ensure_ascii=False, indent=2), encoding="utf-8")

    description_path = folder / "source.description"
    description = description_path.read_text(encoding="utf-8", errors="replace") if description_path.exists() else info.get("description", "")
    chapters = extract_chapters(description or "")
    if chapters:
        text = "\n".join(f'{chapter["time"]} {chapter["title"]}' for chapter in chapters) + "\n"
        (folder / "chapters.txt").write_text(text, encoding="utf-8")
    else:
        logging.warning("[%03d] No description chapters found: %s", index, title)

    subtitles = sorted(folder.glob("source.en*.vtt"))
    if not subtitles:
        logging.warning("[%03d] No English subtitles found: %s", index, title)
    local["chapters"] = chapters
    local["has_subtitles"] = bool(subtitles)
    return local


def build_index(records: list[dict[str, Any]], path: Path) -> None:
    lines = ["# Jeremy's IT Lab — Free CCNA 200-301", "", f"Videos processed: {len(records)}", ""]
    for record in records:
        playlist_index = record["playlist_index"]
        course_day = record.get("course_day")
        day_text = f"Day {course_day}" if course_day is not None else "No Day number"
        lines.extend(
            [
                f'## Video {playlist_index:03d} — {day_text} — {record["title"]}',
                "",
                f'- Playlist index: {playlist_index:03d}',
                f'- Course day: {course_day if course_day is not None else "Unknown"}',
                f'- URL: {record["url"]}',
                f'- Duration: {format_duration(record.get("duration"))}',
                f'- Local folder: `videos_raw/{record["folder"]}/`',
                "- Chapters:",
            ]
        )
        if record.get("chapters"):
            lines.extend(f'  - `{item["time"]}` {item["title"]}' for item in record["chapters"])
        else:
            lines.append("  - No chapters found in description")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def load_local_records(output_root: Path) -> list[dict[str, Any]]:
    """Load downloaded records and refresh derived fields without YouTube access."""
    records: list[dict[str, Any]] = []
    for folder in sorted(path for path in output_root.iterdir() if path.is_dir()):
        metadata_path = folder / "local_metadata.json"
        if not metadata_path.exists():
            logging.warning("Skipping %s: local_metadata.json is missing", folder.name)
            continue
        try:
            record = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logging.warning("Skipping %s: invalid local metadata (%s)", folder.name, exc)
            continue
        record["course_day"] = extract_course_day(record.get("title", ""))
        chapters_path = folder / "chapters.txt"
        chapters: list[dict[str, Any]] = []
        if chapters_path.exists():
            for line in chapters_path.read_text(encoding="utf-8", errors="replace").splitlines():
                match = TIMESTAMP_LINE.match(line)
                if match:
                    time_text = match.group("time")
                    chapters.append({
                        "time": time_text,
                        "seconds": timestamp_seconds(time_text),
                        "title": match.group("title").strip(" -–—|:") or "Untitled chapter",
                    })
        record["chapters"] = chapters
        record["has_subtitles"] = bool(list(folder.glob("source.en*.vtt")))
        metadata_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        records.append(record)
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL, help="YouTube playlist URL")
    parser.add_argument("--limit", type=int, help="Process only the first N entries (useful for testing)")
    parser.add_argument("--local-only", action="store_true", help="Rebuild metadata and index from existing files without accessing YouTube")
    args = parser.parse_args()
    setup_logging()
    output_root = ROOT / "videos_raw"
    output_root.mkdir(exist_ok=True)
    if args.local_only:
        records = load_local_records(output_root)
        build_index(records, ROOT / "index.md")
        logging.info("Rebuilt local metadata and index for %d videos", len(records))
        return 0 if records else 1
    try:
        entries = fetch_playlist(args.url)
    except Exception as exc:
        logging.error("Could not read playlist: %s", exc)
        return 1
    if args.limit:
        entries = entries[: args.limit]
    records = []
    for index, entry in enumerate(entries, start=1):
        record = download_video(entry, index, len(entries), output_root)
        if record:
            records.append(record)
    build_index(records, ROOT / "index.md")
    logging.info("Finished: %d succeeded, %d failed", len(records), len(entries) - len(records))
    return 0 if records else 1


if __name__ == "__main__":
    sys.exit(main())
