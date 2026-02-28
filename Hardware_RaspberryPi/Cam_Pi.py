import subprocess
import requests
import time
import logging
import os
import RPi.GPIO as GPIO

# ================= CONFIG =================
SERVER_API = "http://IP_SERVER/backend/api/detections?image"
PB_URL = "PATH-FOR_DATABASE"

LED_DETECTION = 23
LED_SUCCESS = 25
TRIG = 22
ECHO = 27

# ระยะตรวจจับหลัก
MAX_DISTANCE = 15.0  
# ระยะเผื่อ (Hysteresis) ต้องห่างเกินค่านี้ถึงจะรีเซ็ตระบบ เพื่อป้องกันค่าแกว่ง
CLEAR_DISTANCE = 25.0 
TEMP_IMAGE = "/tmp/frame.jpg"

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_DETECTION, GPIO.OUT)
GPIO.setup(LED_SUCCESS, GPIO.OUT)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

GPIO.output(LED_DETECTION, GPIO.LOW)
GPIO.output(LED_SUCCESS, GPIO.LOW)

def update_hc04_status(status_value):
    """อัปเดตสถานะ Hc04 ไปยัง API"""
    try:
        data = {"Hc04": status_value}
        response = requests.patch(PB_URL, json=data, timeout=5)
        print(f"📡 API Status Updated: {status_value} (HTTP {response.status_code})")
    except Exception as e:
        print(f"❌ Failed to update API status: {e}")

def get_distance():
    """วัดระยะทางแบบหาค่าเฉลี่ย 3 ครั้งเพื่อความแม่นยำ"""
    measurements = []
    for _ in range(3):
        try:
            GPIO.output(TRIG, True)
            time.sleep(0.00001)
            GPIO.output(TRIG, False)
            start_time = time.time()
            stop_time = time.time()
            while GPIO.input(ECHO) == 0:
                start_time = time.time()
            while GPIO.input(ECHO) == 1:
                stop_time = time.time()
            distance = ((stop_time - start_time) * 34300) / 2
            measurements.append(distance)
            time.sleep(0.02)
        except:
            measurements.append(999)
    
    # ส่งค่าที่น้อยที่สุดกลับไป (หรือใช้ sum(measurements)/3)
    return min(measurements)

def capture_and_send():
    """ถ่ายภาพและส่งไฟล์โดยไม่แสดง Log กล้อง"""
    print("📸 Capturing image...")
    subprocess.run([
        "rpicam-still", "-o", TEMP_IMAGE,
        "--width", "1280", "--height", "720",
        "--quality", "95", "--nopreview"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) 

    if os.path.exists(TEMP_IMAGE):
        with open(TEMP_IMAGE, "rb") as f:
            image_bytes = f.read()
        os.remove(TEMP_IMAGE)
        
        try:
            res = requests.post(
                SERVER_API,
                files={"image": ("frame.jpg", image_bytes, "image/jpeg")},
                timeout=10
            )
            if res.status_code == 200:
                GPIO.output(LED_SUCCESS, GPIO.HIGH)
                time.sleep(1)
                GPIO.output(LED_SUCCESS, GPIO.LOW)
                return True
        except Exception as e:
            print(f"❌ Send image failed: {e}")
    return False

print(f"==== System Ready (Stable Mode: < {MAX_DISTANCE} cm) ====")


try:
    has_sent = False 
    current_status = None 

    while True:
        dist = get_distance()
        
        # เงื่อนไขการตรวจจับ (ต้องต่ำกว่า 15 ซม.)
        is_detected = dist < MAX_DISTANCE
        
        # อัปเดตสถานะ API และ LED
        status_to_send = 1 if is_detected else 0
        
        # กรณีวัตถุออกไป: ต้องห่างเกิน CLEAR_DISTANCE (25 ซม.) ถึงจะส่ง 0 และรีเซ็ต
        if not is_detected and dist > CLEAR_DISTANCE:
            if current_status != 0:
                update_hc04_status(0)
                current_status = 0
                GPIO.output(LED_DETECTION, GPIO.LOW)
                if has_sent:
                    print(f"✨ Range cleared ({dist:.2f} cm). System reset.")
                has_sent = False
        
        # กรณีวัตถุเข้ามา: ต่ำกว่า 15 ซม.
        elif is_detected:
            if current_status != 1:
                update_hc04_status(1)
                current_status = 1
                GPIO.output(LED_DETECTION, GPIO.HIGH)
                print(f"🚨 Object detected at {dist:.2f} cm")

            if not has_sent:
                print(f"⏳ Waiting 2s for stability...")
                time.sleep(2)
                # เช็คซ้ำอีกรอบหลังรอ 2 วินาทีเพื่อให้มั่นใจว่ายังนิ่งอยู่
                if get_distance() < MAX_DISTANCE:
                    if capture_and_send():
                        has_sent = True

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n🛑 Stopping...")
finally:
    GPIO.cleanup()