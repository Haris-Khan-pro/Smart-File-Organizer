\# 🗂️ Smart File Organizer Pro

A desktop file organization and analysis application built with Python and CustomTkinter.

Smart File Organizer Pro scans a selected folder, analyzes its files, categorizes them, calculates storage usage, detects duplicate files using SHA-256 hashing, organizes files into category folders, and provides an Undo system to restore organized files.

---

## 📸 Screenshots

![Total Files](screenshots/totalfiles.png)
![Categories](screenshots/categories.png)
![Total Size](screenshots/totalsize.png)
![Duplicates](screenshots/duplicates.png)

---

## ✨ Features

- 📁 **Folder Scanner** — Recursively scans any folder and collects full file metadata
- 📊 **Dashboard Cards** — Live stats for Total Files, Categories, Total Size, and Duplicates
- 🏷️ **File Categorization** — Automatically groups files into categories (Images, Documents, Videos, Audio, Code, Archives, and more)
- 🔍 **Category View** — Click any dashboard card to filter and explore files by category
- 💾 **Size Summary** — See storage usage broken down by category
- 📂 **Organize** — Moves files into named category subfolders in one click
- ↩️ **Undo Organization** — Restores every moved file back to its original location safely
- 🔎 **Duplicate Detection** — Identifies duplicate files using SHA-256 content hashing
- 🌙 **Dark Mode UI** — Clean professional dark interface built with CustomTkinter
- 🛡️ **Error Safe** — All operations handle permission errors, missing files, and naming conflicts without crashing

---

## 📁 Project Structure

```
Smart-File-Organizer/
├── app/
│   ├── main.py                  # 🚀 Entry point — starts the application
│   ├── core/
│   │   ├── config.py            # ⚙️  Category definitions and get_category() logic
│   │   ├── scanner.py           # 🔍 Scans folders and builds file metadata list
│   │   ├── organizer.py         # 📂 Moves files into folders + undo logic
│   │   └── logger.py            # 📝 Logging utility
│   └── ui/
│       ├── main_window.py       # 🖥️  Main window — connects UI to core functions
│       ├── dashboard.py         # 📊 Dashboard card components
│       ├── menu_bar.py          # 🔧 Menu bar
│       └── status_bar.py        # 📌 Status bar
├── config/
│   └── settings.json            # 🔧 App configuration
├── tests/                       # 🧪 Unit tests
├── requirements.txt
└── README.md
```

---

## 🏗️ Architecture — How the Files Work Together

The app follows a strict **core / UI separation**. The UI never touches the filesystem directly. All file operations live in `core/`. The UI only calls core functions and displays their results.

```
┌─────────────────────────────────────────────────┐
│                   app/main.py                   │
│          Entry point — launches the app         │
└────────────────────┬────────────────────────────┘
                     │ creates
                     ▼
┌─────────────────────────────────────────────────┐
│            app/ui/main_window.py                │
│   Handles all buttons, dashboard, file table    │
│   Calls core functions — never touches files    │
└────┬──────────────┬──────────────┬──────────────┘
     │ calls        │ calls        │ calls
     ▼              ▼              ▼
┌─────────┐  ┌───────────┐  ┌─────────────────┐
│scanner  │  │organizer  │  │   config.py      │
│.py      │  │.py        │  │                  │
│         │  │           │  │ Defines all file │
│scan()   │  │organize() │  │ categories and   │
│         │  │           │  │ get_category()   │
│Returns  │  │Moves files│  └─────────────────┘
│file     │  │into named │
│metadata │  │folders    │
│list     │  │           │
│         │  │undo_      │
│         │  │organiz-   │
│         │  │ation()    │
│         │  │           │
│         │  │Moves files│
│         │  │back to    │
│         │  │original   │
│         │  │locations  │
└─────────┘  └───────────┘
```

---

## 🔄 Data Flow — Step by Step

### 1️⃣ App Starts
```
main.py
  └── creates MainWindow()
        └── builds toolbar, dashboard, file table, status bar
```

### 2️⃣ User Selects a Folder
```
MainWindow.select_folder()
  └── stores folder path
  └── resets dashboard to zero
  └── enables the Scan button
```

### 3️⃣ User Clicks Scan
```
MainWindow.scan_folder()
  └── calls scanner.scan(folder_path)
        └── os.walk() through every subfolder
        └── for each file:
              └── reads name, path, size, extension
              └── calls config.get_category(extension)
                    └── looks up extension in FILE_CATEGORIES dict
                    └── returns category name ("Images", "Code", etc.)
              └── builds file dict { name, path, extension, size, category }
        └── returns { files, total_files, categories, total_size }
  └── updates dashboard cards with totals
  └── renders file list in the table
  └── enables the Organize button
```

### 4️⃣ User Clicks Organize
```
MainWindow.organize_files()
  └── calls organizer.organize(folder_path, scanned_files)
        └── for each file:
              └── creates category subfolder if it doesn't exist
              └── handles duplicate filenames (appends _1, _2 ...)
              └── moves file with shutil.move()
              └── records { name, category, source, destination }
        └── returns { moved: [...], errors: [...] }
  └── saves move history to self.last_organization
  └── enables the Undo button
  └── rescans folder to refresh the dashboard
```

### 5️⃣ User Clicks Undo
```
MainWindow.undo_files()
  └── calls organizer.undo_organization(moved_files)
        └── for each moved file:
              └── checks file still exists at destination
              └── recreates original directory if needed
              └── checks original location has no conflict
              └── moves file back with shutil.move()
              └── records restored or error
        └── returns { restored: [...], errors: [...] }
  └── clears self.last_organization
  └── disables Undo button
  └── rescans folder to refresh the dashboard
```

---

## ⚙️ How config.py Works

`config.py` is the brain of the categorization system. It holds a dictionary mapping each category name to a set of file extensions:

```python
FILE_CATEGORIES = {
    "Images":    { ".jpg", ".jpeg", ".png", ".gif", ... },
    "Documents": { ".pdf", ".doc", ".docx", ".txt", ... },
    "Videos":    { ".mp4", ".mkv", ".avi", ...},
    "Audio":     { ".mp3", ".wav", ".flac", ... },
    "Code":      { ".py", ".js", ".html", ".css", ... },
    "Archives":  { ".zip", ".rar", ".7z", ... },
    "Executables": { ".exe", ".msi", ".bat", ... }
}
```

When `scanner.py` processes a file, it calls `get_category(extension)` which loops through this dictionary and returns the matching category. If no match is found, it returns `"Other"`.

To add a new category or support a new file type, you only need to edit `config.py` — nothing else needs to change.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| 🐍 Language | Python 3.10+ |
| 🖥️ GUI Framework | CustomTkinter |
| 📦 File Operations | os, shutil (stdlib) |
| 🔐 Duplicate Detection | hashlib SHA-256 |
| 🏗️ Architecture | Modular — core logic separated from UI |

---

## 🚀 Installation

**1. Clone the repository**

```bash
git clone https://github.com/Haris-Khan-pro/Smart-File-Organizer.git
cd Smart-File-Organizer
```

**2. Create a virtual environment**

```bash
python -m venv .venv
```

**3. Activate the virtual environment**

```bash
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

**4. Install dependencies**

```bash
pip install -r requirements.txt
```

**5. Run the application**

```bash
python -m app.main
```

---

## 📖 Usage

1. 📁 Click **Select Folder** to choose the folder you want to organize
2. 🔍 Click **Scan** to analyze all files in the folder
3. 📊 Review the dashboard — Total Files, Categories, Total Size, Duplicates
4. 🏷️ Click any dashboard card to explore files by category
5. 📂 Click **Organize** to move files into category subfolders
6. ↩️ Click **Undo** at any time to restore all files to their original locations

---

## 🗃️ Supported File Categories

| Category | Extensions |
|---|---|
| 🖼️ Images | jpg, jpeg, png, gif, bmp, svg, webp, ico, tiff |
| 📄 Documents | pdf, doc, docx, txt, xls, xlsx, ppt, pptx, csv |
| 🎬 Videos | mp4, mkv, avi, mov, wmv, flv, webm, m4v |
| 🎵 Audio | mp3, wav, flac, aac, ogg, m4a, wma |
| 💻 Code | py, js, ts, html, css, java, c, cpp, go, rs, php, sql |
| 📦 Archives | zip, rar, tar, gz, 7z, bz2 |
| ⚙️ Executables | exe, msi, bat, cmd, sh |
| 📁 Other | Everything else |

---

## 🤝 Contributing

This project is open source and built for learning. Feel free to fork it, open issues, or submit pull requests.

---

## 👤 Author

**Haris Khan**
- 🐙 GitHub: [@Haris-Khan-pro](https://github.com/Haris-Khan-pro)

---

## 📜 License

This project is open source — see the [LICENSE](LICENSE) file for details.

---

*🐍 Built as part of a 50-day Python project sprint.*
