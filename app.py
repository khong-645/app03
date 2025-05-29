import streamlit as st
from PIL import Image
import requests
from io import BytesIO

def load_image_from_url(url):
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        return img
    except:
        return None

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

st.title("ซ้อนภาพจาก URL ด้วย Streamlit")

# รับ URL รูปภาพ
url1 = st.text_input("URL รูปภาพพื้นหลัง (Base)", "https://upload.wikimedia.org/wikipedia/commons/b/bf/Bulldog_inglese.jpg")
url2 = st.text_input("URL รูปภาพซ้อนที่ 1", "")
url3 = st.text_input("URL รูปภาพซ้อนที่ 2 (ถ้ามี)", "")
alpha = st.slider("ระดับความโปร่งของภาพซ้อน (alpha)", 0.0, 1.0, 0.5, 0.05)

if st.button("โหลดและซ้อนภาพ"):
    base = load_image_from_url(url1)
    overlays = []

    for url in [url2, url3]:
        if url.strip():
            img = load_image_from_url(url)
            if img:
                overlays.append(img)
            else:
                st.error(f"โหลดไม่ได้: {url}")

    if base and overlays:
        overlays_resized = resize_images_to_base(base, overlays)
        result = overlay_images(base, overlays_resized, alpha)
        st.image(result, caption="ภาพซ้อนกันแล้ว", use_container_width=True)
    else:
        st.warning("กรุณาใส่ URL รูปภาพพื้นหลัง และอย่างน้อย 1 ภาพซ้อน")
