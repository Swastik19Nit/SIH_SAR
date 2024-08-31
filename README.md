# SAR Image Colorization Project

This project provides a web application for colorizing Synthetic Aperture Radar (SAR) images using a deep learning model. It consists of a React frontend and a Flask backend, with Firebase used for image storage.This repository contains the project submission for Smart India Hackathon (SIH) 2024 by Team STARDUST. The project addresses the problem statement "SAR Image Colorization for Comprehensive Insight using Deep Learning Model," aiming to develop an innovative solution for enhancing the interpretability of monochromatic SAR imagery through colorization using deep learning models.

## Features

- Upload SAR images
- Colorize SAR images using a pre-trained deep learning model
- Store original and colorized images in Firebase Storage
- Display colorized images to the user

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Node.js and npm installed for the React frontend
- Python 3.7+ installed for the Flask backend
- A Firebase account and project set up
- The `deionising_model.h5` file (your pre-trained model)

## Setup

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the backend directory with the following content:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=path/to/your/serviceAccountKey.json
   FIREBASE_STORAGE_BUCKET=your-firebase-storage-bucket-name.appspot.com
   ```
   Replace the placeholders with your actual Firebase configuration.

5. Ensure your `deionising_model.h5` file is in the backend directory.

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install the required npm packages:
   ```
   npm install
   ```

3. Create a `.env.local` file in the frontend directory with your Firebase configuration:
   ```
   NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
   NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_auth_domain
   NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
   NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_storage_bucket
   NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id
   NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
   ```

## Running the Application

1. Start the Flask backend:
   ```
   cd backend
   python app.py
   ```
   The backend will start running on `http://localhost:5000`.

2. In a new terminal, start the React frontend:
   ```
   cd frontend
   npm run dev
   ```
   The frontend will start running on `http://localhost:3000`.

3. Open your web browser and navigate to `http://localhost:3000` to use the application.

## Usage

1. Click on the "Choose File" button to select a SAR image from your computer.
2. The image will be uploaded to Firebase Storage.
3. Click the "Colorize Image" button to process the image.
4. Wait for the colorization process to complete.
5. The colorized image will be displayed on the page and stored in Firebase Storage.

## Contributing

Contributions to this project are welcome. Please ensure you follow these steps:

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Open a pull request

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgements

- TensorFlow for the deep learning framework
- Firebase for cloud storage
- React and Next.js for the frontend framework
- Flask for the backend framework
