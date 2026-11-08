"""
Streamlit UI component for Excel template download, batch file upload,
row-by-row calculation with progress bar, and Excel output download.
"""

import pandas as pd
import streamlit as st

from components.excel_handler import (
    TAB_CONFIGS,
    generate_excel_template,
    process_excel_batch,
)

EXCEL_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def render_batch_section(tab_key: str):
    """
    Renders the Batch Processing (Excel Template & Upload) section inside a
    Streamlit tab for the given tab_key ('adequacy', 'assessment',
    'prescription', 'clearance', 'koa').
    """
    if tab_key not in TAB_CONFIGS:
        st.error(f"Unknown tab configuration: {tab_key}")
        return

    config = TAB_CONFIGS[tab_key]
    title = config["title"]

    st.divider()
    st.subheader(f"Batch Processing — {title} (Excel)")
    st.markdown(
        "Download the Excel template (which includes an **Inputs** sheet with example rows and a detailed "
        "**Legend** sheet), fill in one or more rows of data, and upload the updated file below to calculate "
        "all results in batch."
    )

    with st.expander(f"View {title} Excel Legend & Column Specifications", expanded=False):
        for note in config.get("general_notes", []):
            st.markdown(f"- {note}")

        legend_rows = [
            {
                "Column": inp["col"],
                "Description": inp["label"],
                "Symbol": inp["symbol"],
                "Units": inp["unit"],
                "Min": str(inp["min"]),
                "Max": str(inp["max"]),
                "Example": str(inp["example"]),
                "Required": "Yes" if inp.get("required", True) else "Optional",
                "Notes": inp.get("notes", ""),
            }
            for inp in config["inputs"]
        ]
        st.markdown("**Input Columns (`Inputs` sheet):**")
        st.dataframe(pd.DataFrame(legend_rows), hide_index=True)

        out_legend_rows = [
            {
                "Output Column": out["col"],
                "Description": out["label"],
                "Symbol": out["symbol"],
                "Units": out["unit"],
            }
            for out in config["outputs"]
        ]
        st.markdown("**Output Columns (`Results` sheet):**")
        st.dataframe(pd.DataFrame(out_legend_rows), hide_index=True)

    template_bytes = generate_excel_template(tab_key, include_sample_rows=True)
    st.download_button(
        label=f"Download {title} Template (.xlsx)",
        data=template_bytes,
        file_name=config["template_filename"],
        mime=EXCEL_MIME,
        key=f"dl_template_{tab_key}",
    )

    uploaded_file = st.file_uploader(
        f"Upload updated {title} Excel file (.xlsx)",
        type=["xlsx"],
        key=f"upload_xlsx_{tab_key}",
    )

    state_key = f"batch_result_{tab_key}"
    file_sig_key = f"batch_file_sig_{tab_key}"

    if uploaded_file is not None:
        raw_bytes = uploaded_file.getvalue()
        current_sig = (uploaded_file.name, len(raw_bytes), hash(raw_bytes))

        run_clicked = st.button("Run Batch Calculation", key=f"run_batch_btn_{tab_key}")

        if run_clicked or st.session_state.get(file_sig_key) != current_sig:
            progress_bar = st.progress(0, text="Starting batch calculation...")
            status_box = st.empty()

            def _on_progress(
                processed_rows,
                remaining_rows,
                total_rows,
                valid_rows,
                missing_or_invalid_rows,
                current_row_result,
            ):
                pct = int(round((processed_rows / total_rows) * 100)) if total_rows > 0 else 100
                msg = (
                    f"Processed: {processed_rows}/{total_rows} rows | "
                    f"Remaining (missing to process): {remaining_rows} rows | "
                    f"Valid: {valid_rows} | "
                    f"Missing/Invalid data rows: {missing_or_invalid_rows}"
                )
                progress_bar.progress(pct, text=msg)
                status_box.info(msg)

            try:
                batch_data = process_excel_batch(
                    tab_key=tab_key,
                    file_or_records=raw_bytes,
                    progress_callback=_on_progress,
                )
                st.session_state[state_key] = batch_data
                st.session_state[file_sig_key] = current_sig
                if batch_data["total_rows"] == 0:
                    progress_bar.progress(100, text="No data rows found in the uploaded file.")
            except Exception as exc:
                st.error(f"Could not process the uploaded Excel file: {exc}")
                return

        batch_data = st.session_state.get(state_key)
        if batch_data:
            total_r = batch_data["total_rows"]
            proc_r = batch_data["processed_rows"]
            valid_r = batch_data["valid_rows"]
            err_r = batch_data["missing_or_invalid_rows"]

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Rows", total_r)
            c2.metric("Processed Rows", proc_r)
            c3.metric("Valid Rows", valid_r)
            c4.metric("Missing / Invalid Rows", err_r)

            if total_r > 0:
                df_res = pd.DataFrame(batch_data["results"], columns=batch_data["columns"])
                st.dataframe(df_res, hide_index=True)

                st.download_button(
                    label=f"Download {title} Output (.xlsx)",
                    data=batch_data["output_excel_bytes"],
                    file_name=config["output_filename"],
                    mime=EXCEL_MIME,
                    key=f"dl_output_{tab_key}",
                )
            else:
                st.warning("The uploaded Excel file does not contain any data rows in the 'Inputs' sheet.")
