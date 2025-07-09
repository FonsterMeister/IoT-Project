import ubinascii              # Conversions between binary data and various encodings
import machine                # To Generate a unique id from processor

# Wireless network
WIFI_SSID =  "Your SSID"
WIFI_PASS = "Your password"

# Adafruit IO (AIO) configuration
AIO_SERVER = "io.adafruit.com"
AIO_PORT = 1883
AIO_USER = "username"
AIO_KEY = "adafruit key"
AIO_CLIENT_ID = ubinascii.hexlify(machine.unique_id())  # Can be anything
AIO_LIGHTS_FEED = "{username}/feeds/lights"
AIO_MAGNET_FEED = "{username}/feeds/magnet"
AIO_CAMERA_FEED = "{username}/feeds/picture"
