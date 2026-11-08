"""
Unit tests for components.batch_ui (Streamlit UI component for batch Excel processing).
Uses unittest.mock to test UI rendering, file upload handling, progress bar
updates, and Excel download buttons without requiring a live Streamlit server.
"""

import sys
import types
import unittest
from unittest.mock import MagicMock

from components.excel_handler import TAB_CONFIGS, generate_excel_template


class _DummySessionState(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value


class TestBatchUI(unittest.TestCase):
    """Tests render_batch_section for all 5 tabs with mocked streamlit and pandas."""

    def setUp(self):
        self._orig_st = sys.modules.get("streamlit")
        self._orig_pd = sys.modules.get("pandas")
        self._orig_batch_ui = sys.modules.get("components.batch_ui")

        self.mock_st = MagicMock()
        self.mock_st.session_state = _DummySessionState()

        # Context manager support for expander
        expander_cm = MagicMock()
        expander_cm.__enter__.return_value = expander_cm
        expander_cm.__exit__.return_value = False
        self.mock_st.expander.return_value = expander_cm

        # Columns mock returning 4 mock column objects
        self.mock_st.columns.side_effect = lambda n: [MagicMock() for _ in range(n if isinstance(n, int) else len(n))]

        mock_pd = types.ModuleType("pandas")
        mock_pd.DataFrame = lambda data, columns=None: {"data": data, "columns": columns}

        sys.modules["streamlit"] = self.mock_st
        sys.modules["pandas"] = mock_pd
        if "components.batch_ui" in sys.modules:
            del sys.modules["components.batch_ui"]

    def tearDown(self):
        if self._orig_st is not None:
            sys.modules["streamlit"] = self._orig_st
        else:
            sys.modules.pop("streamlit", None)

        if self._orig_pd is not None:
            sys.modules["pandas"] = self._orig_pd
        else:
            sys.modules.pop("pandas", None)

        if self._orig_batch_ui is not None:
            sys.modules["components.batch_ui"] = self._orig_batch_ui
        else:
            sys.modules.pop("components.batch_ui", None)

    def test_render_batch_section_no_upload_all_tabs(self):
        """Verifies template download button and legend expander render for all 5 tabs."""
        from components.batch_ui import render_batch_section

        self.mock_st.file_uploader.return_value = None

        for tab_key in TAB_CONFIGS:
            self.mock_st.reset_mock()
            render_batch_section(tab_key)
            self.mock_st.download_button.assert_called_once()
            dl_kwargs = self.mock_st.download_button.call_args.kwargs
            self.assertEqual(dl_kwargs["file_name"], TAB_CONFIGS[tab_key]["template_filename"])
            self.assertEqual(dl_kwargs["key"], f"dl_template_{tab_key}")

    def test_render_batch_section_with_upload_and_progress_all_tabs(self):
        """Verifies file upload triggers batch calculation, progress bar updates, and output download."""
        from components.batch_ui import render_batch_section

        for tab_key in TAB_CONFIGS:
            with self.subTest(tab=tab_key):
                self.mock_st.reset_mock()
                self.mock_st.session_state = _DummySessionState()

                template_bytes = generate_excel_template(tab_key, include_sample_rows=True)
                fake_uploaded = MagicMock()
                fake_uploaded.name = f"uploaded_{tab_key}.xlsx"
                fake_uploaded.getvalue.return_value = template_bytes

                self.mock_st.file_uploader.return_value = fake_uploaded
                self.mock_st.button.return_value = True

                progress_obj = MagicMock()
                self.mock_st.progress.return_value = progress_obj

                render_batch_section(tab_key)

                # Progress bar updated for each sample row
                self.assertGreaterEqual(progress_obj.progress.call_count, 2)
                last_call = progress_obj.progress.call_args
                self.assertEqual(last_call.args[0], 100)
                self.assertIn("Processed: 2/2 rows", last_call.kwargs["text"])
                self.assertIn("Remaining (missing to process): 0 rows", last_call.kwargs["text"])

                # Both template download button and output download button rendered
                self.assertEqual(self.mock_st.download_button.call_count, 2)
                out_dl_kwargs = self.mock_st.download_button.call_args_list[1].kwargs
                self.assertEqual(out_dl_kwargs["file_name"], TAB_CONFIGS[tab_key]["output_filename"])
                self.assertEqual(out_dl_kwargs["key"], f"dl_output_{tab_key}")


if __name__ == "__main__":
    unittest.main()
