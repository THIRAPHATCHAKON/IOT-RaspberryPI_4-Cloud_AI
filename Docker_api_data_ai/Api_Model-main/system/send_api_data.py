import requests

def send_detection_data(lp_number, province, image_path):
    # URL Database ปลายทาง
    target_url = "PATH_FOR_DATABASE"
    
    payload = {
        'license_plate': lp_number,
        'province': province
    }
    
    try:
        with open(image_path, 'rb') as img_file:
            files = {'image': (image_path, img_file, 'image/png')}
            response = requests.post(target_url, data=payload, files=files)
            
            if response.status_code == 200:
                print("✅ [Database] บันทึกข้อมูลเรียบร้อย!")
                return response.json()
            else:
                print(f"❌ [Database] ล้มเหลว: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")