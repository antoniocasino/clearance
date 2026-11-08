"""
Google Analytics (GA4) integration for the EuReCa Streamlit application.

Supports configuring the GA4 Measurement ID (e.g. 'G-XXXXXXXXXX') via:
1. Direct parameter passed to `inject_google_analytics(measurement_id=...)`
2. Environment variable `GA_MEASUREMENT_ID`
3. Streamlit secrets `st.secrets["GA_MEASUREMENT_ID"]`
4. `DEFAULT_GA_MEASUREMENT_ID` constant in this module

Uses a dual-strategy approach for maximum compatibility with both local/Docker
deployments and Streamlit Community Cloud:
- Strategy 1: Injects the gtag.js snippet into Streamlit's static `index.html`
  `<head>` (once per environment, if the package directory is writable).
- Strategy 2: Injects the gtag.js script via `streamlit.components.v1.html`
  (attempting `window.parent.document.head` first and falling back to the
  component frame with `page_location` metadata).
"""

import os
import pathlib
import shutil
import streamlit as st
import streamlit.components.v1 as components

# Replace with your Google Analytics 4 Measurement ID (e.g. "G-XXXXXXXXXX")
# or configure `GA_MEASUREMENT_ID` in `.streamlit/secrets.toml` / environment variables.
DEFAULT_GA_MEASUREMENT_ID = "G-XXXXXXXXXX"

GA_SCRIPT_ID = "eureca-ga4-script"


def get_ga_measurement_id(measurement_id: str | None = None) -> str | None:
    """
    Resolves the active Google Analytics 4 Measurement ID.
    Returns None if not configured or still set to the placeholder 'G-XXXXXXXXXX'.
    """
    if measurement_id and measurement_id.strip():
        candidate = measurement_id.strip()
    elif os.environ.get("GA_MEASUREMENT_ID"):
        candidate = os.environ["GA_MEASUREMENT_ID"].strip()
    else:
        candidate = None
        try:
            if "GA_MEASUREMENT_ID" in st.secrets:
                candidate = str(st.secrets["GA_MEASUREMENT_ID"]).strip()
        except Exception:
            candidate = None
        if not candidate:
            candidate = DEFAULT_GA_MEASUREMENT_ID

    if not candidate or candidate == "G-XXXXXXXXXX":
        return None
    return candidate


def build_ga_head_snippet(measurement_id: str) -> str:
    """Returns the standard GA4 `<head>` HTML snippet for `index.html`."""
    return (
        f'<!-- Google tag (gtag.js) -->\n'
        f'<script id="{GA_SCRIPT_ID}" async src="https://www.googletagmanager.com/gtag/js?id={measurement_id}"></script>\n'
        f'<script id="{GA_SCRIPT_ID}-config">\n'
        f'  window.dataLayer = window.dataLayer || [];\n'
        f'  function gtag(){{dataLayer.push(arguments);}}\n'
        f'  gtag("js", new Date());\n'
        f'  gtag("config", "{measurement_id}");\n'
        f'</script>\n'
    )


def build_ga_component_html(measurement_id: str) -> str:
    """
    Returns an HTML/JS snippet for `streamlit.components.v1.html` that injects
    GA4 into `window.parent.document.head` when permitted by same-origin policy,
    and also initializes `gtag` in the component context as a fallback.
    """
    return f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={measurement_id}"></script>
    <script>
      (function() {{
        var measurementId = "{measurement_id}";
        try {{
          var parentDoc = window.parent.document;
          if (parentDoc && parentDoc.head && !parentDoc.getElementById("{GA_SCRIPT_ID}")) {{
            var s1 = parentDoc.createElement("script");
            s1.id = "{GA_SCRIPT_ID}";
            s1.async = true;
            s1.src = "https://www.googletagmanager.com/gtag/js?id=" + measurementId;
            parentDoc.head.appendChild(s1);

            var s2 = parentDoc.createElement("script");
            s2.id = "{GA_SCRIPT_ID}-config";
            s2.innerHTML =
              "window.dataLayer = window.dataLayer || [];" +
              "function gtag(){{dataLayer.push(arguments);}}" +
              "gtag('js', new Date());" +
              "gtag('config', '" + measurementId + "');";
            parentDoc.head.appendChild(s2);
            return;
          }}
        }} catch (e) {{
          // Cross-origin iframe restriction; fall back to local gtag tracking
        }}

        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', measurementId, {{
          'page_location': document.referrer || window.location.href
        }});
      }})();
    </script>
    """


def try_patch_streamlit_index_html(measurement_id: str, index_path: pathlib.Path | None = None) -> bool:
    """
    Attempts to inject the GA4 snippet into Streamlit's static `index.html` `<head>`
    so that Google Analytics loads in the main document window.

    Returns True if `index.html` already contains the snippet or was successfully patched,
    or False if `index.html` is read-only or not found.
    """
    try:
        if index_path is None:
            index_path = pathlib.Path(st.__file__).resolve().parent / "static" / "index.html"
        if not index_path.exists():
            return False

        html_content = index_path.read_text(encoding="utf-8")
        if GA_SCRIPT_ID in html_content or measurement_id in html_content:
            return True

        snippet = build_ga_head_snippet(measurement_id)
        if "<head>" in html_content:
            updated_html = html_content.replace("<head>", "<head>\n" + snippet, 1)
        elif "<HEAD>" in html_content:
            updated_html = html_content.replace("<HEAD>", "<HEAD>\n" + snippet, 1)
        else:
            return False

        bkp_path = index_path.with_suffix(".html.bkp")
        if not bkp_path.exists():
            shutil.copy2(index_path, bkp_path)

        index_path.write_text(updated_html, encoding="utf-8")
        return True
    except (OSError, PermissionError):
        return False


def inject_google_analytics(measurement_id: str | None = None) -> bool:
    """
    Injects Google Analytics (GA4) into the Streamlit app once per session.

    Returns True if a valid Measurement ID was resolved and injected, False otherwise.
    """
    resolved_id = get_ga_measurement_id(measurement_id)
    if not resolved_id:
        return False

    try_patch_streamlit_index_html(resolved_id)

    if not st.session_state.get("_ga_injected"):
        components.html(build_ga_component_html(resolved_id), height=0, width=0)
        st.session_state["_ga_injected"] = True

    return True
