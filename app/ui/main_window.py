import os
import hashlib

import customtkinter as ctk
from tkinter import filedialog, messagebox

from core.scanner import scan
from core.organizer import organize, undo_organization


class MainWindow(ctk.CTk):

    def __init__(self):

        # ==========================================
        # Appearance
        # ==========================================

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # ==========================================
        # Main Window
        # ==========================================

        super().__init__()

        self.title("Smart File Organizer Pro")
        self.geometry("1200x720")
        self.minsize(900, 600)

        # ==========================================
        # Application State
        # ==========================================

        self.selected_folder = ""

        # Files returned by scanner
        self.scanned_files = []

        # Duplicate groups detected during scan
        self.duplicate_groups = []

        # Number of duplicate files
        self.duplicate_count = 0

        # Last successful organization result
        self.last_organization = None

        # ==========================================
        # Center Window
        # ==========================================

        self.center_window()

        # ==========================================
        # Create Interface
        # ==========================================

        self.create_layout()

    # ==========================================
    # Window Position
    # ==========================================

    def center_window(self):

        self.update_idletasks()

        width = 1200
        height = 720

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.geometry(
            f"{width}x{height}+{x}+{y}"
        )

    # ==========================================
    # Main Layout
    # ==========================================

    def create_layout(self):

        # ==========================================
        # Toolbar
        # ==========================================

        self.toolbar = ctk.CTkFrame(
            self,
            height=70,
            corner_radius=0
        )

        self.toolbar.pack(
            fill="x"
        )

        self.create_toolbar()

        # ==========================================
        # Main Content
        # ==========================================

        self.content = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.content.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        self.create_dashboard()
        self.create_file_table()

        # ==========================================
        # Status Bar
        # ==========================================

        self.statusbar = ctk.CTkFrame(
            self,
            height=35,
            corner_radius=0
        )

        self.statusbar.pack(
            fill="x"
        )

        self.create_statusbar()

    # ==========================================
    # Toolbar
    # ==========================================

    def create_toolbar(self):

        # ==========================================
        # Select Folder
        # ==========================================

        self.select_button = ctk.CTkButton(
            self.toolbar,
            text="📁 Select Folder",
            width=150,
            command=self.select_folder
        )

        self.select_button.pack(
            side="left",
            padx=(20, 10),
            pady=15
        )

        # ==========================================
        # Scan
        # ==========================================

        self.scan_button = ctk.CTkButton(
            self.toolbar,
            text="🔍 Scan",
            width=120,
            state="disabled",
            command=self.scan_folder
        )

        self.scan_button.pack(
            side="left",
            padx=10,
            pady=15
        )

        # ==========================================
        # Organize
        # ==========================================

        self.organize_button = ctk.CTkButton(
            self.toolbar,
            text="📂 Organize",
            width=140,
            state="disabled",
            command=self.organize_files
        )

        self.organize_button.pack(
            side="left",
            padx=10,
            pady=15
        )

        # ==========================================
        # Undo
        # ==========================================

        self.undo_button = ctk.CTkButton(
            self.toolbar,
            text="↩ Undo",
            width=120,
            state="disabled",
            command=self.undo_files
        )

        self.undo_button.pack(
            side="left",
            padx=10,
            pady=15
        )

    # ==========================================
    # Dashboard
    # ==========================================

    def create_dashboard(self):

        # ==========================================
        # Selected Folder
        # ==========================================

        self.folder_frame = ctk.CTkFrame(
            self.content,
            height=60
        )

        self.folder_frame.pack(
            fill="x",
            pady=(0, 15)
        )

        self.folder_label = ctk.CTkLabel(
            self.folder_frame,
            text="No folder selected",
            font=("Segoe UI", 14),
            anchor="w"
        )

        self.folder_label.pack(
            fill="x",
            padx=20,
            pady=15
        )

        # ==========================================
        # Dashboard Cards
        # ==========================================

        self.cards_frame = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )

        self.cards_frame.pack(
            fill="x",
            pady=(0, 15)
        )

        cards = [
            ("📄", "Total Files", "0"),
            ("📁", "Categories", "0"),
            ("💾", "Total Size", "0 MB"),
            ("⚠", "Duplicates", "0"),
        ]

        self.card_values = {}
        self.card_frames = {}

        for icon, title, value in cards:

            card = ctk.CTkFrame(
                self.cards_frame,
                height=105,
                cursor="hand2"
            )

            card.pack(
                side="left",
                expand=True,
                fill="both",
                padx=8
            )

            self.card_frames[title] = card

            # ==========================================
            # Icon
            # ==========================================

            icon_label = ctk.CTkLabel(
                card,
                text=icon,
                font=("Segoe UI Emoji", 25),
                cursor="hand2"
            )

            icon_label.pack(
                pady=(10, 2)
            )

            # ==========================================
            # Title
            # ==========================================

            title_label = ctk.CTkLabel(
                card,
                text=title,
                font=("Segoe UI", 14, "bold"),
                cursor="hand2"
            )

            title_label.pack()

            # ==========================================
            # Value
            # ==========================================

            value_label = ctk.CTkLabel(
                card,
                text=value,
                font=("Segoe UI", 20, "bold"),
                cursor="hand2"
            )

            value_label.pack(
                pady=(2, 8)
            )

            self.card_values[title] = value_label

            # ==========================================
            # Make Card Clickable
            # ==========================================

            card.bind(
                "<Button-1>",
                lambda event, name=title:
                self.card_clicked(name)
            )

            icon_label.bind(
                "<Button-1>",
                lambda event, name=title:
                self.card_clicked(name)
            )

            title_label.bind(
                "<Button-1>",
                lambda event, name=title:
                self.card_clicked(name)
            )

            value_label.bind(
                "<Button-1>",
                lambda event, name=title:
                self.card_clicked(name)
            )

    # ==========================================
    # Dashboard Card Click
    # ==========================================

    def card_clicked(self, card_name):

        if card_name == "Total Files":

            self.display_files(
                self.scanned_files
            )

            self.status_label.configure(
                text=(
                    f"Showing all files • "
                    f"{len(self.scanned_files)} files"
                )
            )

        elif card_name == "Categories":

            self.display_categories()

            self.status_label.configure(
                text="Showing file categories"
            )

        elif card_name == "Total Size":

            self.display_size_summary()

            self.status_label.configure(
                text="Showing size summary"
            )

        elif card_name == "Duplicates":

            self.display_duplicates(
                self.duplicate_groups
            )

            if self.duplicate_count == 0:

                self.status_label.configure(
                    text="No duplicate files found"
                )

            else:

                self.status_label.configure(
                    text=(
                        f"Showing {self.duplicate_count} "
                        f"duplicate files"
                    )
                )

    # ==========================================
    # Duplicate Detection
    # ==========================================

    def detect_duplicates(self, show_results=False):

        self.duplicate_groups = []
        self.duplicate_count = 0

        if not self.scanned_files:

            self.card_values["Duplicates"].configure(
                text="0"
            )

            if show_results:

                self.show_empty_message(
                    "No files available for duplicate detection"
                )

            return

        try:

            # ==========================================
            # Step 1 — Group Files By Size
            # ==========================================

            size_groups = {}

            for file_data in self.scanned_files:

                file_path = file_data.get("path")

                if not file_path:
                    continue

                try:

                    if not os.path.isfile(file_path):
                        continue

                    size = file_data.get(
                        "size",
                        0
                    )

                    size_groups.setdefault(
                        size,
                        []
                    ).append(file_data)

                except OSError:

                    continue

            # ==========================================
            # Step 2 — Hash Files With Same Size
            # ==========================================

            duplicate_groups = []

            for size, files in size_groups.items():

                if len(files) < 2:
                    continue

                hash_groups = {}

                for file_data in files:

                    file_path = file_data.get("path")

                    if not file_path:
                        continue

                    try:

                        file_hash = self.calculate_file_hash(
                            file_path
                        )

                        hash_groups.setdefault(
                            file_hash,
                            []
                        ).append(file_data)

                    except (
                        OSError,
                        PermissionError
                    ):

                        continue

                # ==========================================
                # Store Actual Duplicate Groups
                # ==========================================

                for file_hash, matching_files in hash_groups.items():

                    if len(matching_files) > 1:

                        duplicate_groups.append({
                            "hash": file_hash,
                            "size": size,
                            "files": matching_files
                        })

            # ==========================================
            # Calculate Duplicate Count
            # ==========================================

            duplicate_count = 0

            for group in duplicate_groups:

                duplicate_count += (
                    len(group["files"]) - 1
                )

            # ==========================================
            # Save Results
            # ==========================================

            self.duplicate_groups = duplicate_groups
            self.duplicate_count = duplicate_count

            # ==========================================
            # Update Dashboard Immediately
            # ==========================================

            self.card_values["Duplicates"].configure(
                text=str(duplicate_count)
            )

            # ==========================================
            # Optionally Display Results
            # ==========================================

            if show_results:

                self.display_duplicates(
                    duplicate_groups
                )

        except Exception as error:

            self.card_values["Duplicates"].configure(
                text="0"
            )

            self.status_label.configure(
                text="Duplicate detection failed"
            )

            messagebox.showerror(
                "Duplicate Detection Error",
                str(error)
            )

    # ==========================================
    # Calculate SHA-256 File Hash
    # ==========================================

    def calculate_file_hash(self, file_path):

        sha256 = hashlib.sha256()

        with open(
            file_path,
            "rb"
        ) as file:

            while True:

                chunk = file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                sha256.update(chunk)

        return sha256.hexdigest()

    # ==========================================
    # Display Duplicate Groups
    # ==========================================

    def display_duplicates(self, duplicate_groups):

        self.clear_file_list()

        # ==========================================
        # No Duplicates
        # ==========================================

        if not duplicate_groups:

            ctk.CTkLabel(
                self.file_list,
                text="✓ No duplicate files found",
                text_color="gray",
                font=("Segoe UI", 14)
            ).pack(
                pady=40
            )

            return

        # ==========================================
        # Summary
        # ==========================================

        total_duplicate_files = sum(
            len(group["files"]) - 1
            for group in duplicate_groups
        )

        summary = ctk.CTkLabel(
            self.file_list,
            text=(
                f"Found {len(duplicate_groups)} duplicate groups • "
                f"{total_duplicate_files} duplicate files"
            ),
            font=("Segoe UI", 14, "bold"),
            anchor="w"
        )

        summary.pack(
            fill="x",
            padx=15,
            pady=(5, 15)
        )

        # ==========================================
        # Duplicate Groups
        # ==========================================

        for index, group in enumerate(
            duplicate_groups,
            start=1
        ):

            group_frame = ctk.CTkFrame(
                self.file_list
            )

            group_frame.pack(
                fill="x",
                pady=5,
                padx=5
            )

            # ==========================================
            # Group Header
            # ==========================================

            group_header = ctk.CTkFrame(
                group_frame
            )

            group_header.pack(
                fill="x"
            )

            group_size = self.format_file_size(
                group["size"]
            )

            ctk.CTkLabel(
                group_header,
                text=(
                    f"Duplicate Group {index}  •  "
                    f"{len(group['files'])} identical files  •  "
                    f"{group_size} each"
                ),
                font=("Segoe UI", 13, "bold"),
                anchor="w"
            ).pack(
                side="left",
                fill="x",
                expand=True,
                padx=15,
                pady=10
            )

            # ==========================================
            # Files
            # ==========================================

            for file_index, file_data in enumerate(
                group["files"]
            ):

                file_row = ctk.CTkFrame(
                    group_frame
                )

                file_row.pack(
                    fill="x",
                    padx=10,
                    pady=2
                )

                # ==========================================
                # Original / Duplicate Label
                # ==========================================

                if file_index == 0:

                    label = "ORIGINAL"

                else:

                    label = "DUPLICATE"

                ctk.CTkLabel(
                    file_row,
                    text=label,
                    width=100,
                    font=("Segoe UI", 11, "bold"),
                    anchor="w"
                ).pack(
                    side="left",
                    padx=10
                )

                # ==========================================
                # File Name
                # ==========================================

                ctk.CTkLabel(
                    file_row,
                    text=file_data.get(
                        "name",
                        "Unknown"
                    ),
                    anchor="w"
                ).pack(
                    side="left",
                    fill="x",
                    expand=True,
                    padx=10
                )

                # ==========================================
                # File Size
                # ==========================================

                ctk.CTkLabel(
                    file_row,
                    text=self.format_file_size(
                        file_data.get(
                            "size",
                            0
                        )
                    ),
                    width=100,
                    anchor="e"
                ).pack(
                    side="left",
                    padx=10
                )

    # ==========================================
    # Display Categories
    # ==========================================

    def display_categories(self):

        self.clear_file_list()

        # ==========================================
        # Header
        # ==========================================

        header = ctk.CTkFrame(
            self.file_list,
            height=50
        )

        header.pack(
            fill="x",
            pady=(0, 8)
        )

        ctk.CTkLabel(
            header,
            text="Category",
            font=("Segoe UI", 13, "bold"),
            anchor="w"
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=15
        )

        ctk.CTkLabel(
            header,
            text="Files",
            font=("Segoe UI", 13, "bold"),
            width=120,
            anchor="center"
        ).pack(
            side="left",
            padx=15
        )

        # ==========================================
        # Category Counts
        # ==========================================

        category_counts = {}

        for file_data in self.scanned_files:

            category = file_data.get(
                "category",
                "Other"
            )

            category_counts[category] = (
                category_counts.get(category, 0) + 1
            )

        # ==========================================
        # No Categories
        # ==========================================

        if not category_counts:

            ctk.CTkLabel(
                self.file_list,
                text="No categories available",
                text_color="gray",
                font=("Segoe UI", 14)
            ).pack(
                pady=40
            )

            return

        # ==========================================
        # Category Rows
        # ==========================================

        for category, count in sorted(
            category_counts.items()
        ):

            row = ctk.CTkFrame(
                self.file_list,
                height=55,
                cursor="hand2"
            )

            row.pack(
                fill="x",
                pady=3
            )

            # ==========================================
            # Category Name
            # ==========================================

            category_label = ctk.CTkLabel(
                row,
                text=f"📁  {category}",
                font=("Segoe UI", 14, "bold"),
                anchor="w",
                cursor="hand2"
            )

            category_label.pack(
                side="left",
                fill="x",
                expand=True,
                padx=15
            )

            # ==========================================
            # File Count
            # ==========================================

            count_label = ctk.CTkLabel(
                row,
                text=str(count),
                font=("Segoe UI", 14, "bold"),
                width=120,
                cursor="hand2"
            )

            count_label.pack(
                side="left",
                padx=15
            )

            # ==========================================
            # Make Entire Row Clickable
            # ==========================================

            row.bind(
                "<Button-1>",
                lambda event, name=category:
                self.show_category_files(name)
            )

            category_label.bind(
                "<Button-1>",
                lambda event, name=category:
                self.show_category_files(name)
            )

            count_label.bind(
                "<Button-1>",
                lambda event, name=category:
                self.show_category_files(name)
            )

        # ==========================================
        # Status
        # ==========================================

        self.status_label.configure(
            text=(
                f"Showing {len(category_counts)} "
                f"categories • "
                f"{len(self.scanned_files)} files"
            )
        )

    # ==========================================
    # File Table
    # ==========================================

    def create_file_table(self):

        self.table_frame = ctk.CTkFrame(
            self.content
        )

        self.table_frame.pack(
            fill="both",
            expand=True
        )

        # ==========================================
        # Table Header
        # ==========================================

        self.table_header = ctk.CTkFrame(
            self.table_frame,
            height=45
        )

        self.table_header.pack(
            fill="x"
        )

        ctk.CTkLabel(
            self.table_header,
            text="File Name",
            font=("Segoe UI", 13, "bold"),
            anchor="w"
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(15, 5)
        )

        ctk.CTkLabel(
            self.table_header,
            text="Type",
            font=("Segoe UI", 13, "bold"),
            width=100
        ).pack(
            side="left",
            padx=5
        )

        ctk.CTkLabel(
            self.table_header,
            text="Size",
            font=("Segoe UI", 13, "bold"),
            width=100
        ).pack(
            side="left",
            padx=(5, 15)
        )

        # ==========================================
        # Scrollable File Area
        # ==========================================

        self.file_list = ctk.CTkScrollableFrame(
            self.table_frame,
            fg_color="transparent"
        )

        self.file_list.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        self.show_empty_message()

    # ==========================================
    # Empty Message
    # ==========================================

    def show_empty_message(
        self,
        text="No files scanned yet"
    ):

        self.clear_file_list()

        ctk.CTkLabel(
            self.file_list,
            text=text,
            text_color="gray",
            font=("Segoe UI", 14)
        ).pack(
            pady=40
        )

    # ==========================================
    # Clear File List
    # ==========================================

    def clear_file_list(self):

        for widget in self.file_list.winfo_children():

            widget.destroy()

    # ==========================================
    # Status Bar
    # ==========================================

    def create_statusbar(self):

        self.status_label = ctk.CTkLabel(
            self.statusbar,
            text="Ready",
            font=("Segoe UI", 12),
            anchor="w"
        )

        self.status_label.pack(
            side="left",
            padx=15
        )

    # ==========================================
    # Select Folder
    # ==========================================

    def select_folder(self):

        folder = filedialog.askdirectory(
            title="Select Folder to Organize"
        )

        if not folder:
            return

        self.selected_folder = folder

        self.scanned_files = []
        self.duplicate_groups = []
        self.duplicate_count = 0
        self.last_organization = None

        self.folder_label.configure(
            text=f"Selected Folder: {folder}"
        )

        self.status_label.configure(
            text="Folder selected successfully"
        )

        # ==========================================
        # Reset Dashboard
        # ==========================================

        self.card_values["Total Files"].configure(
            text="0"
        )

        self.card_values["Categories"].configure(
            text="0"
        )

        self.card_values["Total Size"].configure(
            text="0 MB"
        )

        self.card_values["Duplicates"].configure(
            text="0"
        )

        # ==========================================
        # Reset Buttons
        # ==========================================

        self.scan_button.configure(
            state="normal"
        )

        self.organize_button.configure(
            state="disabled"
        )

        self.undo_button.configure(
            state="disabled"
        )

        self.show_empty_message(
            "No files scanned yet"
        )

    # ==========================================
    # Scan Folder
    # ==========================================

    def scan_folder(self):

        if not self.selected_folder:

            messagebox.showwarning(
                "No Folder Selected",
                "Please select a folder first."
            )

            return

        try:

            self.status_label.configure(
                text="Scanning folder..."
            )

            self.update_idletasks()

            # ==========================================
            # Scan
            # ==========================================

            results = scan(
                self.selected_folder
            )

            # ==========================================
            # Store Results
            # ==========================================

            self.scanned_files = results["files"]

            # A new scan invalidates old undo history.
            self.last_organization = None

            # ==========================================
            # Reset Duplicate Data
            # ==========================================

            self.duplicate_groups = []
            self.duplicate_count = 0

            self.card_values["Duplicates"].configure(
                text="0"
            )

            # ==========================================
            # Enable / Disable Organize
            # ==========================================

            if self.scanned_files:

                self.organize_button.configure(
                    state="normal"
                )

            else:

                self.organize_button.configure(
                    state="disabled"
                )

            self.undo_button.configure(
                state="disabled"
            )

            # ==========================================
            # Update Dashboard
            # ==========================================

            self.card_values["Total Files"].configure(
                text=str(
                    results["total_files"]
                )
            )

            self.card_values["Categories"].configure(
                text=str(
                    results["categories"]
                )
            )

            total_size_mb = (
                results["total_size"]
                / (1024 * 1024)
            )

            self.card_values["Total Size"].configure(
                text=f"{total_size_mb:.2f} MB"
            )

            # ==========================================
            # AUTOMATIC DUPLICATE DETECTION
            # ==========================================

            self.status_label.configure(
                text="Checking for duplicate files..."
            )

            self.update_idletasks()

            # Detect duplicates automatically,
            # but DO NOT display duplicate results.
            self.detect_duplicates(
                show_results=False
            )

            # ==========================================
            # IMPORTANT:
            # Show Total Files After Scan
            # ==========================================

            self.display_files(
                self.scanned_files
            )

            # ==========================================
            # Final Status
            # ==========================================

            if self.duplicate_count > 0:

                self.status_label.configure(
                    text=(
                        f"Scan complete • "
                        f"{results['total_files']} files found • "
                        f"{self.duplicate_count} duplicates • "
                        f"Showing all files"
                    )
                )

            else:

                self.status_label.configure(
                    text=(
                        f"Scan complete • "
                        f"{results['total_files']} files found • "
                        f"No duplicates • "
                        f"Showing all files"
                    )
                )

        except Exception as error:

            self.status_label.configure(
                text="Scan failed"
            )

            messagebox.showerror(
                "Scan Error",
                str(error)
            )

    # ==========================================
    # Organize Files
    # ==========================================

    def organize_files(self):

        if not self.selected_folder:

            messagebox.showwarning(
                "No Folder Selected",
                "Please select a folder first."
            )

            return

        if not self.scanned_files:

            messagebox.showwarning(
                "No Files",
                "Please scan the folder first."
            )

            return

        confirm = messagebox.askyesno(
            "Organize Files",
            (
                "Are you sure you want to organize "
                "these files?\n\n"
                "Files will be moved into category "
                "folders."
            )
        )

        if not confirm:
            return

        try:

            self.status_label.configure(
                text="Organizing files..."
            )

            self.update_idletasks()

            # ==========================================
            # Organize
            # ==========================================

            results = organize(
                self.selected_folder,
                self.scanned_files
            )

            moved_files = results.get(
                "moved",
                []
            )

            errors = results.get(
                "errors",
                []
            )

            moved_count = len(
                moved_files
            )

            error_count = len(
                errors
            )

            # ==========================================
            # Save Undo History
            # ==========================================

            if moved_files:

                self.last_organization = {
                    "moved": moved_files,
                    "errors": errors
                }

                self.undo_button.configure(
                    state="normal"
                )

            else:

                self.last_organization = None

                self.undo_button.configure(
                    state="disabled"
                )

            # ==========================================
            # Disable Organize
            # ==========================================

            self.organize_button.configure(
                state="disabled"
            )

            # ==========================================
            # Refresh
            # ==========================================

            self.refresh_after_organization()

            # ==========================================
            # Result Feedback
            # ==========================================

            if error_count == 0:

                self.status_label.configure(
                    text=(
                        f"Organization complete • "
                        f"{moved_count} files moved"
                    )
                )

                messagebox.showinfo(
                    "Organization Complete",
                    (
                        f"Successfully organized "
                        f"{moved_count} files.\n\n"
                        "You can use Undo to restore "
                        "the files."
                    )
                )

            else:

                self.status_label.configure(
                    text=(
                        f"Organization completed with errors • "
                        f"{moved_count} moved, "
                        f"{error_count} errors"
                    )
                )

                messagebox.showwarning(
                    "Organization Completed With Errors",
                    (
                        f"{moved_count} files organized.\n"
                        f"{error_count} files could not "
                        "be moved.\n\n"
                        "Undo can restore the files "
                        "that were successfully moved."
                    )
                )

        except Exception as error:

            self.status_label.configure(
                text="Organization failed"
            )

            messagebox.showerror(
                "Organization Error",
                str(error)
            )

    # ==========================================
    # Undo Organization
    # ==========================================

    def undo_files(self):

        if not self.last_organization:

            messagebox.showinfo(
                "Nothing to Undo",
                "There is no organization action to undo."
            )

            return

        moved_files = self.last_organization.get(
            "moved",
            []
        )

        if not moved_files:

            messagebox.showinfo(
                "Nothing to Undo",
                "There are no moved files to restore."
            )

            return

        confirm = messagebox.askyesno(
            "Undo Organization",
            (
                f"Restore {len(moved_files)} files "
                "to their original locations?"
            )
        )

        if not confirm:
            return

        try:

            self.status_label.configure(
                text="Undoing organization..."
            )

            self.update_idletasks()

            # ==========================================
            # Undo
            # ==========================================

            result = undo_organization(
                moved_files
            )

            restored = result.get(
                "restored",
                []
            )

            errors = result.get(
                "errors",
                []
            )

            restored_count = len(
                restored
            )

            error_count = len(
                errors
            )

            # ==========================================
            # Update Undo History
            # ==========================================

            if error_count == 0:

                self.last_organization = None

                self.undo_button.configure(
                    state="disabled"
                )

            else:

                restored_sources = {
                    item["source"]
                    for item in restored
                }

                remaining = [
                    item
                    for item in moved_files
                    if item.get("source")
                    not in restored_sources
                ]

                if remaining:

                    self.last_organization = {
                        "moved": remaining
                    }

                    self.undo_button.configure(
                        state="normal"
                    )

                else:

                    self.last_organization = None

                    self.undo_button.configure(
                        state="disabled"
                    )

            # ==========================================
            # Refresh
            # ==========================================

            self.refresh_after_organization()

            # ==========================================
            # Result Feedback
            # ==========================================

            if error_count == 0:

                self.status_label.configure(
                    text=(
                        f"Undo complete • "
                        f"{restored_count} files restored"
                    )
                )

                messagebox.showinfo(
                    "Undo Complete",
                    (
                        f"Successfully restored "
                        f"{restored_count} files."
                    )
                )

            else:

                self.status_label.configure(
                    text=(
                        f"Undo completed with errors • "
                        f"{restored_count} restored, "
                        f"{error_count} errors"
                    )
                )

                error_details = "\n".join(
                    f"• {error['name']}: {error['error']}"
                    for error in errors
                )

                messagebox.showwarning(
                    "Undo Completed With Errors",
                    (
                        f"{restored_count} files restored.\n"
                        f"{error_count} files could not "
                        f"be restored.\n\n"
                        f"{error_details}"
                    )
                )

        except Exception as error:

            self.status_label.configure(
                text="Undo failed"
            )

            messagebox.showerror(
                "Undo Error",
                str(error)
            )

    # ==========================================
    # Refresh After Organization
    # ==========================================

    def refresh_after_organization(self):

        try:

            results = scan(
                self.selected_folder
            )

            self.scanned_files = results[
                "files"
            ]

            # ==========================================
            # Update Dashboard
            # ==========================================

            self.card_values["Total Files"].configure(
                text=str(
                    results["total_files"]
                )
            )

            self.card_values["Categories"].configure(
                text=str(
                    results["categories"]
                )
            )

            total_size_mb = (
                results["total_size"]
                / (1024 * 1024)
            )

            self.card_values["Total Size"].configure(
                text=f"{total_size_mb:.2f} MB"
            )

            # ==========================================
            # Detect Duplicates Again
            # ==========================================

            self.detect_duplicates(
                show_results=False
            )

            # ==========================================
            # Show Total Files After Refresh
            # ==========================================

            self.display_files(
                self.scanned_files
            )

            # ==========================================
            # Organize Button
            # ==========================================

            if self.scanned_files:

                self.organize_button.configure(
                    state="normal"
                )

            else:

                self.organize_button.configure(
                    state="disabled"
                )

        except Exception as error:

            self.status_label.configure(
                text="Refresh failed"
            )

            print(
                f"Refresh error: {error}"
            )

    # ==========================================
    # Display Files
    # ==========================================

    def display_files(self, files):

        self.clear_file_list()

        # ==========================================
        # No Files
        # ==========================================

        if not files:

            self.show_empty_message(
                "No files found"
            )

            return

        # ==========================================
        # Create Rows
        # ==========================================

        for file_data in files:

            row = ctk.CTkFrame(
                self.file_list,
                height=45
            )

            row.pack(
                fill="x",
                pady=2
            )

            # ==========================================
            # File Name
            # ==========================================

            ctk.CTkLabel(
                row,
                text=file_data["name"],
                anchor="w"
            ).pack(
                side="left",
                fill="x",
                expand=True,
                padx=(15, 5)
            )

            # ==========================================
            # Extension
            # ==========================================

            extension = file_data.get(
                "extension",
                ""
            )

            if extension:

                extension = extension.upper().replace(
                    ".",
                    ""
                )

            else:

                extension = "FILE"

            ctk.CTkLabel(
                row,
                text=extension,
                width=100
            ).pack(
                side="left",
                padx=5
            )

            # ==========================================
            # File Size
            # ==========================================

            size = self.format_file_size(
                file_data.get(
                    "size",
                    0
                )
            )

            ctk.CTkLabel(
                row,
                text=size,
                width=100
            ).pack(
                side="left",
                padx=(5, 15)
            )

    # ==========================================
    # Format File Size
    # ==========================================

    def format_file_size(self, size):

        if size < 1024:

            return f"{size} B"

        if size < 1024 * 1024:

            return f"{size / 1024:.1f} KB"

        if size < 1024 * 1024 * 1024:

            return f"{size / (1024 * 1024):.1f} MB"

        return f"{size / (1024 * 1024 * 1024):.2f} GB"

    # ==========================================
    # Show Files In Category
    # ==========================================

    def show_category_files(self, category):

        filtered_files = [
            file_data
            for file_data in self.scanned_files
            if file_data.get("category") == category
        ]

        self.display_files(
            filtered_files
        )

        self.status_label.configure(
            text=(
                f"{category} • "
                f"{len(filtered_files)} files"
            )
        )

    # ==========================================
    # Display Size Summary
    # ==========================================

    def display_size_summary(self):

        self.clear_file_list()

        # ==========================================
        # Calculate Category Sizes
        # ==========================================

        category_sizes = {}

        for file_data in self.scanned_files:

            category = file_data.get(
                "category",
                "Other"
            )

            size = file_data.get(
                "size",
                0
            )

            category_sizes[category] = (
                category_sizes.get(category, 0)
                + size
            )

        # ==========================================
        # No Data
        # ==========================================

        if not category_sizes:

            self.show_empty_message(
                "No size information available"
            )

            return

        # ==========================================
        # Header
        # ==========================================

        header = ctk.CTkFrame(
            self.file_list,
            height=45
        )

        header.pack(
            fill="x",
            pady=(0, 5)
        )

        ctk.CTkLabel(
            header,
            text="Category",
            font=("Segoe UI", 13, "bold"),
            anchor="w"
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=15
        )

        ctk.CTkLabel(
            header,
            text="Size",
            font=("Segoe UI", 13, "bold"),
            width=150
        ).pack(
            side="left",
            padx=15
        )

        # ==========================================
        # Rows
        # ==========================================

        for category, size in sorted(
            category_sizes.items()
        ):

            row = ctk.CTkFrame(
                self.file_list,
                height=50
            )

            row.pack(
                fill="x",
                pady=2
            )

            ctk.CTkLabel(
                row,
                text=f"📁  {category}",
                anchor="w",
                font=("Segoe UI", 14)
            ).pack(
                side="left",
                fill="x",
                expand=True,
                padx=15
            )

            ctk.CTkLabel(
                row,
                text=self.format_file_size(
                    size
                ),
                width=150,
                font=("Segoe UI", 14, "bold")
            ).pack(
                side="left",
                padx=15
            )