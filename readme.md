# 🦗 Roach Detector API

This project provides a FastAPI server that uses a YOLOv5 model trained to detect cockroaches in images. It is part of a larger IR-camera surveillance system powered by Raspberry Pi.

## 🔍 What does it do?

- Receives images via HTTP (`/detect` endpoint)
- Runs inference using a trained YOLOv5 model (`best.pt`)
- If a cockroach is detected:
  - Saves the image with bounding boxes at `/detection` folder
  - Sends an MQTT message
- If no detection, discards the image

## 📁 Project Structure

```
roach-detector/
├── app.py               # FastAPI server with loaded trained model
├── best.pt              # Trained YOLOv5 model
├── requirements.txt     # Python environment dependencies
├── detections
├── .gitignore
└── README.md
```

## 🚀 How to Run

1. Clone the repository:

```bash
git clone
cd roach-detector
```

2. Set up virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn torch torchvision pillow python-multipart paho-mqtt python-dotenv
pip install -r requirements.txt
```

3. Make sure YOLOv5 repo is available locally:

```bash
git clone https://github.com/ultralytics/yolov5.git
```

4. Configure your `.env`. You have an example to do it.

# Start server
uvicorn app:app --reload

## Start server running behind the windows (WSL side)
- uvicorn app:app --host 0.0.0.0 --port 8000
- we need for that NAT + port forwarding
    - powershell -> netsh interface portproxy add v4tov4 listenport=8000 listenaddress=0.0.0.0 connectport=8000 connectaddress=<IP_WSL>  (using eth0 )


## 📡 MQTT Integration (optional)

When detection is positive, a JSON message is sent over MQTT:

```json
{
  "detected": true,
  "timestamp": "2025-07-13T23:41:00.123"
}
```

## 🧠 Requirements

- Python 3.8+
- PyTorch
- YOLOv5 (local clone)
- `best.pt` trained model
- A local system with Home Assistant or similar with an opened MQTT broker to receive the alert. 
- This alert should be forward to a push notification in your smartphone through HA system.
- A system like a Raspberry or similar that it should be able to send captured images with a camera.
- LAN/WAN network 


🖼️ watchtower_sender_image

This directory contains a mock Raspberry Pi sender used for testing the inference server.

🔧 What it does

- Watches a local folder for images
- Picks a random image every few seconds
- Sends it to the FastAPI server via HTTP POST
- Intended to simulate how the Raspberry Pi will work in the final setup

## 📁 Project Structure

watchtower_sender_image/
├── capture_images_and_send.py  # Script to send images
├── images/                     # Directory with mock images
├── Dockerfile                  # Docker container definition
└── docker-compose.yaml         # For running the sender container

This mock is useful for testing the full flow if you don't have a camera. 

##  🚀 Eexcution of docker container
docker-compose up --build

