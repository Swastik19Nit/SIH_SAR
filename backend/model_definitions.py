import numpy as np
from PIL import Image
from keras.models import load_model
from keras.layers import MaxPooling2D, Flatten, Dense
from keras.layers import Conv2D, LeakyReLU, Concatenate, Conv2DTranspose, Input
from keras.models import Sequential, Model
import matplotlib.pyplot as plt
import io
# Define constants
IMG_SIZE = 128

def create_discriminator():
    """Create the discriminator model."""
    model = Sequential([
        Conv2D(32, kernel_size=(7,7), strides=1, input_shape=(IMG_SIZE, IMG_SIZE, 3), activation='relu'),
        Conv2D(32, kernel_size=(7,7), strides=1, activation='relu'),
        MaxPooling2D(),
        Conv2D(64, kernel_size=(5,5), strides=1, activation='relu'),
        Conv2D(64, kernel_size=(5,5), strides=1, activation='relu'),
        MaxPooling2D(),
        Conv2D(128, kernel_size=(3,3), strides=1, activation='relu'),
        Conv2D(128, kernel_size=(3,3), strides=1, activation='relu'),
        MaxPooling2D(),
        Conv2D(256, kernel_size=(3,3), strides=1, activation='relu'),
        Conv2D(256, kernel_size=(3,3), strides=1, activation='relu'),
        MaxPooling2D(),
        Flatten(),
        Dense(128, activation='relu'),
        Dense(64, activation='relu'),
        Dense(32, activation='relu'),
        Dense(16, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    return model

def get_generator_model():
    """Create the generator model."""
    inputs = Input(shape=(IMG_SIZE, IMG_SIZE, 1))

    conv1 = Conv2D(16, kernel_size=(5,5), strides=1)(inputs)
    conv1 = LeakyReLU()(conv1)
    conv1 = Conv2D(32, kernel_size=(3,3), strides=1)(conv1)
    conv1 = LeakyReLU()(conv1)
    conv1 = Conv2D(32, kernel_size=(3,3), strides=1)(conv1)
    conv1 = LeakyReLU()(conv1)

    conv2 = Conv2D(32, kernel_size=(5,5), strides=1)(conv1)
    conv2 = LeakyReLU()(conv2)
    conv2 = Conv2D(64, kernel_size=(3,3), strides=1)(conv2)
    conv2 = LeakyReLU()(conv2)
    conv2 = Conv2D(64, kernel_size=(3,3), strides=1)(conv2)
    conv2 = LeakyReLU()(conv2)

    conv3 = Conv2D(64, kernel_size=(5,5), strides=1)(conv2)
    conv3 = LeakyReLU()(conv3)
    conv3 = Conv2D(128, kernel_size=(3,3), strides=1)(conv3)
    conv3 = LeakyReLU()(conv3)
    conv3 = Conv2D(128, kernel_size=(3,3), strides=1)(conv3)
    conv3 = LeakyReLU()(conv3)

    bottleneck = Conv2D(128, kernel_size=(3,3), strides=1, activation='tanh', padding='same')(conv3)

    concat_1 = Concatenate()([bottleneck, conv3])
    conv_up_3 = Conv2DTranspose(128, kernel_size=(3,3), strides=1, activation='relu')(concat_1)
    conv_up_3 = Conv2DTranspose(128, kernel_size=(3,3), strides=1, activation='relu')(conv_up_3)
    conv_up_3 = Conv2DTranspose(64, kernel_size=(5,5), strides=1, activation='relu')(conv_up_3)

    concat_2 = Concatenate()([conv_up_3, conv2])
    conv_up_2 = Conv2DTranspose(64, kernel_size=(3,3), strides=1, activation='relu')(concat_2)
    conv_up_2 = Conv2DTranspose(64, kernel_size=(3,3), strides=1, activation='relu')(conv_up_2)
    conv_up_2 = Conv2DTranspose(32, kernel_size=(5,5), strides=1, activation='relu')(conv_up_2)

    concat_3 = Concatenate()([conv_up_2, conv1])
    conv_up_1 = Conv2DTranspose(32, kernel_size=(3,3), strides=1, activation='relu')(concat_3)
    conv_up_1 = Conv2DTranspose(32, kernel_size=(3,3), strides=1, activation='relu')(conv_up_1)
    conv_up_1 = Conv2DTranspose(3, kernel_size=(5,5), strides=1, activation='relu')(conv_up_1)

    model = Model(inputs, conv_up_1)
    return model

def load_models(generator_weights_path='generator.weights.h5', discriminator_weights_path='discriminator.weights.h5'):
    """Load the pre-trained models and their weights."""
    generator = get_generator_model()
    discriminator = create_discriminator()

    generator.load_weights(generator_weights_path)
    discriminator.load_weights(discriminator_weights_path)

    return generator, discriminator

def preprocess_image(image):
    """Preprocess image for prediction while maintaining original size."""
    original_size = image.size
    img = image.convert('L')
    img = img.resize((IMG_SIZE, IMG_SIZE))
    img = np.array(img)
    img = img.astype('float32') / 255.0
    img = np.expand_dims(img, axis=-1)
    img = np.expand_dims(img, axis=0)
    return img, original_size

def postprocess_image(generated_img, original_size):
    """Postprocess generated image and return as bytes with original size."""
    generated_img = generated_img[0]
    generated_img = (generated_img * 255).astype(np.uint8)
    img = Image.fromarray(generated_img)
    img = img.resize(original_size, Image.LANCZOS)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr