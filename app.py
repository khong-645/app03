import streamlit as st
from PIL import Image
import requests
from io import BytesIO
from ultralytics import YOLO

# โหลดโมเดล YOLOv8 (ถ้าไฟล์โมเดลไม่อยู่ในเครื่อง อาจต้องดาวน์โหลดก่อน)
try:
    model = YOLO("yolov8n.pt")
except Exception as e:
    st.error(f"❌ ไม่สามารถโหลดโมเดล YOLOv8 ได้: {e}")
    model = None

def load_image_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        return img
    except Exception as e:
        st.error(f"❌ โหลดภาพจาก URL ไม่สำเร็จ: {url}\n{e}")
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
    resized = [img.resize(base_size) for img in overlay_images]
    return resized

def overlay_images(base_image, overlay_images, alpha=0.5):
    result = base_image.copy()
    for img in overlay_images:
        result = Image.blend(result, img, alpha)
    return result

st.title("🧠 ซ้อนภาพ + ตรวจจับวัตถุ จาก URL")

url1 = st.text_input("URL รูปภาพพื้นหลัง (Base)", "")
url2 = st.text_input("URL รูปภาพซ้อนที่ 1", "")
url3 = st.text_input("URL รูปภาพซ้อนที่ 2 (ถ้ามี)", "")
alpha = st.slider("ระดับความโปร่งของภาพซ้อน (alpha)", 0.0, 1.0, 0.5, 0.05)

if st.button("โหลดและซ้อนภาพ"):
    urls = [url1, url2, url3]
    all_images = []
    object_info = []

    for i, url in enumerate(urls):
        url = url.strip()
        if url:
            img = load_image_from_url(url)
            if img:
                all_images.append(img)
                with st.spinner(f"🔍 ตรวจจับวัตถุในภาพที่ {i+1}..."):
                    objects = detect_objects(img)
                object_info.append((f"ภาพที่ {i+1}", url, objects))
            else:
                st.error(f"❌ โหลดไม่ได้: {url}")

    # แสดงผลการตรวจจับวัตถุ
    for idx, (title, url, objects) in enumerate(object_info):
        st.markdown(f"### {title}")
        st.image(all_images[idx], caption=f"จาก: {url}", use_container_width=True)
        if objects:
            st.success(f"✅ พบวัตถุ: {', '.join(objects)}")
        else:
            st.info("ไม่พบวัตถุที่รู้จัก")

    # ซ้อนภาพถ้ามีภาพอย่างน้อย 2 ภาพ
    if len(all_images) > 1:
        base = all_images[0]
        overlays = resize_images_to_base(base, all_images[1:])
        result = overlay_images(base, overlays, alpha)
        st.markdown("## 🖼️ ภาพซ้อนกันแล้ว")
        st.image(result, caption="ผลลัพธ์ภาพซ้อน", use_container_width=True)
    elif len(all_images) == 1:
        st.info("ต้องมีภาพซ้อนอย่างน้อย 1 รูป")
    else:
        st.warning("กรุณาใส่ URL รูปภาพอย่างน้อย 1 รูป")
