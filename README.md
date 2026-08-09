# Smart File Organizer

A lightweight desktop utility for scanning a folder, categorizing files, detecting duplicates, and moving files into category-based folders without losing the ability to undo the operation.

## Purpose

Smart File Organizer was built as a practical Python desktop app for everyday file cleanup. It helps users:

- scan a selected folder recursively
- review totals by category and file size
- detect duplicate files by SHA-256 content hash
- move files into organized category folders
- restore files with an undo action if needed

## Features

- recursive folder scanning
- category detection for images, documents, video, audio, code, archives, executables, and other files
- duplicate detection using SHA-256 hashing
- dashboard summary for files, categories, total size, and duplicates
- safe collision handling when destination filenames already exist
- undo support for returning files to their original locations
- clear status messages and logging for operational diagnostics

## Screenshots

No screenshots are currently committed to this repository. Screenshot capture is not automated in the current environment, so this section intentionally avoids broken image references until a real desktop capture is added.

## Architecture

The project keeps the filesystem logic separate from the GUI:

- app/main.py: application entry point
- app/core/scanner.py: scan and duplicate detection logic
- app/core/organizer.py: move and undo logic
- app/ui/main_window.py: CustomTkinter interface and user actions
- app/core/logger.py: application logging
- app/core/config.py: shared metadata and constants
- tests/: unit tests for scan and organization behavior

## Project Structure

```text
SmartFileOrganizer/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── logger.py
│   │   ├── organizer.py
│   │   └── scanner.py
│   └── ui/
│       ├── __init__.py
│       ├── main_window.py
│       ├── dashboard.py
│       ├── menu_bar.py
│       └── status_bar.py
├── config/
│   └── settings.json
├── logs/
├── pyproject.toml
├── tests/
│   ├── __init__.py
│   ├── test_gui_state.py
│   ├── test_organizer.py
│   ├── test_packaging.py
│   └── test_scanner.py
├── README.md
├── requirements.txt
├── .gitignore
└── .venv/
```

## Technologies

- Python 3.10+
- CustomTkinter
- standard library modules such as os, hashlib, shutil, logging, tempfile, unittest

## Installation

1. Clone the repository.
2. Create a virtual environment.
3. Activate the environment.
4. Install requirements.

Example:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the Application

```bash
python -m app.main
```

## Running Tests

```bash
python -m unittest discover -s tests -v
```

## Supported File Categories

The app currently recognizes these categories:

- Images: jpg, jpeg, png, gif, bmp, webp, svg, ico, tiff, tif
- Documents: pdf, doc, docx, txt, rtf, odt, xls, xlsx, csv, ppt, pptx
- Videos: mp4, mkv, avi, mov, wmv, flv, webm, m4v
- Audio: mp3, wav, flac, aac, ogg, m4a, wma
- Code: py, js, ts, jsx, tsx, html, css, java, cpp, c, h, hpp, cs, php, go, rs, rb, sql
- Archives: zip, rar, 7z, tar, gz, bz2
- Executables: exe, msi, bat, cmd, sh
- Other: unrecognized extensions

## Duplicate Detection

Duplicate files are identified by grouping files with the same file size and confirming identical SHA-256 hashes. This avoids false positives caused by same-size but different-content files.

## Organization Behavior

When the user organizes a folder:

- files are moved into category subfolders inside the selected folder
- duplicate destination names are resolved with a safe numbered suffix such as name_1.ext
- files that disappear or cannot be moved are reported as errors without crashing the operation
- successful moves remain available for undo

## Undo Behavior

Undo restores moved files back to their original location when possible. The app blocks restoration if the original location already exists to avoid overwriting user files. It reports conflicts clearly instead of silently discarding them.

## Safety Limitations

This project is intentionally conservative around file safety. It does not overwrite existing files and it does not silently continue after critical filesystem errors. Some limitations remain:

- operations depend on file system permissions
- a folder can change while the app is running
- the GUI is designed for desktop use, not for remote or headless automation
- large scans and operations are executed on background worker threads, but they still depend on local filesystem responsiveness and the active desktop environment

## Known Limitations

- the project is a desktop utility, not a full enterprise document manager
- file categorization is rule-based and extension-based
- layout and styling are intentionally straightforward rather than highly customized
- the app is best suited for local folder cleanup on a personal machine

## Future Improvements

Possible follow-up improvements include:

- better per-file progress indicators
- user-configurable category rules
- export/import of organization history
- drag-and-drop folder support
- packaged Windows installer creation with PyInstaller or a similar tool

## License

This project is provided as a personal portfolio project and does not currently declare a formal open-source license. If you plan to share or publish it publicly, add a license file and include the chosen terms.

## Notes

This project is intended to show good Python desktop engineering habits: validation, safe filesystem behavior, explicit error reporting, and unit-tested core logic. It is not a replacement for a full production file management platform.
