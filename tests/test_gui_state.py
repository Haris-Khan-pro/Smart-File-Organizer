import logging
import unittest
from unittest.mock import patch

import app.core.logger as logger_module
from app.ui.main_window import MainWindow


class TestGuiState(unittest.TestCase):

    def test_initial_action_button_state(self):
        state = MainWindow.get_action_button_state("", [], None)

        self.assertFalse(state["scan"])
        self.assertFalse(state["organize"])
        self.assertFalse(state["undo"])

    def test_selected_folder_enables_scan_and_organize(self):
        scanned_files = [{
            "name": "example.txt",
            "path": "/tmp/example.txt",
            "category": "Documents",
            "size": 10,
        }]

        state = MainWindow.get_action_button_state(
            "/tmp/folder",
            scanned_files,
            None,
        )

        self.assertTrue(state["scan"])
        self.assertTrue(state["organize"])
        self.assertFalse(state["undo"])

    def test_undo_requires_valid_history(self):
        state = MainWindow.get_action_button_state(
            "/tmp/folder",
            [{
                "name": "example.txt",
                "path": "/tmp/example.txt",
                "category": "Documents",
                "size": 10,
            }],
            {"moved": [{"source": "/tmp/a", "destination": "/tmp/b"}]},
        )

        self.assertTrue(state["undo"])

    def test_stale_operation_results_are_rejected(self):
        window = object.__new__(MainWindow)
        window._operation_counter = 0
        window._latest_operation_id = 0

        first_id = window._begin_operation()
        self.assertEqual(first_id, 1)
        self.assertTrue(window._is_current_operation(1))
        self.assertFalse(window._is_current_operation(0))

        second_id = window._begin_operation()
        self.assertEqual(second_id, 2)
        self.assertTrue(window._is_current_operation(2))
        self.assertFalse(window._is_current_operation(1))

    @patch("logging.FileHandler", side_effect=PermissionError("log file unavailable"))
    def test_configure_logging_falls_back_when_file_handler_fails(self, _):
        logger = logging.getLogger("smart_file_organizer")
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            handler.close()

        configured = logger_module.configure_logging()

        self.assertIsNotNone(configured)
        self.assertFalse(configured.propagate)
        self.assertTrue(any(isinstance(handler, logging.StreamHandler) for handler in configured.handlers))


if __name__ == "__main__":
    unittest.main()
