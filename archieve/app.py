import streamlit as st
import os
import shutil
import numpy as np
import pandas as pd
from datetime import datetime
from PIL import Image
from deepface import DeepFace

# ── Config ───────────────────────────────────────────
KNOWN_FACES_DIR = "faces"
ATTENDANCE_FILE = "attendance.csv"
os.makedirs(KNOWN_FACES_DIR, exist_ok=True)

st.set_page_config(page_title="Face Attendance", page_icon="🎓", layout="wide")
st.title("🎓 Face Recognition Attendance System")

# ── Mark Attendance ──────────────────────────────────
def mark_attendance(name):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    if os.path.exists(ATTENDANCE_FILE):
        df = pd.read_csv(ATTENDANCE_FILE)
    else:
        df = pd.DataFrame(columns=["Name", "Date", "Time"])
    already = ((df["Name"] == name) & (df["Date"] == date_str)).any()
    if not already:
        new_row = pd.DataFrame([{"Name": name, "Date": date_str, "Time": time_str}])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(ATTENDANCE_FILE, index=False)
        return True
    return False

# ── Recognize Face ───────────────────────────────────
def recognize_face(snapshot_path):
    best_match = None
    best_distance = 1.0
    for filename in os.listdir(KNOWN_FACES_DIR):
        if filename.endswith((".jpg", ".png", ".jpeg")):
            known_path = os.path.join(KNOWN_FACES_DIR, filename)
            try:
                result = DeepFace.verify(
                    img1_path=snapshot_path,
                    img2_path=known_path,
                    model_name="VGG-Face",
                    enforce_detection=False
                )
                if result["verified"] and result["distance"] < best_distance:
                    best_distance = result["distance"]
                    best_match = os.path.splitext(filename)[0]
            except:
                continue
    return best_match

# ── Tabs ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📸 Register Student",
    "📂 Bulk Upload from Folder",
    "✅ Take Attendance",
    "📊 View Attendance"
])

# ── TAB 1: Register Single Student ───────────────────
with tab1:
    
    photo = st.camera_input("Take a Photo")

    st.markdown("""
    <style>
    div.stButton > button {
        background-color: #2e7d32;
        color: white;
        border: none;
        padding: 10px 28px;
        border-radius: 8px;
        font-size: 16px;
        cursor: pointer;
        transition: background-color 0.3s ease, transform 0.2s ease, box-shadow 0.3s ease;
    }

    div.stButton > button:hover {
        background-color: #43a047;
        transform: scale(1.05);
        box-shadow: 0px 4px 15px rgba(67, 160, 71, 0.5);
        color: white;
    }

    div.stButton > button:active {
        transform: scale(0.98);
        background-color: #1b5e20;
    }
    </style>
""", unsafe_allow_html=True)
    st.header("Register a New Student")
    name = st.text_input("Enter Student Name")
    
if st.button("Register") and name and photo:
    img = Image.open(photo)
    save_path = os.path.join(KNOWN_FACES_DIR, f"{name}.jpg")
    img.save(save_path)
    try:
        DeepFace.extract_faces(img_path=save_path, enforce_detection=True)
        st.success(f"✅ {name} registered successfully!")
    except:
        os.remove(save_path)
        st.error("❌ No face detected. Try again with better lighting.")
    

# ── TAB 2: Bulk Upload from Folder ───────────────────
with tab2:
    st.header("📂 Bulk Upload Images from Folder")

    st.info("""
    ℹ️ **How to use:**
    - Image filename = Student name
    - Example: `John.jpg` → registers as **John**
    - Supported formats: JPG, JPEG, PNG
    """)

    # ── Option 1: Upload Multiple Files ──────────────
    st.subheader("Option 1 — Upload Multiple Images")
    uploaded_files = st.file_uploader(
        "Select all student images at once",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    if st.button("📥 Register All Uploaded Images") and uploaded_files:
        success_count = 0
        fail_count = 0

        progress = st.progress(0)
        status = st.empty()

        for i, uploaded_file in enumerate(uploaded_files):
            # Get name from filename
            student_name = os.path.splitext(uploaded_file.name)[0]
            save_path = os.path.join(KNOWN_FACES_DIR, f"{student_name}.jpg")

            # Save image
            img = Image.open(uploaded_file)
            img.save(save_path)

            # Verify face exists
            try:
                DeepFace.extract_faces(img_path=save_path, enforce_detection=True)
                success_count += 1
                status.success(f"✅ Registered: {student_name}")
            except:
                os.remove(save_path)
                fail_count += 1
                status.error(f"❌ No face found in: {uploaded_file.name}")

            # Update progress bar
            progress.progress((i + 1) / len(uploaded_files))

        st.markdown("---")
        st.success(f"✅ Successfully registered: {success_count} students")
        if fail_count > 0:
            st.error(f"❌ Failed: {fail_count} images (no face detected)")

    st.markdown("---")

    # ── Option 2: Load from Local Folder Path ────────
    st.subheader("Option 2 — Load from Local Folder Path")
    st.warning("⚠️ This only works when running locally (not on Streamlit Cloud)")

    folder_path = st.text_input(
        "Enter folder path",
        placeholder="Example: C:/Users/YourName/Desktop/students"
    )

    if st.button("📂 Load from Folder") and folder_path:
        if not os.path.exists(folder_path):
            st.error("❌ Folder not found! Check the path.")
        else:
            image_files = [
                f for f in os.listdir(folder_path)
                if f.endswith((".jpg", ".jpeg", ".png"))
            ]

            if not image_files:
                st.error("❌ No images found in this folder!")
            else:
                st.info(f"Found {len(image_files)} images. Registering...")
                success_count = 0
                fail_count = 0
                progress = st.progress(0)
                status = st.empty()

                for i, filename in enumerate(image_files):
                    student_name = os.path.splitext(filename)[0]
                    src_path  = os.path.join(folder_path, filename)
                    save_path = os.path.join(KNOWN_FACES_DIR, f"{student_name}.jpg")

                    # Copy image to known_faces folder
                    shutil.copy(src_path, save_path)

                    # Verify face
                    try:
                        DeepFace.extract_faces(img_path=save_path, enforce_detection=True)
                        success_count += 1
                        status.success(f"✅ Registered: {student_name}")
                    except:
                        os.remove(save_path)
                        fail_count += 1
                        status.error(f"❌ No face in: {filename}")

                    progress.progress((i + 1) / len(image_files))

                st.markdown("---")
                st.success(f"✅ Registered: {success_count} students")
                if fail_count > 0:
                    st.error(f"❌ Failed: {fail_count} images")

    st.markdown("---")

    # ── Show Registered Students ──────────────────────
    st.subheader("👥 Currently Registered Students")
    students = [
        os.path.splitext(f)[0]
        for f in os.listdir(KNOWN_FACES_DIR)
        if f.endswith((".jpg", ".png", ".jpeg"))
    ]

    if students:
        cols = st.columns(4)
        for i, student in enumerate(students):
            with cols[i % 4]:
                img_path = os.path.join(KNOWN_FACES_DIR, f"{student}.jpg")
                st.image(img_path, caption=student, use_column_width=True)

        if st.button("🗑️ Clear All Students"):
            shutil.rmtree(KNOWN_FACES_DIR)
            os.makedirs(KNOWN_FACES_DIR, exist_ok=True)
            st.success("✅ All students cleared!")
            st.rerun()
    else:
        st.info("No students registered yet.")

# ── TAB 3: Take Attendance ────────────────────────────
with tab3:
    st.header("Take Attendance via Webcam")
    students = os.listdir(KNOWN_FACES_DIR)

    if not students:
        st.warning("⚠️ No students registered yet.")
    else:
        st.info(f"👥 {len(students)} student(s) registered")
        snapshot = st.camera_input("Take Snapshot for Attendance")

        if snapshot:
            temp_path = "temp_snapshot.jpg"
            Image.open(snapshot).save(temp_path)

            with st.spinner("🔍 Recognizing face..."):
                match = recognize_face(temp_path)

            os.remove(temp_path)

            if match:
                marked = mark_attendance(match)
                if marked:
                    st.success(f"✅ Attendance marked for **{match}**!")
                    st.balloons()
                else:
                    st.info(f"ℹ️ **{match}** already marked today.")
            else:
                st.error("❌ Face not recognized. Please register first.")

# ── TAB 4: View Attendance ────────────────────────────
with tab4:
    st.header("Attendance Records")
    if os.path.exists(ATTENDANCE_FILE):
        try:
            df = pd.read_csv(ATTENDANCE_FILE)
            if df.empty or len(df.columns) == 0:
                st.info("No attendance records yet.")
                st.stop()
        except pd.errors.EmptyDataError:
            st.info("No attendance records yet.")
            st.stop()
