from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import torch
import shutil
import os
from pathlib import Path
from datetime import datetime
from PIL import Image
import io
import paho.mqtt.client as mqtt
import json
from dotenv import load_dotenv

app = FastAPI()

# Load environment variables from the .env file
load_dotenv()

# === CONFIGURATION ===
MODEL_PATH = os.getenv("MODEL_PATH", "./best.pt")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", 0.10))

# === MQTT CONFIGURATION ===
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC")
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASS = os.getenv("MQTT_PASS")

# === LOAD TRAINED MODEL ===
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_PATH).to(device)
model.conf = CONFIDENCE_THRESHOLD

# === DIRECTORY FOR POSITIVE DETECTIONS ===
detect_dir = Path("detections")
detect_dir.mkdir(exist_ok=True)

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        log_event("Successfully connected to MQTT broker.")
    else:
        log_event(f"MQTT connection failed. Code: {rc}")

mqtt_client.on_connect = on_connect
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

def log_event(message: str):
    """Log events with a timestamp."""
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] {message}")

# === ENDPOINT ===
@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    """Endpoint to detect objects in an uploaded image."""
    try:
        timestamp = datetime.now().isoformat()

        # Read the uploaded image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')

        # Perform inference
        results = model(image, size=1280)  # Size 1280 for better accuracy
        detections = results.pred[0]  # tensor Nx6

        detected = False
        if detections is not None and len(detections) > 0:
            for det in detections:
                cls_id = int(det[5])
                class_name = model.names[cls_id]
                if class_name.lower() == "cockroach":
                    detected = True
                    break

        if detected:
            log_event(f"COCKROACH detected in {file.filename} ({len(detections)} objects)")

            # Save the image
            output_path = detect_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
            with open(output_path, "wb") as f:
                f.write(contents)

            # Draw bounding boxes and save the rendered image
            results.render()  # modifies results.imgs with drawn boxes
            rendered_img = Image.fromarray(results.ims[0])
            render_path = detect_dir / f"detected_{timestamp}.jpg"
            rendered_img.save(render_path)

            # Publish MQTT message
            mqtt_payload = json.dumps({"detected": True, "timestamp": datetime.now().isoformat()})
            result = mqtt_client.publish(MQTT_TOPIC, mqtt_payload)
            status = result[0]
            if status == 0:
                log_event(f"MQTT message successfully sent to {MQTT_TOPIC}")
            else:
                log_event(f"Error sending MQTT message: code {status}")

            return JSONResponse(content={"detected": True})
        else:
            log_event(f"No cockroaches detected in {file.filename}")
            return JSONResponse(content={"detected": False})

    except Exception as e:
        log_event(f"Error processing image: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
