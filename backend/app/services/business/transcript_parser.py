"""
services/business/transcript_parser.py
───────────────────────────────────────
Deterministic Transcript Parser.

Parses meeting transcript files in three formats:
1. .txt — Plain text or speaker-prefixed text
2. .vtt — WebVTT format (strips VTT headers, timing cues, speaker tags)
3. .srt — SubRip format (strips subtitle sequence numbers, timing cues)

Features:
- Preserves speaker labels ("Priya:", "John:")
- Normalizes whitespace and line breaks
- Extracts timing markers for evidence quote matching
- Detects empty or corrupt files and raises InvalidFileError

ZERO LLM DEPENDENCIES. 100% Deterministic Python logic.
"""

import re
from typing import Dict, Any, List
from app.core.config import settings
from app.core.exceptions import InvalidFileError
from app.core.logging import get_logger

logger = get_logger(__name__)

# RegEx patterns for timing cues
VTT_TIMING_PATTERN = re.compile(
    r"^\d{2}:\d{2}:\d{2}[\.,]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[\.,]\d{3}", re.MULTILINE
)
SRT_TIMING_PATTERN = re.compile(
    r"^\d{1,2}:\d{2}:\d{2}[\.,]\d{3}\s*-->\s*\d{1,2}:\d{2}:\d{2}[\.,]\d{3}", re.MULTILINE
)
SRT_SEQUENCE_PATTERN = re.compile(r"^\d+\s*$", re.MULTILINE)
SPEAKER_TAG_PATTERN = re.compile(r"<v\s+([^>]+)>", re.IGNORECASE)


class TranscriptParser:
    """Parser for .txt, .vtt, and .srt meeting transcript files."""

    @classmethod
    def parse(cls, filename: str, content_bytes: bytes) -> Dict[str, Any]:
        """
        Parse raw transcript file bytes into normalized text and metadata.

        Args:
            filename: Name of the uploaded file (e.g. "meeting.vtt")
            content_bytes: Raw file bytes

        Returns:
            Dict containing:
                - "raw_text": Normalized clean text
                - "filename": Original filename
                - "format": Format detected ("vtt", "srt", "txt")
                - "character_count": Length of cleaned text
                - "word_count": Approximate word count
                - "lines": List of clean speaker/transcript lines

        Raises:
            InvalidFileError: If format is unsupported or file is empty.
        """
        if not content_bytes or len(content_bytes.strip()) == 0:
            raise InvalidFileError("Transcript file is empty.", filename=filename)

        ext = cls._get_file_extension(filename)
        if ext not in settings.allowed_extensions_list:
            raise InvalidFileError(
                f"Unsupported file format '{ext}'. Allowed formats: {settings.allowed_extensions_list}",
                filename=filename,
            )

        # Decode UTF-8 (handling BOM if present)
        try:
            raw_content = content_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            try:
                raw_content = content_bytes.decode("latin-1")
            except Exception as exc:
                raise InvalidFileError(f"Failed to decode file content: {exc}", filename=filename)

        if ext == ".vtt":
            clean_text, lines = cls._parse_vtt(raw_content)
        elif ext == ".srt":
            clean_text, lines = cls._parse_srt(raw_content)
        else:
            clean_text, lines = cls._parse_txt(raw_content)

        if not clean_text.strip():
            raise InvalidFileError("Parsed transcript contains no valid text content.", filename=filename)

        word_count = len(clean_text.split())
        logger.info(
            f"[PARSE] Parsed '{filename}' ({ext}): {len(lines)} lines, {word_count} words, {len(clean_text)} chars"
        )

        return {
            "raw_text": clean_text,
            "filename": filename,
            "format": ext.lstrip("."),
            "character_count": len(clean_text),
            "word_count": word_count,
            "lines": lines,
        }

    @staticmethod
    def _get_file_extension(filename: str) -> str:
        """Extract lowercase extension including dot, e.g. '.vtt'"""
        if "." not in filename:
            return ""
        return "." + filename.rsplit(".", 1)[1].lower()

    @staticmethod
    def _parse_txt(content: str) -> tuple[str, List[str]]:
        """Parse plain text transcript."""
        lines = []
        for line in content.splitlines():
            line_str = line.strip()
            if line_str:
                lines.append(line_str)
        clean_text = "\n".join(lines)
        return clean_text, lines

    @classmethod
    def _parse_vtt(cls, content: str) -> tuple[str, List[str]]:
        """Parse WebVTT (.vtt) file, removing headers and timing markers."""
        lines = []
        for line in content.splitlines():
            line_str = line.strip()

            # Skip WebVTT header, NOTE blocks, or empty lines
            if not line_str or line_str.startswith("WEBVTT") or line_str.startswith("NOTE"):
                continue

            # Skip timing cues (00:00:01.000 --> 00:00:04.000)
            if VTT_TIMING_PATTERN.match(line_str):
                continue

            # Convert WebVTT voice tags <v Speaker Name> text -> Speaker Name: text
            match = SPEAKER_TAG_PATTERN.search(line_str)
            if match:
                speaker = match.group(1)
                text = SPEAKER_TAG_PATTERN.sub("", line_str).strip()
                line_str = f"{speaker}: {text}"

            lines.append(line_str)

        clean_text = "\n".join(lines)
        return clean_text, lines

    @classmethod
    def _parse_srt(cls, content: str) -> tuple[str, List[str]]:
        """Parse SubRip (.srt) file, removing sequence numbers and timing cues."""
        lines = []
        for line in content.splitlines():
            line_str = line.strip()

            if not line_str:
                continue

            # Skip subtitle sequence numbers (1, 2, 3...)
            if SRT_SEQUENCE_PATTERN.match(line_str):
                continue

            # Skip timing cues (00:00:01,000 --> 00:00:04,000)
            if SRT_TIMING_PATTERN.match(line_str):
                continue

            lines.append(line_str)

        clean_text = "\n".join(lines)
        return clean_text, lines
