# app.py
from flask import Flask, request, render_template
import pickle
import numpy as np
import os

# -------------------------
# Initialize Flask app
# -------------------------
app = Flask(__name__, template_folder="templates")

# -------------------------
# Paths to model files
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # current folder
MODEL_DIR = os.path.join(BASE_DIR, "model")

MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
LE_PATH = os.path.join(MODEL_DIR, "label_encoder.pkl")

# -------------------------
# Load model and preprocessors
# -------------------------
try:
    model = pickle.load(open(MODEL_PATH, "rb"))
    scaler = pickle.load(open(SCALER_PATH, "rb"))
    le = pickle.load(open(LE_PATH, "rb"))
except FileNotFoundError as e:
    print(f"Error: {e}")
    print("Make sure model.pkl, scaler.pkl, and label_encoder.pkl exist in the 'model' folder.")
    raise

# -------------------------
# Routes
# -------------------------
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        math = float(request.form.get("math", 0))
        reading = float(request.form.get("reading", 0))
        writing = float(request.form.get("writing", 0))
    except ValueError:
        return render_template(
            "index.html",
            prediction_text="Invalid input: please enter numeric scores."
        )

    # Prepare input
    X = np.array([[math, reading, writing]])
    X_scaled = scaler.transform(X)

    # Predict
    pred_idx = model.predict(X_scaled)[0]
    pred_label = le.inverse_transform([pred_idx])[0]

    return render_template(
        "index.html",
        prediction_text=f"Predicted race/ethnicity: {pred_label}"
    )


# -------------------------
# Run Flask
# -------------------------
if __name__ == "__main__":
    # Use 0.0.0.0 so Heroku or Docker can access
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
