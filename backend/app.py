from flask import Flask, request, jsonify
from flask_cors import CORS
from firebase_admin import credentials, initialize_app, storage
import io
import numpy as np
from PIL import Image
import base64
import traceback
from image_processing import crop_image_to_tiles, getNewSize, reconstruct_image
from model_definitions import IMG_SIZE, colorize_image, load_classification_model, load_colorization_models, preprocess_image, postprocess_image, classify_tile

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize Firebase Admin SDK
cred = credentials.Certificate("serviceAccountKey.json")
initialize_app(cred, {
    'storageBucket': 'colorise-9dc75.appspot.com'
})

# Load models
classification_model = load_classification_model()
colorization_models = load_colorization_models({
    0: 'colorization_model_agri.h5',
    1: 'colorization_model_barrenland.h5',
    2: 'colorization_model_grassland.h5',
    3: 'colorization_model_urban.h5',
    4: 'colorization_model_combined.h5'
})
print("@@ models loaded")

@app.route('/colorize', methods=['POST'])
def api_colorize():
    try:
        data = request.json
        image_id = data.get('imageId')
        category = data.get('category')
        
        if not image_id:
            return jsonify({'error': 'Missing imageId'}), 400
        
        if category is None:
            return jsonify({'error': 'Missing category'}), 400
        
        bucket = storage.bucket()
        blob = bucket.blob(f'sar_images/{image_id}')
        image_data = blob.download_as_bytes()
        original_img = Image.open(io.BytesIO(image_data))
        
        # Use the provided category instead of classification
        colorization_model = colorization_models[category]
        
        # Modify colorize_image function call to use the specific model
        final_image = colorize_image_with_model(original_img, colorization_model)
        
        img_byte_arr = io.BytesIO()
        final_image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        base64_image = base64.b64encode(img_byte_arr).decode('utf-8')
        
        return jsonify({
            'colorizedImage': f'data:image/png;base64,{base64_image}',
            'message': 'Image colorized successfully',
            'category': category
        })
    
    except Exception as e:
        print(f"Error during colorization: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

# New function to colorize image with a specific model
def colorize_image_with_model(original_img, colorization_model):
    original_width, original_height = original_img.size
        
    # Check if the image is 512x512 or smaller
    if original_width <= 512 and original_height <= 512:
        # Process the entire image directly
        preprocessed_img = preprocess_image(original_img)
        generated_img = colorization_model.predict(preprocessed_img)
        final_image = postprocess_image(generated_img, (original_width, original_height))
        return Image.open(io.BytesIO(final_image))
    
    # For larger images, proceed with tiling
    new_height, new_width = getNewSize(original_height, original_width)
    resized_img = original_img.resize((new_width, new_height), Image.LANCZOS)
    print(new_height,new_width)
    cropped_images_array = crop_image_to_tiles(resized_img)
    
    # Process tiles
    for i, row in enumerate(cropped_images_array):
        for j, tile in enumerate(row):
            tile_preprocessed = preprocess_image(tile)
            generated_tile = colorization_model.predict(tile_preprocessed)
            colorized_tile = postprocess_image(generated_tile, tile.size)
            cropped_images_array[i][j] = Image.open(io.BytesIO(colorized_tile))
    
    # Reconstruct and resize the image
    reconstructed_image = reconstruct_image(cropped_images_array)
    final_image = reconstructed_image.resize((original_width, original_height), Image.LANCZOS)
    
    return final_image

if __name__ == '__main__':
    app.run(debug=True)