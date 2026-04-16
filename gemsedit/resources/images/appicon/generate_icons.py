#!/usr/bin/env python3
"""Generate icon sizes from appicon.png."""

from pathlib import Path

from PIL import Image

SIZES = [16, 24, 32, 48, 64, 128, 256, 512]
ICO_SIZES = [16, 24, 32, 48, 64, 128, 256]  # Sizes to include in .ico file


def main():
    script_dir = Path(__file__).parent
    source = script_dir / "appicon.png"

    if not source.exists():
        print(f"Source image not found: {source}")
        return

    img = Image.open(source)
    print(f"Loaded {source.name} ({img.width}x{img.height})")

    # Generate individual PNG files
    for size in SIZES:
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        output = script_dir / f"icon_{size}.png"
        resized.save(output, "PNG")
        print(f"Created {output.name}")

    # Generate Windows .ico file with multiple sizes
    ico_images = []
    for size in ICO_SIZES:
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        ico_images.append(resized)

    ico_output = script_dir / "appicon.ico"
    # Save the largest image, with all sizes embedded
    ico_images[0].save(
        ico_output,
        format="ICO",
        sizes=[(img.width, img.height) for img in ico_images],
        append_images=ico_images[1:],
    )
    print(f"Created {ico_output.name}")

    print("Done!")


if __name__ == "__main__":
    main()
