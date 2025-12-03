from flask import Flask, render_template, request, jsonify
import io
import base64
from PIL import Image
import numpy as np
import tensorflow as tf
import os
import urllib.request
import json

app = Flask(__name__)

# Paths to models (expected to be in repo root)
MODEL_FILES = {
    'basica': 'best_model_UNet_Basica.h5',
    'mejorada': 'best_model_UNet_Mejorada.h5',
    'rmsprop': 'best_model_UNet_RMSprop.h5'
}

models = {}

def load_models():
    for key, path in MODEL_FILES.items():
        if not os.path.exists(path):
            print(f'Model file not found: {path} (will attempt download if MODEL_BASE_URL set): {path}')
            # try to download from MODEL_BASE_URL if provided
            base = os.environ.get('MODEL_BASE_URL')
            if base:
                try:
                    url = base.rstrip('/') + '/' + os.path.basename(path)
                    print(f'Downloading {url} ...')
                    urllib.request.urlretrieve(url, path)
                    print(f'Downloaded {path}')
                except Exception as e:
                    print(f'Failed to download {path} from {base}: {e}')
            else:
                print('No MODEL_BASE_URL provided; skipping download')

        if not os.path.exists(path):
            print(f'Still missing {path}; skipping load')
            continue

        print(f'Trying to load model {key} from {path}...')
        # Try tf.keras first
        try:
            models[key] = tf.keras.models.load_model(path, compile=False)
            print(f'Loaded {key} with tf.keras, input shape: {models[key].input_shape}')
            continue
        except Exception as e_tf:
            print(f'tf.keras failed for {path}: {e_tf}')

        # Try standalone keras if available
        try:
            import keras as standalone_keras
            try:
                models[key] = standalone_keras.models.load_model(path, compile=False)
                print(f'Loaded {key} with standalone keras, input shape: {models[key].input_shape}')
                continue
            except Exception as e_keras:
                print(f'standalone keras failed for {path}: {e_keras}')
        except Exception:
            print('standalone keras not available')

        # As a last resort, try to reconstruct the model from `model_config` stored inside the HDF5
        try:
            import h5py, json
            with h5py.File(path, 'r') as f:
                mc = None
                if 'model_config' in f.attrs:
                    mc = f.attrs['model_config']
                elif 'model_config' in f:
                    mc = f['model_config'][()]

                if mc is not None:
                    mc_str = mc.decode() if isinstance(mc, (bytes, bytearray)) else str(mc)
                    # quick compatibility fix: replace 'batch_shape' with 'batch_input_shape'
                    mc_str_fixed = mc_str.replace('"batch_shape"', '"batch_input_shape"')
                    try:
                        cfg = json.loads(mc_str_fixed)
                        # if the JSON has the top-level Functional wrapper, get the 'config' or dump back to json
                        if isinstance(cfg, dict) and 'config' in cfg:
                            model_json = json.dumps(cfg)
                        else:
                            model_json = mc_str_fixed

                        model = tf.keras.models.model_from_json(model_json)
                        # try to load weights from the .h5
                        try:
                            model.load_weights(path)
                            models[key] = model
                            print(f'Loaded {key} by reconstructing from model_config and loading weights')
                            continue
                        except Exception as e_w:
                            print(f'Failed to load weights for reconstructed model {path}: {e_w}')
                    except Exception as e_json:
                        print(f'Failed to reconstruct model from model_config for {path}: {e_json}')
        except Exception as e_last:
            print(f'Last-resort reconstruction failed for {path}: {e_last}')

        print(f'Error loading {path}: model not loaded')

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
