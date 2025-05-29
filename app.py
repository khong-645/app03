import streamlit as st
from PIL import Image
import requests
from io import BytesIO

def load_image_from_url(url):
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img
    except:
        return None

def concat_images_horizontally(images):
    widths, heights = zip(*(i.size for i in images))
    total_width = sum(widths)
    max_height = max(heights)

    new_img = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for img in images:
        new_img.paste(img, (x_offset, 0))
        x_offset += img.width

    return new_img

st.title("รวมภาพจาก URL ด้วย Streamlit")

# รับ URL 2-3 อันจากผู้ใช้
url1 = st.text_input("URL รูปภาพที่ 1", "https://upload.wikimedia.org/wikipedia/commons/b/bf/Bulldog_inglese.jpg")
url2 = st.text_input("URL รูปภาพที่ 2 (ถ้ามี)", "")
url3 = st.text_input("URL รูปภาพที่ 3 (ถ้ามี)", "")

if st.button("โหลดและรวมภาพ"):
    urls = [url1, url2, url3]
    images = []

    for url in urls:
        if url.strip() != "":
            img = load_image_from_url(url)
            if img:
                images.append(img)
            else:
                st.error(f"ไม่สามารถโหลดภาพจาก URL: {url}")

    if len(images) > 0:
        combined_img = concat_images_horizontally(images)
        st.image(combined_img, caption="ภาพรวมกันแล้ว", use_column_width=True)
    else:
        st.warning("กรุณาใส่ URL รูปภาพที่ถูกต้องอย่างน้อย 1 รูป")
