from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import cv2
from PIL import Image
import tensorflow as tf
import requests
from io import BytesIO
import firebase_admin
from firebase_admin import credentials, storage
import tempfile
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize Firebase Admin SDK
cred = credentials.Certificate(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
firebase_admin.initialize_app(cred, {
    'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET')
})
print("hello world!")
# Load your model once when the app starts
model = tf.keras.models.load_model('deionising_model.h5')

def preprocess_img(image):
    img = cv2.resize(image, (128, 128))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype('float32') / 255.0
    img = np.expand_dims(img, axis=0)
    return img

def postprocess_img(image_array):
    image_array = np.squeeze(image_array)
    image_array = image_array * 255.0
    image_array = np.clip(image_array, 0, 255).astype(np.uint8)
    restored_image = Image.fromarray(image_array)
    return restored_image

@app.route('/colorize', methods=['POST'])
def colorize():
    data = request.json
    if not data or 'imageUrl' not in data or 'imageId' not in data:
        return jsonify({"error": "Invalid input"}), 400

    original_image_url = data['imageUrl']
    print(original_image_url)
    image_id = data['imageId']
    print(image_id)

    # Download the image
    response = requests.get(original_image_url)
    image = Image.open(BytesIO(response.content))
    image = np.array(image)

    # Preprocess the image
    preprocessed_image = preprocess_img(image)

    # Denoise the image using the model
    denoised_image_array = model.predict(preprocessed_image)

    # Postprocess the image
    restored_image = postprocess_img(denoised_image_array)

    # Save the colorized image to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        restored_image.save(temp_file, format="PNG")
        temp_file_path = temp_file.name

    try:
        # Upload the colorized image to Firebase Storage
        bucket = storage.bucket()
        colorized_blob = bucket.blob(f"colorized_sar_images/{image_id}")
        colorized_blob.upload_from_filename(temp_file_path)

        # Make the blob publicly accessible
        colorized_blob.make_public()
        colorized_image_url = colorized_blob.public_url

        return jsonify({"colorizedImageUrl": colorized_image_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        
        import os
        os.unlink(temp_file_path)

if __name__ == '__main__':
    app.run(debug=True)