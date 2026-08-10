# 📁 Smart File Organizer Pro

A Python desktop utility that recursively scans a folder, categorizes every file by type, detects content-identical duplicates via SHA-256 hashing, and moves files into organized category subfolders — all with a one-click undo.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-brightgreen)
![Tests](https://img.shields.io/badge/Tests-35%20unit%20tests-success)
![Status](https://img.shields.io/badge/Status-Complete-blue)
![License](https://img.shields.io/badge/License-Unlicensed-lightgrey)

---

## 📖 Project Overview

Most people's Downloads or Desktop folders slowly turn into chaos — files of every type piled together with no structure, and multiple copies of the same file scattered across subfolders. Smart File Organizer solves this with a lightweight desktop GUI that does the cleanup work for you.

What makes this project technically interesting is not just what it does, but how it does it:

- **Two-phase duplicate detection** — file size is used as a cheap first filter so SHA-256 hashing is only computed for files that could actually be duplicates. This avoids hashing every file on disk unnecessarily.
- **Operation ID–based stale result protection** — each scan, organize, and undo operation is assigned an incrementing ID. If a new operation starts before an older background worker finishes, the older result is silently discarded rather than overwriting newer state. This prevents race conditions without using locks in the UI layer.
- **Non-destructive organization** — files are never silently overwritten. Every collision produces a numbered suffix (`name_1.ext`, `name_2.ext`...) and every move is recorded for undo.

---

## ✨ Features

| Feature | Description |
|---|---|
| Recursive scanning | Walks all subdirectories; skips symbolic links to avoid loops |
| File categorization | Maps 50+ extensions across 8 categories; unknown types go to `Other` |
| Two-phase duplicate detection | Groups by file size first, then confirms with SHA-256 content hash |
| Dashboard summary | Four clickable cards: Total Files, Categories, Total Size, Duplicates |
| Category browser | Click any category to filter the file list to that type |
| Size summary | Per-category breakdown of total disk usage |
| Duplicate viewer | Groups duplicates with ORIGINAL / DUPLICATE labels and per-file sizes |
| Safe organization | Moves files into category subfolders; collision-safe numbered suffix |
| Undo | Restores all moved files to their original paths in one action |
| Undo conflict protection | Blocks restoration if the original path is already occupied |
| Background threading | Scan, organize, and undo run on daemon threads; GUI stays responsive |
| Stale result protection | Operation ID counter prevents old worker results from corrupting state |
| File logging | Writes INFO+ events to `logs/smart_file_organizer.log` |
| Console fallback | Falls back to WARNING+ console output if the log file is unavailable |
| Partial failure reporting | A failed file does not abort the remaining operation |

---

## 🏗️ Architecture

The project separates filesystem logic from the GUI across two distinct layers.

```
┌─────────────────────────────────────────────────────┐
│                  Presentation Layer                 │
│            app/ui/main_window.py                    │
│   Toolbar · Dashboard Cards · File Table · Status   │
└───────────────────────┬─────────────────────────────┘
                        │ calls
┌───────────────────────▼─────────────────────────────┐
│                   Core Logic Layer                  │
│                                                     │
│   app/core/scanner.py       app/core/organizer.py   │
│   ─────────────────────     ────────────────────    │
│   scan()                    organize()               │
│   find_duplicates()         undo_organization()      │
│   calculate_file_hash()                             │
│   get_category()                                    │
└───────────────────────┬─────────────────────────────┘
                        │ uses
┌───────────────────────▼─────────────────────────────┐
│               Supporting Services                   │
│    app/core/logger.py     app/core/config.py        │
└───────────────────────┬─────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────┐
│              Operating System Filesystem             │
└─────────────────────────────────────────────────────┘
```

### Module Responsibilities

| Module | Role |
|---|---|
| `app/main.py` | Entry point — instantiates `MainWindow` and starts the event loop |
| `app/core/scanner.py` | File discovery, extension categorization, SHA-256 duplicate detection |
| `app/core/organizer.py` | File movement into category folders, collision handling, undo restoration |
| `app/core/logger.py` | Configures named logger with file handler and console fallback |
| `app/core/config.py` | App name, version, window geometry, log file path |
| `app/ui/main_window.py` | Full UI: toolbar, dashboard, file table, background threading, state management |

> **Note:** `app/ui/dashboard.py`, `app/ui/menu_bar.py`, and `app/ui/status_bar.py` exist as placeholder module files. All active UI logic is implemented in `main_window.py`.

📐 **Editable architecture diagram:** `docs/architecture.drawio`

---

## 🔄 How It Works

### Complete Workflow

```
User
 │
 ▼
📁 Select Folder          →  filedialog.askdirectory()
                              Resets all state: files, duplicates, undo history
 │
 ▼
🔍 Scan                   →  Spawns daemon thread with operation_id
                              os.walk() — recursive, no symlinks followed
                              Per-file: path, name, extension, size, category
 │
 ▼
Categorization            →  Extension lookup against FILE_CATEGORIES dict
                              Case-insensitive; unrecognized → "Other"
 │
 ▼
Duplicate Detection       →  Group by file size (cheap filter)
                              Hash same-size files with SHA-256 (1 MB chunks)
                              Groups with matching hash = duplicates
 │
 ▼
Dashboard Update          →  after() callback: Total Files, Categories,
                              Total Size (MB), Duplicate count
                              Stale result check — discards old operation IDs
 │
 ▼
📂 Organize               →  User confirms via dialog
                              Spawns daemon thread with new operation_id
                              Creates category subfolder if needed
                              Checks source still exists before each move
                              Resolves filename collisions with suffix counter
                              Records every move: source + destination
 │
 ▼
Post-Organize Refresh     →  Automatically re-scans folder
                              Rebuilds dashboard and file list
                              Enables Undo button if moves succeeded
 │
 ▼
↩ Undo                    →  User confirms via dialog
                              Spawns daemon thread with new operation_id
                              Verifies file still exists at destination
                              Checks original path is unoccupied
                              Restores: destination → source
                              Remaining undoable records are kept on partial failure
```

📐 **Editable workflow diagram:** `docs/workflow.drawio`

---

## 🔍 Scanning & Duplicate Detection

### Scan Algorithm

`scan(folder_path)` uses `os.walk()` with `followlinks=False`. Symbolic link directories are additionally filtered from the `directories` list at each level to prevent directory-level symlink traversal. Symbolic link files are individually checked and skipped. Files that raise `PermissionError`, `FileNotFoundError`, or `OSError` during `os.path.getsize()` are logged as warnings and skipped without aborting the scan.

Each discovered file produces a record:

```python
{
    "name":      "report.pdf",
    "path":      "/home/user/docs/report.pdf",
    "extension": ".pdf",
    "size":      204800,
    "category":  "Documents"
}
```

### Why Size-First Duplicate Detection?

Size alone cannot confirm that two files have identical content — a trivial example is two files both containing exactly 4 bytes but with different byte values. However, two files with different sizes are guaranteed not to be identical. Grouping by size first means SHA-256 is only computed for files that are at least candidates for duplication, which significantly reduces I/O for large folders with many unique file sizes.

### Two-Phase Detection Flow

```
All scanned files
        │
        ▼
Group by file size
        │
        ├── Groups with only 1 file ──► Skipped (cannot be duplicates)
        │
        └── Groups with 2+ files
                │
                ▼
        Compute SHA-256 for each file (1 MB chunks)
                │
                ▼
        Sub-group by hash
                │
                ├── Sub-groups with only 1 file ──► Not duplicates (same size, different content)
                │
                └── Sub-groups with 2+ files ──► Duplicate group
```

The result is a list of duplicate groups:

```python
[
    {
        "hash": "e3b0c44298fc1c149afb...",
        "size": 204800,
        "files": [
            {"name": "report.pdf",    "path": "/folder/report.pdf"},
            {"name": "report copy.pdf", "path": "/folder/backup/report copy.pdf"}
        ]
    }
]
```

---

## 📦 File Organization

`organize(folder_path, files)` processes every file record from the scanner:

1. Validates that the source path still exists on disk before attempting any move.
2. Creates the category subfolder inside `folder_path` using `os.makedirs(exist_ok=True)`.
3. Detects filename collisions at the destination and increments a counter suffix until a free name is found:

```
photo.jpg        →  already exists
photo_1.jpg      →  already exists
photo_2.jpg      →  free — file is moved here
```

4. Calls `shutil.move(source, destination)`.
5. Records the move with its source and destination paths.
6. On error for an individual file, appends to the errors list and continues with remaining files.

A partial failure does not abort the operation. Files that were successfully moved remain recorded and can be individually undone.

**Return structure:**

```python
{
    "moved": [
        {
            "name":        "photo.jpg",
            "category":    "Images",
            "source":      "/folder/photo.jpg",
            "destination": "/folder/Images/photo.jpg"
        }
    ],
    "errors": []
}
```

---

## ↩️ Undo System

`undo_organization(moved_files)` accepts the move records from the last organize operation.

For each record:

1. Verifies the file still exists at `destination`.
2. Recreates the original directory at `os.path.dirname(source)` if needed.
3. **Checks that the original path is unoccupied** — if a file already exists at `source`, the restore is blocked and reported as an error. Nothing is silently overwritten.
4. Calls `shutil.move(destination, source)`.

If some files restore successfully and others fail, the UI keeps the failed records as the remaining undo history. Only fully successful undo operations clear the undo state entirely.

**Scenario coverage:**

| Scenario | Behaviour |
|---|---|
| File still at destination | Restored to source |
| File missing from destination | Error reported, skipped |
| Source path already occupied | Error reported, not overwritten |
| Invalid history record | Error reported, operation continues |
| Partial success | Remaining undoable records are preserved |

---

## 🧵 Background Processing

Scan, organize, and undo operations each run on a `daemon=True` background thread. Tkinter requires all widget updates to happen on the main GUI thread, so no UI calls are made from worker threads directly.

```
GUI Thread
    │
    ├── User triggers Scan ──────────► Worker Thread
    │    operation_id = N                  │
    │                                      ▼
    │                               scan(folder_path)
    │                                      │
    │                                      ▼
    │                           self.after(0, _apply_scan_results,
    │                                         operation_id, results)
    │                                      │
    ◄──────────────────────────────────────┘
    │
    ▼
_apply_scan_results checks:
    if operation_id != self._latest_operation_id:
        return   ← stale result, discard silently
    else:
        update UI
```

**Stale result protection:** Each time the user starts any operation (`_begin_operation()`), `_operation_counter` is incremented and stored as `_latest_operation_id`. When a worker finishes and schedules its `after()` callback, it passes its own `operation_id`. The callback checks `_is_current_operation(operation_id)` before touching any state. If the user triggered a new operation while the old worker was still running, the old callback is a no-op.

This means the user can safely click Scan multiple times in quick succession, or select a new folder before the previous scan returns, without producing corrupted UI state.

---

## 🛡️ Safety & Reliability

| Protection | Implementation |
|---|---|
| No silent overwrites | Collision suffix counter checked in a `while os.path.exists()` loop |
| Source validation before move | `os.path.isfile(source_path)` checked per file before `shutil.move()` |
| Undo conflict protection | `os.path.exists(source)` checked before restore; blocks if occupied |
| Partial failure tolerance | Per-file `try/except`; failed files do not abort remaining operations |
| Symlink traversal prevention | `followlinks=False` in `os.walk()`; symlink dirs filtered; symlink files skipped |
| Stale worker results | Operation ID comparison in all `after()` callbacks |
| Logging fallback | `PermissionError` on file log creation → falls back to console-only |
| OSError recovery | Top-level `os.walk()` wrapped in `try/except OSError` |

**Honest limitations:** This is a filesystem utility that moves files. It is not transactional. If the process is interrupted mid-organize, files moved so far remain in their category folders. The undo history is in-memory only and does not survive a restart. The app is designed for local desktop use, not for concurrent access or remote filesystems.

---

## 📝 Logging

`app/core/logger.py` configures a named logger (`smart_file_organizer`) on first import.

**Log levels:**

| Level | Handler | Events |
|---|---|---|
| INFO | File (`logs/smart_file_organizer.log`) | Scan start/complete, organize start/complete, undo start/complete, file moves, restores, folder selection, startup |
| WARNING | File + Console | Skipped files, missing sources, undo conflicts, invalid inputs, symlink skips |
| ERROR | File + Console | Move failures, undo failures, category folder creation failures, scan-level OSErrors |

Format: `YYYY-MM-DD HH:MM:SS LEVEL message`

If the log directory cannot be created or the log file cannot be opened (e.g., permission denied), the WARNING and above events are still emitted to the console via `StreamHandler`. File content is not logged — only paths, operation outcomes, and error messages.

---

## 🧪 Testing

35 unit tests across 4 test modules. All core filesystem logic is tested with `tempfile.TemporaryDirectory` — no mocking of the filesystem itself.

| Test Module | Coverage |
|---|---|
| `test_scanner.py` | SHA-256 hashing, duplicate detection, category mapping, case-insensitive extensions, nested directories, empty folders, invalid paths, multiple duplicate groups, same-size different-content (no false positives), duplicate counts |
| `test_organizer.py` | Move to category folder, undo restore, collision renaming (`_1` suffix), missing source error, partial failure on mixed input, repeated undo attempt, undo conflict with occupied source, invalid history input, missing destination |
| `test_gui_state.py` | Initial button state (all disabled), folder selection enables scan/organize, undo enabled only with valid history, stale operation ID rejection, logging fallback when file handler fails |
| `test_packaging.py` | `pyproject.toml` exists, project name and version match, entry point script is declared |

```bash
# Run all tests
python -m unittest discover -s tests -v
```

---

## ⚙️ Installation

**Requirements:** Python 3.10 or higher.

```bash
# 1. Clone the repository
git clone <your-repository-url>
cd SmartFileOrganizer

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate it
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

**Dependencies:**

| Package | Version | Purpose |
|---|---|---|
| `customtkinter` | >=2.7.0 | Dark mode desktop UI framework built on Tkinter |

All other functionality uses the Python standard library (`os`, `hashlib`, `shutil`, `threading`, `logging`, `tempfile`, `pathlib`, `unittest`).

---

## 🚀 Running the Application

```bash
python -m app.main
```

The window opens at 1200×720, centered on screen. Minimum resizable size is 900×600.

---

## 📂 Project Structure

```
SmartFileOrganizer/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # App name, version, window size, log path
│   │   ├── logger.py            # Named logger with file + console handlers
│   │   ├── organizer.py         # organize() and undo_organization()
│   │   └── scanner.py           # scan(), find_duplicates(), get_category()
│   └── ui/
│       ├── __init__.py
│       ├── main_window.py       # Full UI and threading logic
│       ├── dashboard.py         # Placeholder module (not yet implemented)
│       ├── menu_bar.py          # Placeholder module (not yet implemented)
│       └── status_bar.py        # Placeholder module (not yet implemented)
├── config/
│   └── settings.json            # Reserved for future runtime configuration
├── docs/
│   ├── architecture.drawio      # Editable architecture diagram
│   └── workflow.drawio          # Editable workflow diagram
├── logs/                        # Runtime log output (gitignored)
├── tests/
│   ├── __init__.py
│   ├── test_gui_state.py
│   ├── test_organizer.py
│   ├── test_packaging.py
│   └── test_scanner.py
├── pyproject.toml
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🗂️ Supported File Categories

| Category | Extensions |
|---|---|
| Images | `.jpg` `.jpeg` `.png` `.gif` `.bmp` `.webp` `.svg` `.ico` `.tiff` `.tif` |
| Documents | `.pdf` `.doc` `.docx` `.txt` `.rtf` `.odt` `.xls` `.xlsx` `.csv` `.ppt` `.pptx` |
| Videos | `.mp4` `.mkv` `.avi` `.mov` `.wmv` `.flv` `.webm` `.m4v` |
| Audio | `.mp3` `.wav` `.flac` `.aac` `.ogg` `.m4a` `.wma` |
| Code | `.py` `.js` `.ts` `.jsx` `.tsx` `.html` `.css` `.java` `.cpp` `.c` `.h` `.hpp` `.cs` `.php` `.go` `.rs` `.rb` `.sql` |
| Archives | `.zip` `.rar` `.7z` `.tar` `.gz` `.bz2` |
| Executables | `.exe` `.msi` `.bat` `.cmd` `.sh` |
| Other | Any unrecognized extension |

Extension matching is case-insensitive. `.JPG`, `.jpg`, and `.Jpg` all map to `Images`.

---

## 📸 Screenshots

| 📄 Total Files View | 📁 Categories View |
|---|---|
| ![Total Files](screenshots/totalfiles.png) | ![Categories](screenshots/categories.png) |
| Dashboard showing total file count after a scan. Click the card to list all discovered files with their type and size. | Files grouped by category. Click any category row to filter the file table to that type only. |

| 💾 Total Size View | ⚠️ Duplicates View |
|---|---|
| ![Total Size](screenshots/totalsize.png) | ![Duplicates](screenshots/duplicates.png) |
| Storage usage broken down per category — useful for spotting which file types are consuming the most disk space. | Duplicate groups detected via SHA-256 content hashing. Each group labels the original and every duplicate copy. |

---

## ⚠️ Limitations

- **In-memory undo only.** Operation history is lost when the application closes. There is no persistent undo log.
- **Rule-based categorization.** Files are sorted by extension, not content type detection. A `.txt` file containing Python code goes to Documents, not Code.
- **Single-operation undo.** Only the most recent organize operation can be undone. Earlier operations are no longer undoable once a new organize runs.
- **Local filesystem only.** The app assumes a responsive local filesystem. Network drives and remote mounts may produce degraded performance or unexpected errors.
- **No packaging tested.** `pyproject.toml` declares a `smart-file-organizer` entry point script, but PyInstaller or platform-specific installer creation has not been tested.
- **No concurrent access protection.** If the target folder is modified by another process while the app is running, the app will detect individual missing files and report them as errors rather than crashing.

---

## 🗺️ Future Improvements

- User-configurable category rules (add/remove extensions or categories at runtime)
- Per-file progress indicator during large organize operations
- Persistent undo history (session log file)
- Drag-and-drop folder selection
- Multi-operation undo stack
- PyInstaller packaging with a Windows installer

---

## 👨‍💻 Author

**Haris Khan**

A CS graduate building real-world Python and full-stack projects to demonstrate engineering depth through code rather than credentials.

| | |
|---|---|
| 🐙 GitHub | [@Haris-Khan-pro](https://github.com/Haris-Khan-pro) |
| 📁 This Project | [Smart-File-Organizer](https://github.com/Haris-Khan-pro/Smart-File-Organizer) |
| 🏃 Sprint | Built during a 50-day Python project sprint — 2 production-quality project per day |

> This project demonstrates Python desktop engineering fundamentals: layered architecture, background threading with race condition protection, two-phase duplicate detection, non-destructive filesystem operations, and a fully unit-tested core logic layer.

---

## 📄 License

This project is currently **unlicensed**. It is shared for portfolio and educational purposes. If you intend to redistribute or build on it, add a formal license file.
