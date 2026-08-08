import os
import shutil

import customtkinter as ctk
from tkinter import filedialog, messagebox

from core.scanner import scan
from core.organizer import organize


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
            command=self.undo_organization
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

            messagebox.showinfo(
                "Duplicates",
                "Duplicate detection will be added next."
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
            text="Files",
            font=("Segoe UI", 13, "bold"),
            width=120
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
                height=50,
                cursor="hand2"
            )

            row.pack(
                fill="x",
                pady=2
            )

            category_label = ctk.CTkLabel(
                row,
                text=f"📁  {category}",
                font=("Segoe UI", 14),
                anchor="w",
                cursor="hand2"
            )

            category_label.pack(
                side="left",
                fill="x",
                expand=True,
                padx=15
            )

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
            # Click Category
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

    def show_empty_message(self, text="No files scanned yet"):

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

            results = scan(
                self.selected_folder
            )

            # ==========================================
            # Store Results
            # ==========================================

            self.scanned_files = results["files"]

            # A new scan invalidates the old undo state
            self.last_organization = None

            # ==========================================
            # Enable Organize
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
            # Display Files
            # ==========================================

            self.display_files(
                self.scanned_files
            )

            # ==========================================
            # Status
            # ==========================================

            self.status_label.configure(
                text=(
                    f"Scan complete • "
                    f"{results['total_files']} files found"
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
            # Update UI
            # ==========================================

            self.organize_button.configure(
                state="disabled"
            )

            self.status_label.configure(
                text=(
                    f"Organization complete • "
                    f"{moved_count} files moved"
                )
            )

            # ==========================================
            # Show Result
            # ==========================================

            if error_count == 0:

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

            # ==========================================
            # Rescan Folder
            # ==========================================

            self.refresh_after_organization()

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

    def undo_organization(self):

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

            restored_count = 0
            errors = []

            # ==========================================
            # Restore Each File
            # ==========================================

            for file_data in moved_files:

                source = file_data.get(
                    "source"
                )

                destination = file_data.get(
                    "destination"
                )

                if not source or not destination:
                    errors.append(
                        "Missing source or destination path."
                    )
                    continue

                # File no longer exists at destination
                if not os.path.isfile(destination):

                    errors.append(
                        f"File not found: {destination}"
                    )

                    continue

                try:

                    # ==========================================
                    # Make Sure Original Directory Exists
                    # ==========================================

                    original_directory = os.path.dirname(
                        source
                    )

                    os.makedirs(
                        original_directory,
                        exist_ok=True
                    )

                    # ==========================================
                    # Avoid Overwriting Another File
                    # ==========================================

                    if os.path.exists(source):

                        errors.append(
                            (
                                f"Original location already "
                                f"contains a file: {source}"
                            )
                        )

                        continue

                    # ==========================================
                    # Move Back
                    # ==========================================

                    shutil.move(
                        destination,
                        source
                    )

                    restored_count += 1

                except Exception as error:

                    errors.append(
                        f"{os.path.basename(destination)}: {error}"
                    )

            # ==========================================
            # Clear Undo History
            # ==========================================

            self.last_organization = None

            self.undo_button.configure(
                state="disabled"
            )

            # ==========================================
            # Rescan
            # ==========================================

            self.refresh_after_organization()

            # ==========================================
            # Result
            # ==========================================

            if not errors:

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
                        f"Undo completed • "
                        f"{restored_count} restored, "
                        f"{len(errors)} errors"
                    )
                )

                messagebox.showwarning(
                    "Undo Completed With Errors",
                    (
                        f"{restored_count} files restored.\n"
                        f"{len(errors)} files could not "
                        "be restored."
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
            # Display Updated Files
            # ==========================================

            self.display_files(
                self.scanned_files
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