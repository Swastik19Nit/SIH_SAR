from PIL import Image

def getNewSize(height, width):
    """
    Calculate the new size ensuring dimensions are multiples of 128,
    while maintaining the aspect ratio as closely as possible.
    """
    # Calculate the aspect ratio
    aspect_ratio = width / height

    # Calculate new dimensions that are multiples of 128
    new_height = ((height + 127) // 128) * 128
    new_width = ((width + 127) // 128) * 128

    # Adjust dimensions to maintain aspect ratio as closely as possible
    if new_width / new_height > aspect_ratio:
        # Too wide, adjust width
        new_width = int(new_height * aspect_ratio)
        new_width = ((new_width + 127) // 128) * 128
    elif new_width / new_height < aspect_ratio:
        # Too tall, adjust height
        new_height = int(new_width / aspect_ratio)
        new_height = ((new_height + 127) // 128) * 128

    return new_height, new_width

def crop_image_to_tiles(image):
    """Crop the image into 128x128 tiles."""
    width, height = image.size
    tile_width, tile_height = 128, 128

    x_tiles = width // tile_width
    y_tiles = height // tile_height

    cropped_images_array = []

    for i in range(x_tiles):
        row = []
        for j in range(y_tiles):
            left = i * tile_width
            upper = j * tile_height
            right = left + tile_width
            lower = upper + tile_height

            cropped_image = image.crop((left, upper, right, lower))
            row.append(cropped_image)

        cropped_images_array.append(row)

    return cropped_images_array

def reconstruct_image(cropped_images_array):
    """Reconstruct the image from cropped 128x128 tiles."""
    x_tiles = len(cropped_images_array)
    y_tiles = len(cropped_images_array[0])

    tile_width, tile_height = cropped_images_array[0][0].size
    final_image = Image.new('RGB', (x_tiles * tile_width, y_tiles * tile_height))

    for i in range(x_tiles):
        for j in range(y_tiles):
            left = i * tile_width
            upper = j * tile_height
            final_image.paste(cropped_images_array[i][j], (left, upper))

    return final_image