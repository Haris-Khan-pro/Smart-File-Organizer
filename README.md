# Smart File Organizer Pro

A desktop file organization and analysis application built with Python and CustomTkinter.

Smart File Organizer Pro scans a selected folder, analyzes its files, categorizes them, calculates storage usage, detects duplicate files using SHA-256 hashing, organizes files into category folders, and provides an Undo system to restore organized files.

---

## Screenshots

![Total Files](screenshots/totalfiles.png)
![Categories](screenshots/categories.png)
![Total Size](screenshots/totalsize.png)
![Duplicates](screenshots/duplicates.png)

---

## Features

- **Folder Scanner** — Recursively scans any folder and collects full file metadata
- **Dashboard Cards** — Live stats for Total Files, Categories, Total Size, and Duplicates
- **File Categorization** — Automatically groups files into categories (Images, Documents, Videos, Audio, Code, Archives, and more)
- **Category View** — Click any dashboard card to filter and explore files by category
- **Size Summary** — See storage usage broken down by category
- **Organize** — Moves files into named category subfolders in one click
- **Undo Organization** — Restores every moved file back to its original location safely
- **Duplicate Detection** — Identifies duplicate files using SHA-256 content hashing
- **Dark Mode UI** — Clean professional dark interface built with CustomTkinter
- **Error Safe** — All operations handle permission errors, missing files, and naming conflicts without crashing

---

## Project Structure

```
Smart-File-Organizer/
├── app/
│   ├── main.py                  # Entry point
│   ├── core/
│   │   ├── scanner.py           # Folder scanning and file metadata
│   │   ├── organizer.py         # File organization and undo logic
│   │   ├── config.py            # Category definitions and settings
│   │   └── logger.py            # Logging utility
│   └── ui/
│       ├── main_window.py       # Main application window
│       ├── dashboard.py         # Dashboard card components
│       ├── menu_bar.py          # Menu bar
│       └── status_bar.py        # Status bar
├── config/
│   └── settings.json            # App configuration
├── tests/                       # Unit tests
├── requirements.txt
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| GUI Framework | CustomTkinter |
| File Operations | os, shutil (stdlib) |
| Duplicate Detection | hashlib SHA-256 |
| Architecture | Modular — core logic separated from UI |

---

## Installation

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
python app/main.py
```

---

## Usage

1. Click **Select Folder** to choose the folder you want to organize
2. Click **Scan** to analyze all files in the folder
3. Review the dashboard — Total Files, Categories, Total Size, Duplicates
4. Click any dashboard card to explore files by category
5. Click **Organize** to move files into category subfolders
6. Click **Undo** at any time to restore all files to their original locations

---

## How Undo Works

Every time you organize a folder, the app records the exact source and destination path of every file that was moved. When you click **Undo**, each file is moved back to its original location. If the original directory no longer exists, it is recreated automatically. Files are never deleted and existing files are never overwritten.

---

## Supported File Categories

| Category | Extensions |
|---|---|
| Images | jpg, jpeg, png, gif, bmp, svg, webp, ico |
| Documents | pdf, doc, docx, txt, xls, xlsx, ppt, pptx, csv |
| Videos | mp4, mkv, avi, mov, wmv, flv, webm |
| Audio | mp3, wav, flac, aac, ogg, m4a |
| Code | py, js, ts, html, css, java, c, cpp, json, xml |
| Archives | zip, rar, tar, gz, 7z |
| Other | Everything else |

---

## Contributing

This project is open source and built for learning. Feel free to fork it, open issues, or submit pull requests.

---

## Author

**Haris Khan**
- GitHub: [@Haris-Khan-pro](https://github.com/Haris-Khan-pro)

---

## License

This project is open source — see the [LICENSE](LICENSE) file for details.

---

*Built as part of a 50-day Python project sprint.*
