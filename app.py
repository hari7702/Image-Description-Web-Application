from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
from PIL import Image
import io

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Load MobileNetV2 model
model = MobileNetV2(weights="imagenet")

def prepare_image(image, target_size=(224, 224)):
    """
    Preprocess the uploaded image for MobileNetV2.
    """
    if image.mode != "RGB":
        image = image.convert("RGB")  # Ensure 3-channel image
    image = image.resize(target_size)  # Resize to 224x224
    image = np.array(image, dtype=np.float32)
    image = preprocess_input(image)  # Normalize as per MobileNetV2
    image = np.expand_dims(image, axis=0)  # Add batch dimension
    return image

@app.route("/")
def home():
    return "Welcome to the Image Prediction API. Use the /predict endpoint."

@app.route("/predict", methods=["POST"])
def predict():
    """
    Predict the content of the uploaded image.
    """
    if request.method != "POST":
        return jsonify({"error": "Invalid method. Use POST."}), 405  # Handle invalid methods

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded!"}), 400  # Handle missing file

    file = request.files["image"]
    if not file:
        return jsonify({"error": "Invalid image file!"}), 400

    try:
        # Open image and preprocess
        image = Image.open(io.BytesIO(file.read()))
        processed_image = prepare_image(image)

        # Predict using MobileNetV2
        preds = model.predict(processed_image)
        results = decode_predictions(preds, top=3)[0]

        # Format results as JSON
        predictions = [
            {"label": res[1], "confidence": float(res[2])} for res in results
        ]
        return jsonify({"predictions": predictions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
