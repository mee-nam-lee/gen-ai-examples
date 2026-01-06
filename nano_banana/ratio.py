from PIL import Image
import os

def resize_image_without_cropping(input_image_path, target_width, target_height, output_filename=None):
    """
    Resizes an image to the target dimensions without cropping. The aspect ratio might change.

    Args:
        input_image_path (str): Path to the input image file.
        target_width (int): The desired width of the output image.
        target_height (int): The desired height of the output image.
        output_filename (str, optional): The name of the output image file. 
                                         If None, a default name will be generated.
    """
    if not os.path.exists(input_image_path):
        raise FileNotFoundError(f"Input image not found at {input_image_path}")

    try:
        img = Image.open(input_image_path)
    except Exception as e:
        raise ValueError(f"Could not open image file: {e}")

    # Resize the image
    resized_img = img.resize((target_width, target_height), Image.LANCZOS)

    if output_filename is None:
        base, ext = os.path.splitext(os.path.basename(input_image_path))
        output_filename = f"{base}_resized_{target_width}x{target_height}{ext}"

    resized_img.save(output_filename)
    print(f"Resized image saved to {output_filename} with dimensions {target_width}x{target_height}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Resize an image to specified dimensions without cropping.")
    parser.add_argument("input_path", type=str, help="Path to the input image file.")
    parser.add_argument("target_width", type=int, help="Desired width of the output image in pixels.")
    parser.add_argument("target_height", type=int, help="Desired height of the output image in pixels.")
    parser.add_argument("--output", type=str, default=None, 
                        help="Optional: Output filename. If not provided, a default name will be generated.")

    args = parser.parse_args()

    try:
        resize_image_without_cropping(args.input_path, args.target_width, args.target_height, args.output)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
