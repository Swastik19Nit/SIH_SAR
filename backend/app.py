from flask import Flask, request, jsonify
from flask_cors import CORS
from firebase_admin import credentials, initialize_app, storage
import io
from model_definitions import load_models, preprocess_image, postprocess_image
from PIL import Image
import base64

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize Firebase Admin SDK
cred = credentials.Certificate(process.ENV.GOOGLE_APPLICATION_CREDENTIALS)
initialize_app(cred, {
    'storageBucket': FIREBASE_STORAGE_BUCKET
})

# Load models
generator, discriminator = load_models()
print("@@ models loaded")

@app.route('/colorize', methods=['POST'])
def api_colorize():
    if request.method != 'POST':
        return jsonify({'error': 'Method not allowed'}), 405

    data = request.json
    image_url = data.get('imageUrl')
    image_id = data.get('imageId')

    if not image_url or not image_id:
        return jsonify({'error': 'Missing imageUrl or imageId'}), 400

    try:
        # Download the image from Firebase
        print(f"Downloading image from Firebase: sar_images/{image_id}")
        bucket = storage.bucket()
        blob = bucket.blob(f'sar_images/{image_id}')
        image_data = blob.download_as_bytes()

        # Convert to image
        print("Converting image data to PIL image")
        img = Image.open(io.BytesIO(image_data))
        
        # Preprocess image
        print("Preprocessing image for model input")
        preprocessed_img, original_size = preprocess_image(img)

        # Generate colorized image
        print("Running model prediction")
        generated_image = generator.predict(preprocessed_img)
        
        # Postprocess image
        print("Postprocessing image")
        colorized_image_bytes = postprocess_image(generated_image, original_size)

        # Encode the image as base64
        base64_image = base64.b64encode(colorized_image_bytes).decode('utf-8')

        print("Colorized image successfully processed")
        return jsonify({
            'colorizedImage': f'data:image/png;base64,{base64_image}',
            'message': 'Image colorized successfully'
        })

    except Exception as e:
        print(f"Error during colorization: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)