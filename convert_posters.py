#!/usr/bin/env python3
"""
Improved script to convert movie posters to TRMNL-compatible 1-bit PNG format
Based on ImageMagick guide: https://docs.usetrmnl.com/go/imagemagick-guide

Usage:
    python3 convert_posters.py input.jpg output.png
    python3 convert_posters.py --batch /path/to/posters/
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def convert_single_image(input_path, output_path, dither=True):
    """
    Convert a single image to TRMNL-compatible 1-bit PNG format
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        print(f"❌ Input file not found: {input_path}")
        return False

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # ImageMagick command for high-quality 1-bit PNG (from TRMNL docs)
    if dither:
        # Use Floyd-Steinberg dithering for better quality
        cmd = [
            'magick', str(input_path),
            '-resize', '200x300>',  # Max dimensions, maintain aspect ratio
            '-dither', 'FloydSteinberg',
            '-remap', 'pattern:gray50',
            '-depth', '1',
            '-strip',
            'png:' + str(output_path)
        ]
    else:
        # Simple monochrome conversion
        cmd = [
            'magick', str(input_path),
            '-resize', '200x300>',
            '-monochrome',
            '-colors', '2',
            '-depth', '1',
            '-strip',
            'png:' + str(output_path)
        ]

    try:
        print(f"Converting {input_path.name} → {output_path.name}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Verify the output
        verify_cmd = ['magick', 'identify', '-verbose', str(output_path)]
        verify_result = subprocess.run(verify_cmd, capture_output=True, text=True)

        if '1-bit' in verify_result.stdout and 'PNG' in verify_result.stdout:
            print(f"✅ Successfully converted to 1-bit PNG")
            return True
        else:
            print(f"⚠️  Converted but format verification failed")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ ImageMagick error: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ ImageMagick not found. Install with: brew install imagemagick")
        return False

def batch_convert(directory, output_dir=None):
    """
    Convert all images in a directory
    """
    directory = Path(directory)
    if output_dir:
        output_dir = Path(output_dir)
    else:
        output_dir = directory / "converted"

    output_dir.mkdir(exist_ok=True)

    converted_count = 0
    total_count = 0

    for file_path in directory.glob("*"):
        if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp', '.tiff', '.bmp']:
            total_count += 1
            output_path = output_dir / f"{file_path.stem}_1bit.png"
            if convert_single_image(file_path, output_path):
                converted_count += 1

    print(f"\n📊 Batch conversion complete: {converted_count}/{total_count} images converted")

def main():
    parser = argparse.ArgumentParser(description="Convert images to TRMNL-compatible 1-bit PNG format")
    parser.add_argument('input', help='Input image file or directory')
    parser.add_argument('output', nargs='?', help='Output file (for single image) or output directory (for batch)')
    parser.add_argument('--batch', action='store_true', help='Batch convert all images in directory')
    parser.add_argument('--no-dither', action='store_true', help='Disable dithering for simple conversion')

    args = parser.parse_args()

    if args.batch or (args.output and Path(args.input).is_dir()):
        batch_convert(args.input, args.output)
    else:
        if not args.output:
            input_path = Path(args.input)
            output_path = input_path.parent / f"{input_path.stem}_1bit.png"
        else:
            output_path = Path(args.output)

        convert_single_image(args.input, output_path, dither=not args.no_dither)

if __name__ == "__main__":
    main()
