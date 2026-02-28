Real-time LPR System (IoT + Cloud)
ระบบตรวจจับป้ายทะเบียนรถอัตโนมัติโดยใช้เซนเซอร์ Ultrasonic วัดระยะประชิด และประมวลผลผ่าน iApp API บน Cloud Server
1. ฝั่ง Raspberry Pi (Edge Device)
ทำหน้าที่ตรวจจับวัตถุ, วัดระยะทาง, ควบคุมไฟ LED และส่งภาพไปยัง Server

ไฟล์หลัก: Hardware_RaspberryPi
Logic การทำงาน:
ตรวจจับวัตถุในระยะ < 15 cm (ปรับจูนผ่าน MAX_DISTANCE).
ใช้ระบบ Hysteresis (Clear ที่ 25 cm) เพื่อป้องกันการส่งข้อมูลซ้ำซ้อนจากสัญญาณรบกวน.
ส่งสถานะ 1 ไปยัง PocketBase เมื่อเจอวัตถุ และส่ง 0 เมื่อวัตถุออกไป.
ถ่ายภาพความละเอียด 1280x720 และส่งไปยัง API Server.

🛠 การติดตั้ง (Setup):
การเชื่อมต่อสาย (Wiring):
TRIG: GPIO 22 | ECHO: GPIO 27
LED Detection: GPIO 23 (สีแดง)
LED Success: GPIO 25 (สีเขียว)

สร้าง Environment:
Bash
python3 -m venv venv
source venv/bin/activate
pip install requests RPi.GPIO

2. ฝั่ง Cloud Server (Docker & API)
ทำหน้าที่รับรูปภาพจาก Pi, เรียกใช้ iApp LPR API และบันทึกข้อมูลลง Database
📁 ไฟล์หลัก: Docker_api_data_ai (Inside Docker)
Endpoint: POST /backend/api/detections?image
API Integration: * เรียกใช้ iApp LPR V3 (ค่าบริการ 0.75 IC/Request).
จัดการ Error 402 (Insufficient Credits) และ 415 (Format Error).
Database: บันทึกทะเบียนรถและจังหวัดลงในระบบ Backend.

การจัดการ Docker (Linux/MacOS):
git clone https://github.com/your-user/IOT-RaspberryPI_4-Cloud_AI

cd Api_Model-main

1.sudo apt install docker.io
2.sudo systemctl start docker
3.sudo systemctl enable docker
4.docker build -t lpr-service .
5.docker run -d \
  --name lpr_system \
  -p 5000:5000 \
  --restart always \
  -v $(pwd)/images:/app/images \
  lpr-service
6.docker ps
