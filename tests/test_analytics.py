"""
Unit tests for Google Analytics (GA4) integration (components.analytics).
"""

import os
import pathlib
import sys
import tempfile
import types
import unittest
from unittest.mock import MagicMock


class TestGoogleAnalytics(unittest.TestCase):
    """Tests GA4 Measurement ID resolution, index.html patching, and component injection."""

    def setUp(self):
        self._orig_st = sys.modules.get("streamlit")
        self._orig_comp = sys.modules.get("streamlit.components")
        self._orig_comp_v1 = sys.modules.get("streamlit.components.v1")
        self._orig_analytics = sys.modules.get("components.analytics")
        self._orig_env = os.environ.get("GA_MEASUREMENT_ID")

        self.mock_st = MagicMock()
        self.mock_st.session_state = {}
        self.mock_st.secrets = {}
        self.mock_st.__file__ = "/tmp/fake_streamlit/__init__.py"

        self.mock_comp_v1 = MagicMock()
        mock_comp = types.ModuleType("streamlit.components")
        mock_comp.v1 = self.mock_comp_v1
        self.mock_st.components = mock_comp

        sys.modules["streamlit"] = self.mock_st
        sys.modules["streamlit.components"] = mock_comp
        sys.modules["streamlit.components.v1"] = self.mock_comp_v1
        sys.modules.pop("components.analytics", None)

    def tearDown(self):
        if self._orig_env is not None:
            os.environ["GA_MEASUREMENT_ID"] = self._orig_env
        else:
            os.environ.pop("GA_MEASUREMENT_ID", None)

        if self._orig_st is not None:
            sys.modules["streamlit"] = self._orig_st
        else:
            sys.modules.pop("streamlit", None)

        if self._orig_comp is not None:
            sys.modules["streamlit.components"] = self._orig_comp
        else:
            sys.modules.pop("streamlit.components", None)

        if self._orig_comp_v1 is not None:
            sys.modules["streamlit.components.v1"] = self._orig_comp_v1
        else:
            sys.modules.pop("streamlit.components.v1", None)

        if self._orig_analytics is not None:
            sys.modules["components.analytics"] = self._orig_analytics
        else:
            sys.modules.pop("components.analytics", None)

    def test_measurement_id_resolution(self):
        from components.analytics import get_ga_measurement_id

        os.environ.pop("GA_MEASUREMENT_ID", None)
        # Default placeholder returns None
        self.assertIsNone(get_ga_measurement_id())

        # Direct parameter
        self.assertEqual(get_ga_measurement_id("G-ABC1234567"), "G-ABC1234567")

        # Secrets fallback
        self.mock_st.secrets = {"GA_MEASUREMENT_ID": "G-SECRET999"}
        self.assertEqual(get_ga_measurement_id(), "G-SECRET999")

        # Environment variable takes precedence over secrets
        os.environ["GA_MEASUREMENT_ID"] = "G-ENV123456"
        self.assertEqual(get_ga_measurement_id(), "G-ENV123456")

    def test_try_patch_streamlit_index_html(self):
        from components.analytics import GA_SCRIPT_ID, try_patch_streamlit_index_html

        with tempfile.TemporaryDirectory() as tmpdir:
            index_file = pathlib.Path(tmpdir) / "index.html"
            index_file.write_text("<html><head><title>Streamlit</title></head><body></body></html>", encoding="utf-8")

            ok = try_patch_streamlit_index_html("G-TEST12345", index_path=index_file)
            self.assertTrue(ok)

            patched = index_file.read_text(encoding="utf-8")
            self.assertIn("G-TEST12345", patched)
            self.assertIn(GA_SCRIPT_ID, patched)
            self.assertTrue(index_file.with_suffix(".html.bkp").exists())

            # Calling a second time is idempotent
            ok2 = try_patch_streamlit_index_html("G-TEST12345", index_path=index_file)
            self.assertTrue(ok2)
            self.assertEqual(index_file.read_text(encoding="utf-8").count(GA_SCRIPT_ID), 2)

    def test_inject_google_analytics_once_per_session(self):
        from components.analytics import inject_google_analytics

        # When unconfigured, returns False and does not call components.html
        os.environ.pop("GA_MEASUREMENT_ID", None)
        self.assertFalse(inject_google_analytics())
        self.mock_comp_v1.html.assert_not_called()

        # When configured, injects via components.html once per session
        self.assertTrue(inject_google_analytics("G-LIVE12345"))
        self.mock_comp_v1.html.assert_called_once()
        self.assertTrue(self.mock_st.session_state.get("_ga_injected"))

        # Subsequent call in the same session does not re-render duplicate iframe
        self.assertTrue(inject_google_analytics("G-LIVE12345"))
        self.mock_comp_v1.html.assert_called_once()


if __name__ == "__main__":
    unittest.main()
