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
ROSTER_FILE     = "students.csv"          # ← NEW: pre-loaded student list
os.makedirs(KNOWN_FACES_DIR, exist_ok=True)

st.set_page_config(page_title="Face Attendance", page_icon="🎓", layout="wide")
st.title("🎓 Face Recognition Attendance System")

# ── Shared button style ──────────────────────────────
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

# ── Roster helpers ───────────────────────────────────
def load_roster() -> pd.DataFrame:
    """Return the student roster. Columns: Name, StudentID (optional)."""
    if os.path.exists(ROSTER_FILE):
        try:
            df = pd.read_csv(ROSTER_FILE)
            if "Name" not in df.columns:
                df = pd.DataFrame(columns=["Name", "StudentID"])
        except pd.errors.EmptyDataError:
            df = pd.DataFrame(columns=["Name", "StudentID"])
    else:
        df = pd.DataFrame(columns=["Name", "StudentID"])
    return df

def save_roster(df: pd.DataFrame):
    df.to_csv(ROSTER_FILE, index=False)

def roster_names() -> list:
    return load_roster()["Name"].dropna().unique().tolist()

def face_exists(name: str) -> bool:
    """Check whether a reference photo exists for this student."""
    for ext in (".jpg", ".jpeg", ".png"):
        if os.path.exists(os.path.join(KNOWN_FACES_DIR, f"{name}{ext}")):
            return True
    return False

# ── Mark Attendance ──────────────────────────────────
def mark_attendance(name: str) -> bool:
    now      = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    if os.path.exists(ATTENDANCE_FILE):
        try:
            df = pd.read_csv(ATTENDANCE_FILE)
        except pd.errors.EmptyDataError:
            df = pd.DataFrame(columns=["Name", "Date", "Time"])
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
def recognize_face(snapshot_path: str):
    """
    Compare snapshot against every face image in KNOWN_FACES_DIR.
    Returns the best-matching student name, or None.
    """
    best_match    = None
    best_distance = 1.0

    for filename in os.listdir(KNOWN_FACES_DIR):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        known_path = os.path.join(KNOWN_FACES_DIR, filename)
        try:
            result = DeepFace.verify(
                img1_path=snapshot_path,
                img2_path=known_path,
                model_name="VGG-Face",
                enforce_detection=False,
            )
            if result["verified"] and result["distance"] < best_distance:
                best_distance = result["distance"]
                best_match    = os.path.splitext(filename)[0]
        except Exception:
            continue

    return best_match

# ── Tabs ─────────────────────────────────────────────
tab0, tab1, tab2, tab3, tab4 = st.tabs([
    "👥 Student Roster",          # ← NEW
    "📸 Register Student",
    "📂 Bulk Upload from Folder",
    "✅ Take Attendance",
    "📊 View Attendance",
])

# ══════════════════════════════════════════════════════
# TAB 0 — Student Roster  (pre-load student details)
# ══════════════════════════════════════════════════════
with tab0:
    st.header("👥 Student Roster")
    st.info(
        "Add students here **before** taking attendance. "
        "Once a student is in the roster you only need to supply their photo once — "
        "attendance can be marked by face recognition without re-registering them every session."
    )

    roster_df = load_roster()

    # ── Manual add ──────────────────────────────────
    st.subheader("Add a Student")
    col_a, col_b = st.columns(2)
    with col_a:
        new_name = st.text_input("Full Name", key="roster_name")
    with col_b:
        new_id   = st.text_input("Student ID (optional)", key="roster_id")

    if st.button("➕ Add to Roster"):
        if not new_name.strip():
            st.error("Name cannot be empty.")
        elif new_name.strip() in roster_df["Name"].values:
            st.warning(f"**{new_name}** is already in the roster.")
        else:
            new_row   = pd.DataFrame([{"Name": new_name.strip(), "StudentID": new_id.strip()}])
            roster_df = pd.concat([roster_df, new_row], ignore_index=True)
            save_roster(roster_df)
            st.success(f"✅ **{new_name}** added to roster.")
            st.rerun()

    st.markdown("---")

    # ── Upload roster CSV ────────────────────────────
    st.subheader("Import Roster from CSV")
    st.caption("CSV must have at least a **Name** column. A **StudentID** column is optional.")
    uploaded_roster = st.file_uploader("Upload students.csv", type=["csv"], key="roster_upload")

    if st.button("📥 Import CSV") and uploaded_roster:
        try:
            imported = pd.read_csv(uploaded_roster)
            if "Name" not in imported.columns:
                st.error("CSV must contain a 'Name' column.")
            else:
                # Merge — skip duplicates
                existing_names = set(roster_df["Name"].values)
                new_students   = imported[~imported["Name"].isin(existing_names)]
                if "StudentID" not in new_students.columns:
                    new_students = new_students.copy()
                    new_students["StudentID"] = ""
                roster_df = pd.concat(
                    [roster_df, new_students[["Name", "StudentID"]]], ignore_index=True
                )
                save_roster(roster_df)
                st.success(f"✅ Imported {len(new_students)} new student(s).")
                st.rerun()
        except Exception as e:
            st.error(f"Failed to read CSV: {e}")

    st.markdown("---")

    # ── Roster table ────────────────────────────────
    st.subheader("Current Roster")
    roster_df = load_roster()   # reload after possible changes

    if roster_df.empty:
        st.info("No students in roster yet.")
    else:
        # Annotate with photo status
        roster_df["Photo Registered"] = roster_df["Name"].apply(
            lambda n: "✅ Yes" if face_exists(n) else "⚠️ No photo yet"
        )
        st.dataframe(roster_df, use_container_width=True)

        st.caption(
            "Students marked **⚠️ No photo yet** cannot be recognised until you upload "
            "their photo in the **Register Student** or **Bulk Upload** tab."
        )

        if st.button("🗑️ Clear Entire Roster"):
            save_roster(pd.DataFrame(columns=["Name", "StudentID"]))
            st.success("Roster cleared.")
            st.rerun()

# ══════════════════════════════════════════════════════
# TAB 1 — Register Single Student
# ══════════════════════════════════════════════════════
with tab1:
    st.header("Register a New Student")

    # ── Choose from roster or type a new name ───────
    roster_names_list = roster_names()
    use_roster        = roster_names_list  # may be empty

    if use_roster:
        st.info("Students already in the roster are listed below. Select one to register their photo, or type a brand-new name.")
        name_choice = st.selectbox(
            "Select from roster (or choose 'New student…')",
            options=["— New student —"] + use_roster,
            key="reg_select",
        )
        if name_choice == "— New student —":
            name = st.text_input("Enter New Student Name", key="reg_new_name")
        else:
            name = name_choice
    else:
        name = st.text_input("Enter Student Name", key="reg_plain_name")

    photo = st.camera_input("Take a Photo")

    if st.button("Register") and name and photo:
        img       = Image.open(photo)
        save_path = os.path.join(KNOWN_FACES_DIR, f"{name}.jpg")
        img.save(save_path)
        try:
            DeepFace.extract_faces(img_path=save_path, enforce_detection=True)

            # Auto-add to roster if not already there
            roster_df = load_roster()
            if name not in roster_df["Name"].values:
                new_row   = pd.DataFrame([{"Name": name, "StudentID": ""}])
                roster_df = pd.concat([roster_df, new_row], ignore_index=True)
                save_roster(roster_df)

            st.success(f"✅ {name} registered successfully!")
        except Exception:
            os.remove(save_path)
            st.error("❌ No face detected. Try again with better lighting.")

# ══════════════════════════════════════════════════════
# TAB 2 — Bulk Upload
# ══════════════════════════════════════════════════════
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
        accept_multiple_files=True,
    )

    if st.button("📥 Register All Uploaded Images") and uploaded_files:
        success_count = fail_count = 0
        progress = st.progress(0)
        status   = st.empty()
        roster_df = load_roster()

        for i, uploaded_file in enumerate(uploaded_files):
            student_name = os.path.splitext(uploaded_file.name)[0]
            save_path    = os.path.join(KNOWN_FACES_DIR, f"{student_name}.jpg")
            img = Image.open(uploaded_file)
            img.save(save_path)

            try:
                DeepFace.extract_faces(img_path=save_path, enforce_detection=True)
                success_count += 1
                status.success(f"✅ Registered: {student_name}")

                # Auto-add to roster
                if student_name not in roster_df["Name"].values:
                    roster_df = pd.concat(
                        [roster_df, pd.DataFrame([{"Name": student_name, "StudentID": ""}])],
                        ignore_index=True,
                    )
            except Exception:
                os.remove(save_path)
                fail_count += 1
                status.error(f"❌ No face found in: {uploaded_file.name}")

            progress.progress((i + 1) / len(uploaded_files))

        save_roster(roster_df)
        st.markdown("---")
        st.success(f"✅ Successfully registered: {success_count} students")
        if fail_count:
            st.error(f"❌ Failed: {fail_count} images (no face detected)")

    st.markdown("---")

    # ── Option 2: Local Folder Path ──────────────────
    st.subheader("Option 2 — Load from Local Folder Path")
    st.warning("⚠️ This only works when running locally (not on Streamlit Cloud)")

    folder_path = st.text_input(
        "Enter folder path",
        placeholder="Example: C:/Users/YourName/Desktop/students",
    )

    if st.button("📂 Load from Folder") and folder_path:
        if not os.path.exists(folder_path):
            st.error("❌ Folder not found! Check the path.")
        else:
            image_files = [
                f for f in os.listdir(folder_path)
                if f.lower().endswith((".jpg", ".jpeg", ".png"))
            ]
            if not image_files:
                st.error("❌ No images found in this folder!")
            else:
                st.info(f"Found {len(image_files)} images. Registering…")
                success_count = fail_count = 0
                progress  = st.progress(0)
                status    = st.empty()
                roster_df = load_roster()

                for i, filename in enumerate(image_files):
                    student_name = os.path.splitext(filename)[0]
                    src_path     = os.path.join(folder_path, filename)
                    save_path    = os.path.join(KNOWN_FACES_DIR, f"{student_name}.jpg")
                    shutil.copy(src_path, save_path)

                    try:
                        DeepFace.extract_faces(img_path=save_path, enforce_detection=True)
                        success_count += 1
                        status.success(f"✅ Registered: {student_name}")

                        if student_name not in roster_df["Name"].values:
                            roster_df = pd.concat(
                                [roster_df, pd.DataFrame([{"Name": student_name, "StudentID": ""}])],
                                ignore_index=True,
                            )
                    except Exception:
                        os.remove(save_path)
                        fail_count += 1
                        status.error(f"❌ No face in: {filename}")

                    progress.progress((i + 1) / len(image_files))

                save_roster(roster_df)
                st.markdown("---")
                st.success(f"✅ Registered: {success_count} students")
                if fail_count:
                    st.error(f"❌ Failed: {fail_count} images")

    st.markdown("---")

    # ── Show Registered Students ──────────────────────
    st.subheader("👥 Currently Registered Students")
    students = [
        os.path.splitext(f)[0]
        for f in os.listdir(KNOWN_FACES_DIR)
        if f.lower().endswith((".jpg", ".png", ".jpeg"))
    ]

    if students:
        cols = st.columns(4)
        for i, student in enumerate(students):
            with cols[i % 4]:
                img_path = os.path.join(KNOWN_FACES_DIR, f"{student}.jpg")
                st.image(img_path, caption=student, use_column_width=True)

        if st.button("🗑️ Clear All Student Photos"):
            shutil.rmtree(KNOWN_FACES_DIR)
            os.makedirs(KNOWN_FACES_DIR, exist_ok=True)
            st.success("✅ All student photos cleared! (Roster preserved)")
            st.rerun()
    else:
        st.info("No student photos registered yet.")

# ══════════════════════════════════════════════════════
# TAB 3 — Take Attendance
# ══════════════════════════════════════════════════════
with tab3:
    st.header("Take Attendance via Webcam")

    all_roster_names = roster_names()
    photo_students   = [
        os.path.splitext(f)[0]
        for f in os.listdir(KNOWN_FACES_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    if not photo_students:
        st.warning("⚠️ No student photos registered yet. Please register photos first.")
    else:
        # Show roster vs photo coverage summary
        no_photo = [n for n in all_roster_names if not face_exists(n)]
        st.info(
            f"👥 **{len(all_roster_names)}** student(s) in roster — "
            f"**{len(photo_students)}** have photos for recognition."
        )
        if no_photo:
            with st.expander(f"⚠️ {len(no_photo)} student(s) in roster have no photo yet"):
                for n in no_photo:
                    st.write(f"• {n}")

        snapshot = st.camera_input("Take Snapshot for Attendance")

        if snapshot:
            temp_path = "temp_snapshot.jpg"
            Image.open(snapshot).save(temp_path)

            with st.spinner("🔍 Recognising face…"):
                match = recognize_face(temp_path)

            os.remove(temp_path)

            if match:
                # ── Check if matched student is in roster ──
                roster_df = load_roster()
                in_roster = match in roster_df["Name"].values

                marked = mark_attendance(match)
                if marked:
                    st.success(f"✅ Attendance marked for **{match}**!")
                    if not in_roster:
                        st.caption("(Student was not in the roster — added automatically.)")
                    st.balloons()
                else:
                    st.info(f"ℹ️ **{match}** already marked today.")
            else:
                st.error("❌ Face not recognised. Please register the student's photo first.")

                # ── Helpful hint: show roster students without photos ──
                if no_photo:
                    st.caption(
                        "Tip: The following roster students still need their photo uploaded: "
                        + ", ".join(no_photo)
                    )

# ══════════════════════════════════════════════════════
# TAB 4 — View Attendance
# ══════════════════════════════════════════════════════
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

        # ── Filter controls ──────────────────────────
        col1, col2 = st.columns(2)
        with col1:
            date_filter = st.selectbox(
                "Filter by Date",
                options=["All"] + sorted(df["Date"].unique().tolist(), reverse=True),
            )
        with col2:
            name_filter = st.selectbox(
                "Filter by Student",
                options=["All"] + sorted(df["Name"].unique().tolist()),
            )

        filtered = df.copy()
        if date_filter != "All":
            filtered = filtered[filtered["Date"] == date_filter]
        if name_filter != "All":
            filtered = filtered[filtered["Name"] == name_filter]

        st.dataframe(filtered, use_container_width=True)

        # ── Daily summary against roster ────────────
        if date_filter != "All":
            st.markdown("---")
            st.subheader(f"Attendance Summary — {date_filter}")
            roster_df    = load_roster()
            present_set  = set(filtered["Name"].values)
            absent_list  = [n for n in roster_names() if n not in present_set]

            col_p, col_a = st.columns(2)
            with col_p:
                st.metric("Present", len(present_set))
            with col_a:
                st.metric("Absent", len(absent_list))

            if absent_list:
                with st.expander("Absent Students"):
                    for n in absent_list:
                        st.write(f"• {n}")

        # ── Download ─────────────────────────────────
        st.markdown("---")
        csv_data = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Attendance CSV",
            data=csv_data,
            file_name="attendance_export.csv",
            mime="text/csv",
        )
    else:
        st.info("No attendance records yet.")