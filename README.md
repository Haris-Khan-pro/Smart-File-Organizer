# Smart File Organizer Pro

> A desktop file organization and analysis application built with Python and CustomTkinter.

Smart File Organizer Pro scans a selected folder, analyzes its files, categorizes them, calculates storage usage, detects duplicate files using SHA-256 hashing, organizes files into category folders, and provides an Undo system to restore organized files.

---

## 📸 Project Preview

<!-- Replace the image path below with your project screenshot -->

![Smart File Organizer Pro](docs/images/dashboard.png)

---

## ✨ Features

### 📁 Folder Selection

Select any folder from your computer and use it as the workspace for scanning and organization.

### 🔍 File Scanner

The scanner analyzes files inside the selected folder and collects information such as:

- File name
- Extension
- File size
- Category
- File path

### 📊 Dashboard

The dashboard provides four main statistics:

- Total Files
- Categories
- Total Size
- Duplicates

Each dashboard card can be selected to display its corresponding information.

### 📂 Categories

Files are grouped according to their detected category.

Users can click a category to view the files belonging to that category.

### 💾 Storage Analysis

The Total Size section provides a breakdown of storage usage by category.

### ⚠ Duplicate Detection

Smart File Organizer Pro automatically checks for duplicate files after scanning.

Duplicate detection uses a two-stage process:

1. Files are grouped by file size.
2. Files with matching sizes are compared using SHA-256 hashes.

This avoids treating files as duplicates simply because they have the same filename or size.

The application displays:

- Number of duplicate groups
- Number of duplicate files
- Original file
- Duplicate files
- File size

### 📦 File Organization

Files can be organized into category folders.

The application keeps track of moved files so the operation can be reversed.

### ↩ Undo Organization

The Undo system restores files to their original locations after organization.

The application also handles partial failures during restoration.

### 🔄 Automatic Refresh

After organization or undo operations, the application rescans the folder and updates the dashboard automatically.

---

# 🖥️ Application Flow

```text
Select Folder
      │
      ▼
    Scan
      │
      ├──────────────► File Analysis
      │
      ├──────────────► Category Detection
      │
      ├──────────────► Size Calculation
      │
      └──────────────► Duplicate Detection
                              │
                              ▼
                     SHA-256 Verification
                              │
                              ▼
                       Dashboard Results
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
         Total Files      Categories      Total Size
              │
              ▼
        Duplicate View
              
              │
              ▼
          Organize
              │
              ▼
            Undo