import threading

import customtkinter as ctk
from tkinter import filedialog, messagebox

from app.core.config import APP_NAME, WINDOW_GEOMETRY, WINDOW_MIN_SIZE
from app.core.logger import logger
from app.core.scanner import scan
from app.core.organizer import organize, undo_organization


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

        self.title(APP_NAME)
        self.geometry(WINDOW_GEOMETRY)
        self.minsize(*WINDOW_MIN_SIZE)
        logger.info("Application startup complete")

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

        # Track the latest in-flight operation so stale worker results
        # cannot overwrite a newer scan/organize/undo state.
        self._operation_counter = 0
        self._latest_operation_id = 0

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

    def detect_duplicates(
        self,
        show_results=False,
        duplicate_groups=None,
    ):

        self.duplicate_groups = []
        self.duplicate_count = 0

        try:

            if duplicate_groups is None:
                duplicate_groups = []

            self.duplicate_groups = duplicate_groups

            # Count duplicate files from the scanner's result set.
            # The core scanner owns duplicate detection; the UI only
            # reflects the already-computed result.
            self.duplicate_count = sum(
                len(group.get("files", [])) - 1
                for group in duplicate_groups
            )

            self.card_values["Duplicates"].configure(
                text=str(self.duplicate_count)
            )

            if show_results:
                self.display_duplicates(
                    duplicate_groups
                )

        except Exception as error:

            self.card_values["Duplicates"].configure(
                text="0"
            )

            self.duplicate_groups = []
            self.duplicate_count = 0

            self.status_label.configure(
                text="Duplicate detection failed"
            )

            messagebox.showerror(
                "Duplicate Detection Error",
                str(error)
            )

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
    # Action Button State
    # ==========================================

    @staticmethod
    def get_action_button_state(selected_folder, scanned_files, last_organization):
        has_folder = bool(selected_folder)
        has_files = bool(scanned_files)
        has_undo = bool(last_organization and last_organization.get("moved"))

        return {
            "scan": has_folder,
            "organize": has_folder and has_files,
            "undo": has_undo,
        }

    def update_action_buttons(self):

        state = self.get_action_button_state(
            self.selected_folder,
            self.scanned_files,
            self.last_organization,
        )

        self.scan_button.configure(
            state="normal" if state["scan"] else "disabled"
        )

        self.organize_button.configure(
            state="normal" if state["organize"] else "disabled"
        )

        self.undo_button.configure(
            state="normal" if state["undo"] else "disabled"
        )

    def _begin_operation(self):
        self._operation_counter += 1
        self._latest_operation_id = self._operation_counter
        return self._latest_operation_id

    def _is_current_operation(self, operation_id):
        return operation_id == self._latest_operation_id

    # ==========================================
    # Select Folder
    # ==========================================

    def select_folder(self):

        self._begin_operation()

        folder = filedialog.askdirectory(
            title="Select Folder to Organize"
        )

        if not folder:
            return

        self.selected_folder = folder
        logger.info("Folder selected: %s", folder)

        self.scanned_files = []
        self.duplicate_groups = []
        self.duplicate_count = 0
        self.last_organization = None

        self.folder_label.configure(
            text=f"Selected Folder: {folder}"
        )

        self.status_label.configure(
            text="Folder selected • ready to scan"
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

        self.update_action_buttons()

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

        operation_id = self._begin_operation()

        self.scan_button.configure(state="disabled")
        self.organize_button.configure(state="disabled")
        self.undo_button.configure(state="disabled")

        self.status_label.configure(
            text="Scanning folder..."
        )

        self.update_idletasks()

        worker = threading.Thread(
            target=self._scan_worker,
            args=(operation_id,),
            daemon=True,
        )
        worker.start()

    def _scan_worker(self, operation_id):

        try:
            logger.info("Scan started for folder: %s", self.selected_folder)
            results = scan(self.selected_folder)
            self.after(0, self._apply_scan_results, operation_id, results)

        except (OSError, ValueError, TypeError) as error:
            logger.exception("Unexpected scan error for folder: %s", self.selected_folder)
            self.after(0, self._handle_scan_error, operation_id, error)

    def _apply_scan_results(self, operation_id, results):

        if not self._is_current_operation(operation_id):
            logger.info("Ignoring stale scan results for operation %s", operation_id)
            return

        self.scanned_files = results["files"]
        self.last_organization = None
        self.duplicate_groups = []
        self.duplicate_count = 0

        self.card_values["Duplicates"].configure(
            text="0"
        )

        self.card_values["Total Files"].configure(
            text=str(results["total_files"])
        )

        self.card_values["Categories"].configure(
            text=str(results["categories"])
        )

        total_size_mb = results["total_size"] / (1024 * 1024)
        self.card_values["Total Size"].configure(
            text=f"{total_size_mb:.2f} MB"
        )

        self.detect_duplicates(
            show_results=False,
            duplicate_groups=results["duplicates"],
        )

        logger.info(
            "Scan complete for %s: %s files, %s duplicates",
            self.selected_folder,
            results["total_files"],
            self.duplicate_count,
        )

        self.display_files(self.scanned_files)
        self.update_action_buttons()

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

    def _handle_scan_error(self, operation_id, error):
        if not self._is_current_operation(operation_id):
            logger.info("Ignoring stale scan error for operation %s", operation_id)
            return

        self.status_label.configure(text="Scan failed")
        self.update_action_buttons()
        messagebox.showerror("Scan Error", str(error))

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

        operation_id = self._begin_operation()

        self.scan_button.configure(state="disabled")
        self.organize_button.configure(state="disabled")
        self.undo_button.configure(state="disabled")

        self.status_label.configure(
            text="Organizing files..."
        )
        self.update_idletasks()

        worker = threading.Thread(
            target=self._organize_worker,
            args=(operation_id,),
            daemon=True,
        )
        worker.start()

    def _organize_worker(self, operation_id):

        try:
            logger.info("Organization started for folder: %s with %s files", self.selected_folder, len(self.scanned_files))
            results = organize(self.selected_folder, self.scanned_files)
            self.after(0, self._apply_organization_results, operation_id, results)

        except (OSError, ValueError, TypeError) as error:
            logger.exception("Unexpected organization error for folder: %s", self.selected_folder)
            self.after(0, self._handle_organization_error, operation_id, error)

    def _apply_organization_results(self, operation_id, results):

        if not self._is_current_operation(operation_id):
            logger.info("Ignoring stale organization results for operation %s", operation_id)
            return

        moved_files = results.get("moved", [])
        errors = results.get("errors", [])
        moved_count = len(moved_files)
        error_count = len(errors)

        if moved_files:
            self.last_organization = {
                "moved": moved_files,
                "errors": errors,
            }
        else:
            self.last_organization = None

        self.refresh_after_organization()
        self.update_action_buttons()

        if error_count == 0:
            logger.info("Organization complete: %s files moved", moved_count)
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
            logger.warning("Organization finished with errors: %s moved, %s failed", moved_count, error_count)
            self.status_label.configure(
                text=(
                    f"Organization finished with errors • "
                    f"{moved_count} moved, "
                    f"{error_count} failed"
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

    def _handle_organization_error(self, operation_id, error):
        if not self._is_current_operation(operation_id):
            logger.info("Ignoring stale organization error for operation %s", operation_id)
            return

        self.status_label.configure(text="Organization failed")
        self.update_action_buttons()
        messagebox.showerror("Organization Error", str(error))

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

        operation_id = self._begin_operation()

        self.scan_button.configure(state="disabled")
        self.organize_button.configure(state="disabled")
        self.undo_button.configure(state="disabled")

        self.status_label.configure(
            text="Restoring files..."
        )
        self.update_idletasks()

        worker = threading.Thread(
            target=self._undo_worker,
            args=(operation_id, moved_files),
            daemon=True,
        )
        worker.start()

    def _undo_worker(self, operation_id, moved_files):

        try:
            logger.info("Undo started for %s files", len(moved_files))
            result = undo_organization(moved_files)
            self.after(0, self._apply_undo_results, operation_id, moved_files, result)

        except (OSError, ValueError, TypeError) as error:
            logger.exception("Unexpected undo error")
            self.after(0, self._handle_undo_error, operation_id, error)

    def _apply_undo_results(self, operation_id, moved_files, result):

        if not self._is_current_operation(operation_id):
            logger.info("Ignoring stale undo results for operation %s", operation_id)
            return

        restored = result.get("restored", [])
        errors = result.get("errors", [])
        restored_count = len(restored)
        error_count = len(errors)

        if error_count == 0:
            self.last_organization = None
        else:
            restored_sources = {item["source"] for item in restored}
            remaining = [
                item for item in moved_files
                if item.get("source") not in restored_sources
            ]
            self.last_organization = {"moved": remaining} if remaining else None

        self.update_action_buttons()
        self.refresh_after_organization()

        if error_count == 0:
            logger.info("Undo complete: %s files restored", restored_count)
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
            logger.warning("Undo finished with errors: %s restored, %s failed", restored_count, error_count)
            self.status_label.configure(
                text=(
                    f"Undo finished with errors • "
                    f"{restored_count} restored, "
                    f"{error_count} failed"
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

    def _handle_undo_error(self, operation_id, error):
        if not self._is_current_operation(operation_id):
            logger.info("Ignoring stale undo error for operation %s", operation_id)
            return

        self.status_label.configure(text="Undo failed")
        self.update_action_buttons()
        messagebox.showerror("Undo Error", str(error))

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
            # Reuse Duplicates From scan()
            # ==========================================

            self.detect_duplicates(
                show_results=False,
                duplicate_groups=results["duplicates"],
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

            if not self.scanned_files:
                self.status_label.configure(
                    text="Folder refreshed • no files remain"
                )
            elif self.duplicate_count > 0:
                self.status_label.configure(
                    text=(
                        f"Folder refreshed • "
                        f"{len(self.scanned_files)} files • "
                        f"{self.duplicate_count} duplicate files"
                    )
                )
            else:
                self.status_label.configure(
                    text=(
                        f"Folder refreshed • "
                        f"{len(self.scanned_files)} files • "
                        f"no duplicates"
                    )
                )

        except Exception as error:

            self.status_label.configure(
                text="Refresh failed"
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