from flask import Flask, request
import requests
from requests.auth import HTTPDigestAuth
import datetime
import time

app = Flask(__name__)

# Camera config
CAMERA_USER = "root" #Replace if you have changed username
CAMERA_PASS = "password" #Replace with your password for the camera
IP_CAMERA_URL = "http://x.x.x.x/axis-cgi/jpg/image.cgi" #Replace with the ip address of the camera

# Discord webhook
DISCORD_WEBHOOK_URL = "Your discord webhook"

@app.route('/door', methods=['POST'])
def door_opened():
    print("Door trigger received!")
    time.sleep(2)  # Optional: allow camera to stabilize

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        image_response = requests.get(
            IP_CAMERA_URL,
            auth=HTTPDigestAuth(CAMERA_USER, CAMERA_PASS)
        )

        if image_response.status_code != 200:
            print(f"Camera response: {image_response.status_code}")
            return {"error": "Failed to fetch image"}, 500

        files = {
            "file": (f"snapshot_{timestamp}.jpg", image_response.content)
        }

        data = {"content": "🚪 Door opened!"}
        requests.post(DISCORD_WEBHOOK_URL, data=data, files=files)

        return {"status": "ok"}

    except Exception as e:
        print("Exception:", e)
        return {"error": "Exception during image fetch"}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
