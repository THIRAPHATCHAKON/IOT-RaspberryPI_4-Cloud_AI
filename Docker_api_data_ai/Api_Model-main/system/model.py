import requests
import json
import sys
import os
import glob
from send_api_data import send_detection_data 

# --- 1. ตั้งค่าพื้นฐาน (อัปเดตเป็น iApp V3) ---
url_iapp = "URL_API_IAPP"
api_key_iapp = "KEY_API"

# --- 2. ส่วนการรับไฟล์ภาพแบบอัตโนมัติ ---
if len(sys.argv) > 1:
    file_path = sys.argv[1]
else:
    list_of_files = glob.glob(os.path.join('images', '*'))
    file_path = max(list_of_files, key=os.path.getmtime) if list_of_files else None

if not file_path or not os.path.exists(file_path):
    print(f"❌ ไม่พบไฟล์รูปภาพ: {file_path}")
    sys.exit()

print(f"✅ กำลังประมวลผลไฟล์ (iApp API): {file_path}")

try:
    with open(file_path, 'rb') as f:
        # iApp ใช้ Header 'apikey' (ตัวเล็ก) และส่งไฟล์ผ่าน Multipart form-data
        files_iapp = {'file': f}
        headers = {'apikey': api_key_iapp}
        response = requests.post(url_iapp, files=files_iapp, headers=headers)

    # ตรวจสอบ Rate Limit จาก Header (ถ้ามี)
    remain_day = response.headers.get('x-ratelimit-remaining-day', 'N/A')
    
    if response.status_code == 200:
        result = response.json()
        
        # --- 3. จัดการข้อมูลที่ได้จาก iApp ---
        # ตัวอย่าง province: "th-14:Phra Nakhon Si Ayutthaya (พระนครศรีอยุธยา)"
        raw_province = result.get('province', '') 
        
        # ตัดเอาเฉพาะภาษาไทยในวงเล็บ
        if '(' in raw_province and ')' in raw_province:
            clean_province = raw_province.split('(')[-1].split(')')[0]
        else:
            # กรณีไม่มีวงเล็บ ให้พยายามแยกด้วยเครื่องหมาย :
            clean_province = raw_province.split(':')[-1] if ':' in raw_province else raw_province
            
        lp = result.get('lp_number')
        brand = result.get('vehicle_brand', 'Unknown')
        color = result.get('vehicle_color', 'Unknown')
        
        print(f"--- ผลการอ่าน: {lp} ({clean_province}) ---")
        print(f"🚗 ยี่ห้อ: {brand} | สี: {color}")
        print(f"📊 โควตาคงเหลือวันนี้: {remain_day}")
        
        # ส่งข้อมูลไปยัง API ปลายทางของคุณ
        send_detection_data(lp, clean_province, file_path)
        
    elif response.status_code == 401:
        print("❌ Error: API Key ของ iApp ไม่ถูกต้อง")
    elif response.status_code == 429:
        print("❌ Error: Rate limit เกินกำหนดแล้ว")
    else:
        print(f"❌ Error API: {response.status_code} - {response.text}")

except Exception as e:
    print(f"❌ เกิดข้อผิดพลาดใน model.py: {e}")