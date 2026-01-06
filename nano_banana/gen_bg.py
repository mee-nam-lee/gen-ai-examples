from PIL import Image
import os

def generate_white_background_image(width, height, output_filename_base="img"):
    """
    Generates a white background image of specified width and height.

    Args:
        width (int): The width of the image.
        height (int): The height of the image.
        output_filename_base (str): The base name for the output image file (e.g., "img").
    """
    if not isinstance(width, int) or not isinstance(height, int) or width <= 0 or height <= 0:
        raise ValueError("Width and height must be positive integers.")

    # Construct filename with dimensions: e.g., "img_1920x1080.png"
    final_filename = f"{output_filename_base}_{width}x{height}.png"

    # Create a new white image in RGB format
    img = Image.new("RGB", (width, height), color = 'white')
    img.save(final_filename)
    print(f"Generated {final_filename} with dimensions {width}x{height}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate a white background image.")
    parser.add_argument("width", type=int, help="Width of the image in pixels.")
    parser.add_argument("height", type=int, help="Height of the image in pixels.")
    parser.add_argument("--output_base", type=str, default="img", 
                        help="Base output filename (e.g., 'img' for 'img_1920x1080.png').")

    args = parser.parse_args()

    try:
        generate_white_background_image(args.width, args.height, args.output_base)
    except ValueError as e:
        print(f"Error: {e}")