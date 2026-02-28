from flask import Flask, request, jsonify
import os
import subprocess
import sys

app = Flask(__name__)
UPLOAD_FOLDER = 'images'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/backend/api/detections', methods=['POST'])
def receive_detection():
    if 'image' not in request.files:
        return jsonify({"status": "failed", "message": "No image part"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"status": "failed", "message": "No selected file"}), 400

    if file:
        # บันทึกไฟล์ลงในโฟลเดอร์ images
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        print(f"✅ บันทึกรูปภาพเรียบร้อย: {file_path}")

        # สั่งรัน model.py พร้อมส่ง path รูปไปเป็น argument
        try:
            # ใช้ sys.executable เพื่อให้มั่นใจว่าใช้ Python ตัวเดียวกับที่รัน Server
            subprocess.Popen([sys.executable, 'model.py', file_path])
        except Exception as e:
            print(f"❌ ไม่สามารถเริ่ม model.py ได้: {e}")

        return jsonify({
            "status": "success", 
            "message": "Image received and processing started",
            "saved_path": file_path
        }), 200

if __name__ == '__main__':
    # รันบน Local/Cloud ใช้พอร์ต 5000
    app.run(host='0.0.0.0', port=5000)