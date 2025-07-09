import time                   # Allows use of time.sleep() for delays
from mqtt import MQTTClient   # For use of MQTT protocol to talk to Adafruit IO
import machine                # Interfaces with hardware components
import micropython            # Needed to run any MicroPython code
from machine import Pin       # Define pin
import keys                   # Contain all keys used here
import wifiConnection         # Contains functions to connect/disconnect from WiFi
import urequests
import json

# BEGIN SETTINGS
# These need to be change to suit your environment
MEASURE_INTERVAL = 5000    # milliseconds
last_value_sent_ticks = 0  # milliseconds
led = Pin("LED", Pin.OUT)   # led pin initialization for Raspberry Pi Pico W
last_read_value = -1

pin_input = Pin(27, Pin.IN)

# IP of the device running the Flask server
SERVER_IP = 'x.x.x.x'  # Replace with your device's IP address
SERVER_PORT = 5000
ENDPOINT = f"http://{SERVER_IP}:{SERVER_PORT}/door"

# Callback Function to respond to messages from Adafruit IO
def sub_cb(topic, msg):          # sub_cb means "callback subroutine"
    print((topic, msg))          # Outputs the message that was received. Debugging use.
    if msg == b"ON":             # If message says "ON" ...
        led.on()                 # ... then LED on
    elif msg == b"OFF":          # If message says "OFF" ...
        led.off()                # ... then LED off
    else:                        # If any other message is received ...
        print("Unknown message") # ... do nothing but output that it happened.

def get_value():
    return pin_input.value()

def send_trigger():
    try:
        print("Sending trigger to server...")
        res = urequests.post(ENDPOINT, json={"status": "open"})
        print("Server response:", res.text)
        res.close()
    except Exception as e:
        print("Error sending trigger:", e)

# Function to publish sensor data to Adafruit IO MQTT server at fixed interval
def send_value():
    global last_value_sent_ticks
    global MEASURE_INTERVAL
    global last_read_value

    if ((time.ticks_ms() - last_value_sent_ticks) < MEASURE_INTERVAL):
        return; # Too soon since last one sent.

    door_status = get_value()
    if last_read_value != door_status:
        last_read_value = door_status
        print("Publishing: {0} to {1} ... ".format(door_status, keys.AIO_MAGNET_FEED), end='')
        try:
            client.publish(topic=keys.AIO_MAGNET_FEED, msg=str(door_status))
            print("DONE")
        except Exception as e:
            print("FAILED")
        finally:
            last_value_sent_ticks = time.ticks_ms()
        if door_status == 1:
            send_trigger()

# Try WiFi Connection
try:
    ip = wifiConnection.connect()
except KeyboardInterrupt:
    print("Keyboard interrupt")

# Use the MQTT protocol to connect to Adafruit IO
client = MQTTClient(keys.AIO_CLIENT_ID, keys.AIO_SERVER, keys.AIO_PORT, keys.AIO_USER, keys.AIO_KEY)

# Subscribed messages will be delivered to this callback
client.set_callback(sub_cb)
client.connect()
client.subscribe(keys.AIO_LIGHTS_FEED)
print("Connected to %s, subscribed to %s topic" % (keys.AIO_SERVER, keys.AIO_LIGHTS_FEED))

try:                      # Code between try: and finally: may cause an error
                          # so ensure the client disconnects the server if
                          # that happens.
    while 1:              # Repeat this loop forever
        client.check_msg()# Action a message if one is received. Non-blocking.
        send_value()     # Send a 0 or 1 depending on door status to Adafruit IO if it's time.
finally:                  # If an exception is thrown ...
    client.disconnect()   # ... disconnect the client and clean up.
    client = None
    wifiConnection.disconnect()
    print("Disconnected from Adafruit IO.")
