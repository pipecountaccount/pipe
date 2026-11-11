import streamlit as st
from PIL import Image, ImageDraw
from ultralytics import YOLO
import numpy as np
import cv2
import io
import zipfile
from datetime import datetime
from pathlib import Path
from streamlit_image_coordinates import streamlit_image_coordinates

from data_manager import (
    add_location,
    append_result,
    load_locations,
    load_results,
    safe_filename_part,
    IMAGES_DIR,
    CSV_PATH,
)

# -------------------------------------------------
# 1. 初期設定とモデルロード
# -------------------------------------------------

st.set_page_config(
    page_title="PINEAPPLE Pipe Counter",
    layout="wide"
)

@st.cache_resource
def load_model():
    model_path = "last_openvino_model"
    return YOLO(model_path)

model = load_model()



TARGET_SIZE = 960


# -------------------------------------------------
# 2. Session State の初期化
# -------------------------------------------------

DEFAULTS = {
    "phase": "upload",
    "mask_rects": [],
    "temp_point": None,
    "last_processed_click": None,
    "points": [],
    "auto_boxes": None,
    "current_upload_id": None,
    "saved_zip_data": None,
    "saved_filename": None,
    "saved_message": None,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -------------------------------------------------
# 3. 便利関数
# -------------------------------------------------

def apply_masks(img, rects):
    """画像に黒塗りのマスクを適用する"""
    draw = ImageDraw.Draw(img)

    for r in rects:
        draw.rectangle(
            [r[0], r[1], r[2], r[3]],
            fill="black"
        )

    return img


def resize_with_aspect_ratio(img, target_max_side):
    """アスペクト比を維持してリサイズする"""

    w, h = img.size

    if w > h:
        new_w = target_max_side
        new_h = int(h * (target_max_side / w))
    else:
        new_h = target_max_side
        new_w = int(w * (target_max_side / h))

    return img.resize(
        (new_w, new_h),
        Image.LANCZOS
