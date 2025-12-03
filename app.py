from flask import Flask, render_template, request, jsonify
import io
import base64
from PIL import Image
import numpy as np
import tensorflow as tf
from tensorflow import keras
import os
import sys

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

# Paths to models (expected to be in repo root)
MODEL_FILES = {
    'basica': 'best_model_UNet_Basica.h5',
    'mejorada': 'best_model_UNet_Mejorada.h5',
    'rmsprop': 'best_model_UNet_RMSprop.h5'
}

models = {}

def build_unet_model(input_shape=(128, 128, 1)):
    """Construye la arquitectura U-Net usada para todos los modelos"""
    inputs = keras.Input(shape=input_shape)
    
    # Encoder
    c1 = keras.layers.Conv2D(64, (3, 3), padding='same')(inputs)
    c1 = keras.layers.BatchNormalization()(c1)
    c1 = keras.layers.Activation('relu')(c1)
    c1 = keras.layers.Conv2D(64, (3, 3), padding='same')(c1)
    c1 = keras.layers.BatchNormalization()(c1)
    c1 = keras.layers.Activation('relu')(c1)
    p1 = keras.layers.MaxPooling2D((2, 2))(c1)
    
    c2 = keras.layers.Conv2D(128, (3, 3), padding='same')(p1)
    c2 = keras.layers.BatchNormalization()(c2)
    c2 = keras.layers.Activation('relu')(c2)
    c2 = keras.layers.Conv2D(128, (3, 3), padding='same')(c2)
    c2 = keras.layers.BatchNormalization()(c2)
    c2 = keras.layers.Activation('relu')(c2)
    p2 = keras.layers.MaxPooling2D((2, 2))(c2)
    
    c3 = keras.layers.Conv2D(256, (3, 3), padding='same')(p2)
    c3 = keras.layers.BatchNormalization()(c3)
    c3 = keras.layers.Activation('relu')(c3)
    c3 = keras.layers.Conv2D(256, (3, 3), padding='same')(c3)
    c3 = keras.layers.BatchNormalization()(c3)
    c3 = keras.layers.Activation('relu')(c3)
    p3 = keras.layers.MaxPooling2D((2, 2))(c3)
    
    # Bottleneck
    c4 = keras.layers.Conv2D(512, (3, 3), padding='same')(p3)
    c4 = keras.layers.BatchNormalization()(c4)
    c4 = keras.layers.Activation('relu')(c4)
    c4 = keras.layers.Dropout(0.3)(c4)
    c4 = keras.layers.Conv2D(512, (3, 3), padding='same')(c4)
    c4 = keras.layers.BatchNormalization()(c4)
    c4 = keras.layers.Activation('relu')(c4)
    
    # Decoder
    u5 = keras.layers.Conv2DTranspose(256, (2, 2), strides=(2, 2), padding='same')(c4)
    u5 = keras.layers.concatenate([u5, c3])
    c5 = keras.layers.Conv2D(256, (3, 3), padding='same')(u5)
    c5 = keras.layers.BatchNormalization()(c5)
    c5 = keras.layers.Activation('relu')(c5)
    c5 = keras.layers.Conv2D(256, (3, 3), padding='same')(c5)
    c5 = keras.layers.BatchNormalization()(c5)
    c5 = keras.layers.Activation('relu')(c5)
    
    u6 = keras.layers.Conv2DTranspose(128, (2, 2), strides=(2, 2), padding='same')(c5)
    u6 = keras.layers.concatenate([u6, c2])
    c6 = keras.layers.Conv2D(128, (3, 3), padding='same')(u6)
    c6 = keras.layers.BatchNormalization()(c6)
    c6 = keras.layers.Activation('relu')(c6)
    c6 = keras.layers.Conv2D(128, (3, 3), padding='same')(c6)
    c6 = keras.layers.BatchNormalization()(c6)
    c6 = keras.layers.Activation('relu')(c6)
    
    u7 = keras.layers.Conv2DTranspose(64, (2, 2), strides=(2, 2), padding='same')(c6)
    u7 = keras.layers.concatenate([u7, c1])
    c7 = keras.layers.Conv2D(64, (3, 3), padding='same')(u7)
    c7 = keras.layers.BatchNormalization()(c7)
    c7 = keras.layers.Activation('relu')(c7)
    c7 = keras.layers.Conv2D(64, (3, 3), padding='same')(c7)
    c7 = keras.layers.BatchNormalization()(c7)
    c7 = keras.layers.Activation('relu')(c7)
    
    # Output
    outputs = keras.layers.Conv2D(3, (1, 1), activation='sigmoid')(c7)
    
    model = keras.Model(inputs=[inputs], outputs=[outputs])
    return model

def load_models():
    for key, path in MODEL_FILES.items():
        if not os.path.exists(path):
            print(f'Model file not found: {path}')
            continue

        print(f'Loading model {key} from {path}...')
        try:
            # Try direct load first
            models[key] = keras.models.load_model(path, compile=False)
            print(f'✓ Loaded {key} successfully')
        except Exception as e1:
            print(f'Direct load failed, trying weights-only approach...')
            try:
                # Build U-Net and try to load weights
                model = build_unet_model()
                model.load_weights(path, by_name=True, skip_mismatch=True)
                models[key] = model
                print(f'✓ Loaded {key} successfully (weights transfer)')
            except Exception as e2:
                print(f'✗ Could not load {key}: Incompatible format')
                # Don't crash - just skip this model
                continue

def get_model_input_size(model):
    # Try to determine (height, width)
    shape = model.input_shape
    # shape can be (None, H, W, C) or similar
    if shape is None:
        return (256, 256)
    if len(shape) >= 3 and shape[1] is not None and shape[2] is not None:
        return (int(shape[1]), int(shape[2]))
    return (256, 256)

def preprocess_image(pil_img, target_size):
    # Convert to grayscale if not already
    img = pil_img.convert('L')
    img = img.resize(target_size, Image.BICUBIC)
    arr = np.array(img).astype('float32') / 255.0
    # add channel dim
    arr = np.expand_dims(arr, axis=-1)
    arr = np.expand_dims(arr, axis=0)
    return arr

def postprocess_output(output):
    # output expected shape (1,H,W,3) with values [0,1] or [0,255]
    out = np.squeeze(output, axis=0)
    if out.max() <= 1.01:
        out = np.clip(out * 255.0, 0, 255).astype('uint8')
    else:
        out = np.clip(out, 0, 255).astype('uint8')
    img = Image.fromarray(out)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode('utf-8')
    return 'data:image/png;base64,' + b64

@app.route('/')
def index():
    # report which models were successfully loaded
    available = {k: (k in models) for k in MODEL_FILES.keys()}
    return render_template('index.html', models=available)

@app.route('/colorize', methods=['POST'])
def colorize():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    file = request.files['image']
    model_key = request.form.get('model', 'rmsprop')
    if model_key not in models:
        return jsonify({'error': f'Model {model_key} not available'}), 400

    try:
        pil_img = Image.open(file.stream).convert('RGB')
    except Exception as e:
        return jsonify({'error': f'Invalid image: {e}'}), 400

    model = models[model_key]
    target_size = get_model_input_size(model)
    x = preprocess_image(pil_img, target_size)

    # Run prediction
    try:
        pred = model.predict(x)
    except Exception as e:
        return jsonify({'error': f'Inference failed: {e}'}), 500

    img_b64 = postprocess_output(pred)
    return jsonify({'image': img_b64})

if __name__ == '__main__':
    load_models()
    # development server; production on Render should use gunicorn
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
