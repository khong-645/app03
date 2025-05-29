import streamlit as st
from PIL import Image
import requests
from io import BytesIO

# ลอง import YOLO โมเดล ถ้าไม่มีให้ติดตั้ง ultralytics
try:
    from ultralytics import YOLO
    model = YOLO("yolov8n.pt")  # โหลดโมเดล (ถ้ายังไม่มี จะดาวน์โหลดเอง)
except Exception as e:
    st.error(f"ไม่สามารถโหลดโมเดล YOLO ได้: {e}")
    model = None

def load_image_from_url(url):
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        return img
    except:
        return None

def detect_objects(image):
    if model is None:
        return []
    results = model.predict(image)
    if results and len(results) > 0 and results[0].boxes is not None and len(results[0].boxes) > 0:
        names = results[0].names
        classes = results[0].boxes.cls.tolist()
        detected = [names[int(c)] for c in classes]
        return list(set(detected))
    return []

def resize_images_to_base(base_image, overlay_images):
    base_size = base_image.size
    resized = []
    for img in overlay_images:
        resized.append(img.resize(base_size))
    return resized

def overlay_images(base_image, overlay_images, alpha=0.5):
    result = base_image.copy()
    for img in overlay_images:
        blended = Image.blend(result, img, alpha)
        result = blended
    return result

st.title("ซ้อนภาพจาก URL + ตรวจจับวัตถุ ด้วย Streamlit")

# รับ URL รูปภาพ
url1 = st.text_input("URL รูปภาพพื้นหลัง (Base)", "https://upload.wikimedia.org/wikipedia/commons/b/bf/Bulldog_inglese.jpg")
url2 = st.text_input("URL รูปภาพซ้อนที่ 1", "")
url3 = st.text_input("URL รูปภาพซ้อนที่ 2 (ถ้ามี)", "")
alpha = st.slider("ระดับความโปร่งของภาพซ้อน (alpha)", 0.0, 1.0, 0.5, 0.05)

if st.button("โหลดและซ้อนภาพ"):
    base = load_image_from_url(url1)
    overlays = []
    objects_info = []

    # ตรวจจับวัตถุและเก็บข้อมูลภาพพื้นหลัง
    if base:
        objs = detect_objects(base)
        objects_info.append(("ภาพพื้นหลัง", url1, objs))

    # โหลดและตรวจจับวัตถุภาพซ้อน
    for url in [url2, url3]:
        if url.strip():
            img = load_image_from_url(url)
            if img:
                overlays.append(img)
                objs = detect_objects(img)
                objects_info.append(("ภาพซ้อน", url, objs))
            else:
                st.error(f"โหลดไม่ได้: {url}")

    # แสดงภาพและวัตถุที่ตรวจจับได้
    for idx, (title, url, objs) in enumerate(objects_info):
        st.markdown(f"### {title}")
        st.image(load_image_from_url(url), caption=f"จาก: {url}", use_container_width=True)
        if objs:
            st.success(f"ตรวจพบวัตถุ: {', '.join(objs)}")
        else:
            st.info("ไม่พบวัตถุที่รู้จัก")

    # ซ้อนภาพถ้ามีภาพซ้อนอย่างน้อย 1 ภาพ
    if base and overlays:
        overlays_resized = resize_images_to_base(base, overlays)
        result = overlay_images(base, overlays_resized, alpha)
        st.markdown("## ภาพซ้อนกันแล้ว")
        st.image(result, caption="ผลลัพธ์ภาพซ้อน", use_container_width=True)
    else:
        st.warning("กรุณาใส่ URL รูปภาพพื้นหลัง และอย่างน้อย 1 รูปภาพซ้อน")
