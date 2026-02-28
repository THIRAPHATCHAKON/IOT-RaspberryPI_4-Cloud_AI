# ใช้ Python Image พื้นฐานที่น้ำหนักเบา
FROM python:3.10-slim

# ตั้งค่า Directory ทำงานใน Container
WORKDIR /app

# ติดตั้ง dependencies สำหรับระบบ (เช่น libgl1 สำหรับ OpenCV ถ้ามีในอนาคต)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# คัดลอกไฟล์ requirements เข้ามาติดตั้งก่อน (เพื่อใช้ประโยชน์จาก Docker Cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกโค้ดทั้งหมดในโฟลเดอร์ system เข้าไปใน Container
COPY system/ .

# สร้างโฟลเดอร์ images รอไว้สำหรับเก็บรูปที่ส่งมา
RUN mkdir -p images

# เปิดพอร์ต 5000 ตามที่ server.py ใช้งาน
EXPOSE 5000

# สั่งรัน server.py เมื่อเริ่ม Container
CMD ["python", "server.py"]