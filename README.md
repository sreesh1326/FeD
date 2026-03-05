# Face Recognition Attendance System
This app automates classroom attendance using **face recognition technology**.  
Instead of calling names or passing paper sheets, students are identified by their face  
and attendance is logged instantly.

**Built with:**
- 🐍 Python + Streamlit (UI)
- 🤖 DeepFace + VGG-Face (face recognition engine)
- 🐼 Pandas (data management)
- 🖼️ Pillow (image processing)

**Files the system manages:**

| File | Purpose |
|---|---|
| `students.csv` | Master list of all students (roster) |
| `faces/` folder | One reference photo per student |
| `attendance.csv` | Log of every marked attendance with date & time |
        """)

    # ── How It Works ──────────────────────────────────
    with st.expander("⚙️ How It Works — Step by Step"):
        st.markdown("""
### The 4-Step Workflow

**Step 1 — Build your Student Roster (Tab: 👥 Student Roster)**
- Add student names and IDs before anything else
- Import a CSV with a `Name` column for bulk entry
- The roster is stored in `students.csv` automatically

**Step 2 — Register Face Photos (Tab: 📸 Register Student or 📂 Bulk Upload)**
- Each student needs one reference photo taken once
- Photos are saved in the `faces/` folder as `StudentName.jpg`
- DeepFace validates that a real face is detected in the photo
- Bulk upload lets you register an entire class at once from a folder

**Step 3 — Take Attendance (Tab: ✅ Take Attendance)**
- Student stands in front of the webcam
- App captures a snapshot and compares it against all photos in `faces/`
- DeepFace's `verify()` finds the closest match
- Attendance is logged in `attendance.csv` with name, date, and time
- Each student can only be marked once per day

**Step 4 — View Records (Tab: 📊 View Attendance)**
- Filter records by date or student name
- See who is absent for any given day (cross-referenced with roster)
- Download the filtered data as a CSV file
        """)

    # ── Tab Guide ─────────────────────────────────────
    with st.expander("🗂️ Tab-by-Tab User Guide"):
        st.markdown("""
### 👥 Student Roster
| Action | How |
|---|---|
| Add a student | Type name + ID → click **➕ Add to Roster** |
| Import a class list | Upload a CSV with a `Name` column → click **📥 Import CSV** |
| Delete selected students | Pick names from dropdown → click **🗑️ Remove** |
| Also delete their photo | Check the checkbox before removing |
| Clear everyone | Click **🗑️ Clear Entire Roster** |

---

### 📸 Register Student
| Action | How |
|---|---|
| Register from roster | Select name from dropdown → take photo → **Register** |
| Register new student | Choose "New student…" → type name → take photo → **Register** |

> ⚠️ Make sure lighting is good and the face is clearly visible.

---

### 📂 Bulk Upload from Folder
| Action | How |
|---|---|
| Upload multiple images | Select all images at once → click **📥 Register All** |
| Load from local folder | Enter folder path → click **📂 Load from Folder** |
| View registered students | Scroll down to see photo grid |
| Clear all photos | Click **🗑️ Clear All Student Photos** |

> 📌 File name = Student name. Example: `Alice.jpg` registers as **Alice**

---

### ✅ Take Attendance
| Action | How |
|---|---|
| Mark attendance | Click **Take Snapshot** → face is recognised automatically |
| Already marked today | App will notify you — no duplicate entries |
| Face not recognised | Register the student's photo first |

---

### 📊 View Attendance
| Action | How |
|---|---|
| Filter by date | Use the **Filter by Date** dropdown |
| Filter by student | Use the **Filter by Student** dropdown |
| See absent students | Select a specific date — absent list appears below |
| Download records | Click **⬇️ Download Attendance CSV** |
        """)

    # ── FAQ ───────────────────────────────────────────
    with st.expander("❓ Frequently Asked Questions"):
        st.markdown("""
**Q: Do I need to register students every session?**  
A: No. Register the photo once — the system recognises them in every future session automatically.

---

**Q: Do I need to create `students.csv` manually?**  
A: No. The file is created automatically the first time you add a student through the app.

---

**Q: What if a student's face isn't recognised?**  
A: Make sure their photo is registered. Poor lighting or face coverings can affect accuracy — try re-registering with a clearer photo.

---

**Q: Can two students be marked from the same snapshot?**  
A: No. Each snapshot marks one person. Students need to take snapshots one at a time.

---

**Q: What happens if I delete a student from the roster?**  
A: They are removed from the roster. You can optionally also delete their face photo. Their past attendance records in `attendance.csv` are preserved.

---

**Q: Can a student be marked twice in one day?**  
A: No. The system checks the date and prevents duplicate entries for the same student on the same day.

---

**Q: Will this work on Streamlit Cloud?**  
A: Partially. The webcam works but files (`students.csv`, `faces/`, `attendance.csv`) reset whenever the app restarts. For persistent data, run it locally or integrate cloud storage like Firebase.

---

**Q: How accurate is the face recognition?**  
A: VGG-Face is highly accurate under good lighting. Accuracy drops with masks, heavy glasses, or very poor lighting.
        """)

    # ── File Structure ────────────────────────────────
    with st.expander("📁 Project File Structure"):
        st.markdown("""
```
your-project/
│
├── app.py                  ← Main Streamlit app (run this)
├── requirements.txt        ← Python dependencies
├── students.csv            ← Auto-created: student roster
├── attendance.csv          ← Auto-created: attendance log
│
├── faces/                  ← Auto-created: reference photos
│   ├── Alice.jpg
│   ├── Bob.jpg
│   └── ...
│
└── archive/                ← Old/unused files (ignored by app)
    └── old_app.py
```
        """)

    # ── Requirements ──────────────────────────────────
    with st.expander("📦 Requirements & Installation"):
        st.markdown("""
### Install Dependencies

Make sure you have Python 3.8+ installed, then run:

```bash
pip install streamlit deepface pandas pillow opencv-python tf-keras
```

Or if you have a `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Run the App

```bash
streamlit run app.py
```

### Recommended `requirements.txt`
```
streamlit
deepface
pandas
pillow
opencv-python
tf-keras
numpy
