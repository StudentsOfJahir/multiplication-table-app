# 🖼️ Streamlit Image Filter App (Beginner Friendly)

import io
import numpy as np
import streamlit as st
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ExifTags

# ---------- Page setup ----------
st.set_page_config(page_title="Image Filter App", page_icon="🎨", layout="wide")
st.title("🎨 Image Filter App")
st.caption("Upload a photo, tweak filters, and download the result.")

# ---------- Helpers ----------
def load_image(file):
    img = Image.open(file)
    # Auto-rotate using EXIF orientation (if present)
    try:
        exif = img.getexif()
        if exif:
            img = ImageOps.exif_transpose(img)
    except Exception:
        pass
    # Ensure RGB for consistent processing
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    return img

def apply_sepia(img, intensity=1.0):
    """
    Apply a simple sepia effect. intensity: 0..1
    """
    if img.mode == "RGBA":
        # Work on RGB, keep alpha to re-attach
        rgb, a = img.convert("RGB"), img.split()[-1]
        img = rgb
    arr = np.array(img).astype(np.float32)

    # Sepia transform matrix
    tr = np.array([
        [0.393, 0.769, 0.189],
        [0.349, 0.686, 0.168],
        [0.272, 0.534, 0.131],
    ], dtype=np.float32)

    sep = arr @ tr.T
    sep = np.clip(sep, 0, 255).astype(np.uint8)

    # Blend original with sepia by intensity
    out = (arr * (1 - intensity) + sep * intensity).clip(0, 255).astype(np.uint8)
    out_img = Image.fromarray(out, mode="RGB")

    # Re-attach alpha if original had it
    if 'a' in locals():
        out_img.putalpha(a)
    return out_img

def pil_to_bytes(img, fmt="PNG", quality=90):
    buf = io.BytesIO()
    if fmt.upper() == "JPEG" and img.mode == "RGBA":
        img = img.convert("RGB")  # JPEG has no alpha
    save_kwargs = {}
    if fmt.upper() == "JPEG":
        save_kwargs["quality"] = int(quality)
        save_kwargs["optimize"] = True
    img.save(buf, format=fmt.upper(), **save_kwargs)
    buf.seek(0)
    return buf

# ---------- Sidebar controls ----------
with st.sidebar:
    st.header("⚙️ Controls")
    uploaded = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "webp"])
    st.write("---")
    st.subheader("Basic Filters")
    do_grayscale = st.checkbox("Grayscale")
    do_sepia = st.checkbox("Sepia")
    sepia_intensity = st.slider("Sepia intensity", 0.0, 1.0, 0.7, 0.05, disabled=not do_sepia)

    blur_radius = st.slider("Gaussian Blur", 0.0, 10.0, 0.0, 0.5)

    st.subheader("Adjustments (1.0 = no change)")
    bright = st.slider("Brightness", 0.1, 3.0, 1.0, 0.1)
    contrast = st.slider("Contrast", 0.1, 3.0, 1.0, 0.1)
    color = st.slider("Color (Saturation)", 0.0, 3.0, 1.0, 0.1)
    sharp = st.slider("Sharpness", 0.0, 3.0, 1.0, 0.1)

    st.subheader("Geometry")
    rotate_deg = st.slider("Rotate (°)", -180, 180, 0, 1)
    flip_h = st.checkbox("Flip horizontally")
    flip_v = st.checkbox("Flip vertically")

    st.write("---")
    st.subheader("Download Options")
    out_fmt = st.selectbox("Format", ["PNG", "JPEG"], index=0)
    jpeg_q = st.slider("JPEG quality", 50, 100, 90, disabled=(out_fmt != "JPEG"))

# ---------- Main app ----------
if uploaded is None:
    st.info("👆 Upload an image to begin.")
    st.stop()

# Load
orig = load_image(uploaded)
img = orig.copy()

# Apply filters in a simple, intuitive order
if do_grayscale:
    img = ImageOps.grayscale(img).convert("RGB")  # keep 3 channels for consistency

if do_sepia:
    img = apply_sepia(img, intensity=sepia_intensity)

if blur_radius > 0:
    img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))

# Enhancements (brightness, contrast, color, sharpness)
if abs(bright - 1.0) > 1e-6:
    img = ImageEnhance.Brightness(img).enhance(bright)
if abs(contrast - 1.0) > 1e-6:
    img = ImageEnhance.Contrast(img).enhance(contrast)
if abs(color - 1.0) > 1e-6:
    img = ImageEnhance.Color(img).enhance(color)
if abs(sharp - 1.0) > 1e-6:
    img = ImageEnhance.Sharpness(img).enhance(sharp)

# Geometry (rotate, flips)
if rotate_deg != 0:
    # expand=True to avoid cropping after rotation
    img = img.rotate(rotate_deg, resample=Image.BICUBIC, expand=True)
if flip_h:
    img = ImageOps.mirror(img)
if flip_v:
    img = ImageOps.flip(img)

# Show before/after side-by-side
c1, c2 = st.columns(2)
with c1:
    st.subheader("Before")
    st.image(orig, use_container_width=True)
with c2:
    st.subheader("After")
    st.image(img, use_container_width=True)

# Download
if out_fmt == "JPEG":
    buf = pil_to_bytes(img, fmt="JPEG", quality=jpeg_q)
else:
    buf = pil_to_bytes(img, fmt="PNG")

st.download_button(
    label="⬇️ Download edited image",
    data=buf,
    file_name=f"edited_image.{out_fmt.lower()}",
    mime=f"image/{out_fmt.lower()}",
)
