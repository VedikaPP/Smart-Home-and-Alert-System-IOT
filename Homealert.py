"""
IoT Smart Home and Alert System
--------------------------------
Microcontroller : Raspberry Pi Pico W
Language        : MicroPython
Sensors         : IR / PIR Motion Sensor
Alert           : Buzzer + Twilio SMS

NOTE:
- This code uses PLACEHOLDERS for Wi-Fi and Twilio credentials.
- Add your own credentials before running.
"""

from machine import Pin
import time
import network
import urequests

# ==============================
# GPIO PIN CONFIGURATION
# ==============================
IR_SENSOR_PIN = 2        # IR / PIR sensor connected to GP2
BUZZER_PIN = 15          # Buzzer connected to GP15

ir_sensor = Pin(IR_SENSOR_PIN, Pin.IN)
buzzer = Pin(BUZZER_PIN, Pin.OUT)
buzzer.value(0)          # Buzzer OFF initially

# ==============================
# WIFI CONFIGURATION (PLACEHOLDERS)
# ==============================
WIFI_SSID = "YOUR_WIFI_NAME"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

# ==============================
# TWILIO CONFIGURATION (PLACEHOLDERS)
# ==============================
TWILIO_ACCOUNT_SID = "YOUR_TWILIO_ACCOUNT_SID"
TWILIO_AUTH_TOKEN = "YOUR_TWILIO_AUTH_TOKEN"
TWILIO_FROM_NUMBER = "YOUR_TWILIO_PHONE_NUMBER"
TWILIO_TO_NUMBER = "YOUR_MOBILE_NUMBER"

ALERT_MESSAGE = "⚠️ ALERT: Motion detected at your home entrance!"

# ==============================
# WIFI CONNECTION FUNCTION
# ==============================
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("📡 Connecting to Wi-Fi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)

        timeout = 15
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
            print("⏳ Waiting for Wi-Fi connection...")

        if not wlan.isconnected():
            raise RuntimeError("❌ Wi-Fi connection failed")

    print("✅ Wi-Fi connected")
    print("📶 IP Address:", wlan.ifconfig()[0])
    return wlan

# ==============================
# SEND SMS USING TWILIO
# ==============================
def send_sms():
    url = "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json".format(
        TWILIO_ACCOUNT_SID
    )

    data = {
        "From": TWILIO_FROM_NUMBER,
        "To": TWILIO_TO_NUMBER,
        "Body": ALERT_MESSAGE
    }

    print("📨 Sending SMS alert...")
    try:
        response = urequests.post(
            url,
            data=data,
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        )

        if 200 <= response.status_code < 300:
            print("✅ SMS sent successfully")
        else:
            print("❌ SMS failed | Status:", response.status_code)

        response.close()

    except Exception as e:
        print("⚠️ Error sending SMS:", e)

# ==============================
# MAIN PROGRAM LOOP
# ==============================
print("🔐 IoT Smart Home & Alert System Started 🔐")

wifi_connected = False
sms_sent = False

while True:
    motion_detected = ir_sensor.value()
    print("IR Sensor Status:", motion_detected)

    if motion_detected == 1:
        print("🚨 Motion Detected!")
        buzzer.value(1)

        if not wifi_connected:
            try:
                connect_wifi()
                wifi_connected = True
            except Exception as e:
                print("Wi-Fi Error:", e)

        if wifi_connected and not sms_sent:
            send_sms()
            sms_sent = True

    else:
        buzzer.value(0)
        sms_sent = False
        print("✅ No motion detected")

    time.sleep(2)
