"use client"
import React, { useState, useRef } from 'react';
import { storage } from '@/utils/firebase';
import { ref, uploadBytes, getDownloadURL } from 'firebase/storage';
import { v4 as uuidv4 } from 'uuid';

const SARImageUpload: React.FC = () => {
  const [originalImage, setOriginalImage] = useState<string | null>(null);
  const [colorizedImage, setColorizedImage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [imageId, setImageId] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setIsLoading(true);
      const newImageId = uuidv4();
      setImageId(newImageId);
      const storageRef = ref(storage, `sar_images/${newImageId}`);

      try {
        await uploadBytes(storageRef, file);
        const downloadURL = await getDownloadURL(storageRef);
        setOriginalImage(downloadURL);
      } catch (error) {
        console.error("Error uploading image: ", error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleColorize = async () => {
    if (!originalImage || !imageId) {
      console.error('Image URL or ID is missing');
      return;
    }
  
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:5000/colorize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ imageUrl: originalImage, imageId: imageId }),
      });
  
      if (!response.ok) {
        throw new Error('Colorization failed');
      }
  
      const data = await response.json();
      console.log(data);
      if (data.colorizedImage) {
        setColorizedImage(data.colorizedImage);
      } else {
        console.error('No colorizedImage found in the response');
        throw new Error('No colorizedImage found in the response');
      }
    } catch (error) {
      console.error("Error during colorization: ", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="max-w-5xl mx-auto p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl shadow-xl">
      <h1 className="text-3xl font-extrabold mb-8 text-center text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-blue-400">
        SAR Image Colorization
      </h1>

      <div
        className="border-dashed border-4 border-blue-300 rounded-lg p-8 flex flex-col items-center justify-center text-center mb-8 cursor-pointer hover:border-blue-400 transition duration-300 ease-in-out"
        onClick={handleClick}
      >
        <input
          type="file"
          accept="image/*"
          onChange={handleImageUpload}
          className="hidden"
          ref={fileInputRef}
        />
        <p className="text-blue-600 font-medium mb-4">Drag & drop an image here, or click to select a file</p>
        <button
          className="bg-blue-600 text-white px-5 py-3 rounded-full font-semibold shadow-lg hover:bg-blue-700 transition duration-300 ease-in-out"
        >
          Choose File
        </button>
      </div>

      {originalImage && (
        <div className="mb-8">
          <h2 className="text-xl font-bold mb-4 text-center text-blue-600">Original Image</h2>
          <div className="flex justify-center">
            <img src={originalImage} alt="Original SAR" className="max-w-full h-auto rounded-lg shadow-xl transform hover:scale-105 transition duration-300 ease-in-out" />
          </div>
        </div>
      )}

      {originalImage && !colorizedImage && (
        <div className="flex justify-center mb-8">
          <button
            onClick={handleColorize}
            disabled={isLoading}
            className="bg-gradient-to-r from-green-400 to-green-500 text-white px-8 py-4 rounded-full font-bold shadow-lg hover:from-green-500 hover:to-green-600 transition duration-300 ease-in-out disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Processing...' : 'Colorize Image'}
          </button>
        </div>
      )}

      {colorizedImage && (
        <div className="mb-8">
          <h2 className="text-xl font-bold mb-4 text-center text-green-600">Colorized Image</h2>
          <div className="flex justify-center">
            <img src={colorizedImage} alt="Colorized SAR" className="max-w-full h-auto rounded-lg shadow-xl transform hover:scale-105 transition duration-300 ease-in-out" />
          </div>
        </div>
      )}
    </div>
  );
};

export default SARImageUpload;