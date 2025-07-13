#!/usr/bin/env python3
"""Convert multiple audio files to a single M4B file.

This script uses ``ffmpeg`` to concatenate audio files and encode them as an
M4B audiobook. Provide the input files in the order you want them to appear in
the final file.
"""

import argparse
import os
import subprocess
import sys
import tempfile


def check_ffmpeg() -> None:
    """Ensure ``ffmpeg`` is available on the system."""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise SystemExit("ffmpeg is required but was not found") from exc


def build_file_list(files):
    """Create a temporary file list for ffmpeg's concat demuxer."""
    tmp = tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt")
    with tmp:
        for path in files:
            abs_path = os.path.abspath(path)
            if not os.path.isfile(abs_path):
                tmp.close()
                os.unlink(tmp.name)
                raise SystemExit(f"Input file not found: {path}")
            tmp.write(f"file '{abs_path}'\n")
    return tmp.name


def convert_to_m4b(input_files, output_file):
    file_list = build_file_list(input_files)
    cmd = [
        "ffmpeg",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        file_list,
        "-acodec",
        "aac",
        "-b:a",
        "64k",
        "-vn",
        output_file,
    ]
    try:
        subprocess.run(cmd, check=True)
    finally:
        os.unlink(file_list)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_files", nargs="+", help="Audio files to include in order")
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output M4B filename",
    )
    args = parser.parse_args()

    output = args.output
    if not output.lower().endswith(".m4b"):
        output += ".m4b"

    check_ffmpeg()
    convert_to_m4b(args.input_files, output)


if __name__ == "__main__":
    main()
