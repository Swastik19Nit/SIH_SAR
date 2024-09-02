import numpy as np
from keras.models import load_model
from PIL import Image
import io
from collections import Counter
from image_processing import crop_image_to_tiles, getNewSize, reconstruct_image

IMG_SIZE = 128

def load_classification_model(weights_path='classification_model.h5'):
    """Load the classification model."""
    model = load_model(weights_path)
    return model

def colorize_image(original_img, classification_model, colorization_models):
    original_width, original_height = original_img.size
    
    # Check if the image is 512x512 or smaller
    if original_width <= 512 and original_height <= 512:
        # Process the entire image directly
        preprocessed_img = preprocess_image(original_img)
        class_id = classify_tile(preprocessed_img, classification_model)
        colorization_model = colorization_models[class_id]
        generated_img = colorization_model.predict(preprocessed_img)
        final_image = postprocess_image(generated_img, (original_width, original_height))
        return Image.open(io.BytesIO(final_image)), class_id
    
    # For larger images, proceed with tiling as before
    new_height, new_width = getNewSize(original_height, original_width)
    resized_img = original_img.resize((new_width, new_height))
    cropped_images_array = crop_image_to_tiles(resized_img)
    
    classifications = []
    preprocessed_tiles = []
    
    # Preprocess and classify tiles
    for row in cropped_images_array:
        for tile in row:
            tile_preprocessed = preprocess_image(tile)
            preprocessed_tiles.append(tile_preprocessed)
            class_id = classify_tile(tile_preprocessed, classification_model)
            classifications.append(class_id)
    
    # Determine the majority class
    class_counts = Counter(classifications)
    majority_class = class_counts.most_common(1)[0][0]
    total_tiles = len(classifications)
    majority_percentage = (class_counts[majority_class] / total_tiles) * 100
    
    # Process tiles
    for i, row in enumerate(cropped_images_array):
        for j, tile in enumerate(row):
            tile_preprocessed = preprocessed_tiles[i * len(row) + j]
            if majority_percentage > 50:
                colorization_model = colorization_models[majority_class]
            else:
                colorization_model = colorization_models[classifications[i * len(row) + j]]
            
            generated_tile = colorization_model.predict(tile_preprocessed)
            colorized_tile = postprocess_image(generated_tile, tile.size)
            cropped_images_array[i][j] = Image.open(io.BytesIO(colorized_tile))
    
    # Reconstruct and resize the image
    reconstructed_image = reconstruct_image(cropped_images_array)
    final_image = reconstructed_image.resize((original_width, original_height), Image.LANCZOS)
    
    return final_image, majority_class if majority_percentage > 50 else None

def classify_tile(tile_preprocessed, classification_model):
    """Classify a preprocessed tile using the classification model."""
    prediction = classification_model.predict(tile_preprocessed)
    class_id = np.argmax(prediction)  # Get the class 
    return class_id

def load_colorization_models(model_paths):
    """Load the colorization models."""
    models = {}
    for class_id, path in model_paths.items():
        models[class_id] = load_model(path)
    return models

def preprocess_image(image):
    """Preprocess image for prediction."""
    img = image.convert('L')
    if img.size[0] > IMG_SIZE or img.size[1] > IMG_SIZE:
        img = img.resize((IMG_SIZE, IMG_SIZE))
    
    img = np.array(img)
    img = img.astype('float32') / 255.0

    if img.shape[0] < IMG_SIZE or img.shape[1] < IMG_SIZE:
        pad_height = max(0, IMG_SIZE - img.shape[0])
        pad_width = max(0, IMG_SIZE - img.shape[1])
        img = np.pad(img, ((0, pad_height), (0, pad_width)), mode='constant', constant_values=0)
    
    img = np.expand_dims(img, axis=-1)
    img = np.expand_dims(img, axis=0)
    return img

def postprocess_image(generated_img, original_size):
    """Postprocess generated image and return as bytes with original size."""
    generated_img = generated_img[0]
    generated_img = (generated_img * 255).astype(np.uint8)
    if generated_img.shape[-1] == 1:
        generated_img = generated_img.squeeze(axis=-1)
    
    img = Image.fromarray(generated_img)
    
    # Crop the image if it was padded during preprocessing
    if img.size[0] > original_size[0] or img.size[1] > original_size[1]:
        img = img.crop((0, 0, original_size[0], original_size[1]))
    
    # Resize only if the current size doesn't match the original size
    if img.size != original_size:
        img = img.resize(original_size, Image.LANCZOS)
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr
