import streamlit as st
import pandas as pd

def key_informations_page():
    st.title("Key Information for Nephrologists on Using the App 'EuReCa'")
    st.markdown("""
         <style>
            p {text-align: justify;}
        </style>
        """,
        unsafe_allow_html=True
    ) 
    st.write("""
    The EuReCa app is reserved exclusively for nephrologists involved in the treatment of adult patients on maintenance haemodialysis (HD), as all calculations must necessarily be confirmed by qualified medical professionals before clinical use or for diagnostic purposes.

    There are two ways to take into account residual kidney function (KRU). Neither is proven superior in clinical studies so far. The **standard Kt/V (stdKt/V)** is the historical method, and the **Normalised EKRU (EKRUN)** is more recently introduced (see Home page). EKRUN requires less dialysis and is preferable to most patients.
    """)

    # --- Module 1: Adequacy ---
    st.header("1. The 'Adequacy' Module")
    st.write("""
    This is the main program that calculates all the key parameters of the double pool urea kinetic model (UKM). It shows the dialysis dose values (eKt/V) necessary to prescribe adequacy with one, two, and three HD sessions per week, respectively, according to criteria based alternately on stdKt/V or EKRUN with a variable target (see Home section), in order to choose the most suitable frequency and dose for the individual patient.
    """)

    st.write("""
    **Select blood and urine concentrations units:**
    * Blood and urine urea nitrogen concentrations (mg/dl)
    * Blood and urine urea concentrations (mg/dl)
    * Blood and urine urea concentrations (mmol/l)
    """)

    st.subheader("Table 1: Input and Output values of the module 'Adequacy'")

    adequacy_input_data = {
        '#': list(range(1, 20)),
        'Input': [
            "Patient id", "Lab date", "Number of HD sessions per week (1, 2, or 3)",
            "Preceding interdialytic interval (2, 3, 4, or 7)", "Pre-dialysis body weight",
            "Post-dialysis body weight", "Session length", "Blood flow rate",
            "Pre-dialyzer infusion rate (set 0 in HD or HDF-post)*",
            "Post-dialyzer infusion rate (set 0 in HD or HDF-pre)*",
            "Dialysate flow rate", "Dialyzer Manufacturer*", "Dialyzer Model*",
            "Dialyzer urea KoA in vitro *", "Pre-dialysis Blood Urea or Urea Nitrogen",
            "Post-dialysis Blood Urea or Urea Nitrogen", "Urinary Output",
            "Urinary Urea or Urea Nitrogen",
            "Renal urea clearance (enter 999 to calculate it from urine)**"
        ],
        'Symbols': [
            "PTID", "Lab date", "NHDWK", "PIDI", "BW0", "BWT", "TD", "Qb", "HDFpre",
            "HDFpost", "Qd", "name", "name", "KoA", "C0", "CT", "UO", "UU(N)", "KRU"
        ],
        'Units': [
            "", "dd/mm/yyyy", "Number", "days", "kg", "kg", "min", "ml/min",
            "ml/min", "ml/min", "ml/min", "", "", "ml/min", "mg/dl or mmol/l",
            "mg/dl or mmol/l", "ml/day", "mg/dl or mmol/l", "ml/min"
        ],
        'Min': [
            "", "", 1, 1, 20, "<BW0", 60, 100, 0, 0, 100, "", "", 500,
            "BUN 20", "BUN 10", 0, 0, 0
        ],
        'Max': [
            "", "", 3, 7, 140, 140, 480, 450, 250, 150, 800, "", "", 2500,
            "BUN 200", "BUN 100", 4000, "BUN700", 7
        ],
        'Example': [
            "N.N.", "03/02/2025", 1, 7, 71, 70, 240, 300, 0, 0, 500, "Fresenius",
            "FX10", 977, "BUN 80", "BUN 25", 1000, 300, 999
        ]
    }

    df_adequacy_input = pd.DataFrame(adequacy_input_data)
    st.dataframe(df_adequacy_input, hide_index=True)

    st.subheader("Table 1: Output Values")

    adequacy_output_data = {
        '#': list(range(1, 19)),
        'Output': [
            "Total Dialyzer Urea Clearance", "Single pool Kt/V", "Equilibrated Kt/V",
            "Urea distribution volume (double pool)", "Protein catabolic rate (g/kg/day)",
            "Renal urea clearance (calculated)", "KRU normalized per V 35 l",
            "Equivalent Renal Clearance per V 35 l", "EKRUN_variable target (10-1.5 KRUN)*",
            "EKRUN ≥10 – 1.5 KRUN *", "Standard Kt/V", "StdKt/V ≥ 2.1",
            "Ultrafiltration rate", "UFR ≤ 13 ml/h/kg",
            "TD needed for UFR=13 ml/h/kg", "Weekly net Ultrafiltration",
            "eKt/V to get EKRUN=12-KRUN", "eKt/V to be prescribed to get stdKt/V=2.3"
        ],
        'Symbols': [
            "Kd Tot", "spKt/V", "eKt/V", "Vdp", "PCRn", "KRU", "KRUN", "EKRUN",
            "EKRU_VTM", "Adequacy", "StdKt/V", "Adequacy", "UFR", "Adequacy", "TDN",
            "UFwk", "eKt/V", "eKt/V"
        ],
        'Units': [
            "ml/min", "dimensionless", "dimensionless", "l", "(g/kg/day)", "ml/min",
            "ml/min per 35l V", "ml/min per 35l V", "ml/min per 35l V", "Yes/No",
            "Volume/wk", "Yes/No", "ml/h per kg", "Yes/No", "min per session",
            "dimensionless", "dimensionless", "(l)"
        ],
        'Results': [
            205.11, 1.24, 1.10, 39.34, 0.68, 4.04, 3.59, 6.78, 4.61, "Yes",
            1.74, "No", 3.57, "Yes", 65.93, 1.00, 1.79, 2.47
        ]
    }
    df_adequacy_output = pd.DataFrame(adequacy_output_data)
    st.dataframe(df_adequacy_output, hide_index=True)

    st.markdown("""
    *Note.*
    This module measures various kinetic parameters, such as Kd, V, KRUN, PCRn, and the two ECCs, and verifies that at least the minimum stdKt/V and/or EKRUN has been achieved. The latter is calculated as follows: EKRUN = EKRU/V x 35 l, i.e., the equivalent renal clearance of urea (EKRU) is normalized, i.e., divided by the patient's urea volume V, and then multiplied by a typical volume equal to 35 l. Normalized renal urea clearance (KRU) is calculated in the same way: KRUN = KRU/V x 35 L.
    UKM-based treatment adequacy is defined as one with stdKt/V >= 2.1, or with EKRUN >= 10 - 1.5 KRUN. This last equation was introduced in the article "The reasons for a clinical trial on incremental haemodialysis", a research letter by Casino et al, on behalf of the Eudial Working Group of ERA-EDTA (NDT, 2020), in preparation of the protocol of "REAL LIFE" (RandomizEd clinical triaL on the effIcacy and saFety of incremental haEmodialysis), a randomized, multicentre and prospective study still ongoing (NCT04360694) evaluating the efficacy and safety of incremental hemodialysis compared to the standard regimen of three weekly sessions. It means that the minimum EKRUN to be delivered varies as a function of KRUN, being 10 ml/min for 35 l V when KRUN=0 and decreasing by 1.5 times the actual value of KRUN. For example, with KRUN = 2, minimum EKRUN = 10 - 1.5 x 2 = 7 ml/min for 35 l V. Of note, in anuric patients, EKRUN of 10 ml/min per 35 l V corresponds to eKt/V of 1.05 on 3HD/wk schedule, which in turn corresponds to stdKt/V=2.1 v/wk. This module also verifies the adequacy of the ultrafiltration rate, i.e., UFR<=13 ml/h/kg, and calculates the session duration (TDN) that would be required to achieve a UFR of 13 ml/h/kg. Finally, it estimates the weekly water load to be ultrafiltered.
    """)

    # --- Module 2: stdKt/V & EKRUN ---
    st.header("2. The 'stdKt/V & EKRUN' Module")
    st.write("""
    This module calculates the stdKt/V and EKRUN values predicted by the following parameters: Number of HD sessions per week, Normalised KRU (KRUN), delivered dialysis dose (eKt/V), length of the previous interdialytic interval (PIDI and associated interdialytic weight gain (IDWG). One can realize that this module can be used both to explore the prescription with the two different ECCs and to predict whether the prescribed treatment would deliver at least the minimum adequate value for stdKt/V (2.1 v/wk) and/or EKRUN (10 – KRUN ml/min per 35 l V) (see above).
    To highlight the differences associated with the use of stdKt/V and EKRUN in the once-weekly and twice-weekly regimens, we show two realistic practical examples.
    """)

    st.subheader("Table 2a: Example 1: stdKt/V & EKRUN on 1HD/wk")
    table2a_data = {
        '#': [1, 2, 3, 4, 5, 6],
        'Input': [
            "Patient identifier", "Number of HD per week", "Normalised KRU",
            "delivered eKt/V", "Preceding interdialytic interval",
            "Weight gain during PIDI"
        ],
        'Symbols': ["PTID", "NHDWK", "KRUN", "eKt/V", "PIDI", "IDWG"],
        'Units': ["", "number", "ml/min per 35l V", "number", "days", "kg"],
        'Min': ["", 1, 0, 0.5, 2, 0.1],
        'Max': ["", 3, 7, 2.0, 7, 5],
        'Example': ["N.N.", 1, 4, 1.2, 4, 1]
    }
    df_table2a_input = pd.DataFrame(table2a_data)
    st.dataframe(df_table2a_input, hide_index=True)

    table2a_output_data = {
        '#': [1, 2, 3, 4, 5],
        'Output': [
            "Weekly net Ultrafiltration", "Standard Kt/V",
            "Normalised Equivalent Renal Urea Clearance", "EKRUN variable target",
            "EKRUN minimum adequate"
        ],
        'Symbols': ["UFwk", "StdKt/V", "EKRUN", "EKRUN_VTM", "EKRUN min"],
        'Units': ["l", "v/wk", "ml/min per 35l V", "ml/min per 35l V", "ml/min per 35l V"],
        'Results': [1, 1.90, 7.41, 8.00, 4.00]
    }
    df_table2a_output = pd.DataFrame(table2a_output_data)
    st.dataframe(df_table2a_output, hide_index=True)

    st.markdown("""
    *Note.* In this virtual patient, undergoing a once-weekly dialysis regimen, with KRUN=4 ml/min for 35 l V and eKt/V=1.2, the value of stdKt/V would be 1.90, which is lower than both the prescription target, (2.3), and the adequate minimum (2.1). In practice, the use of stdKt/V does not allow the once-weekly regimen in this patient. Conversely, EKRUN would be 7.41 ml/min for 35 L V, which is lower than the EKRUN prescription target, which in this case would be 8.0 ml/min for 35 L V, but higher than the EKRUN adequate minimum, which in this case would be 4 ml/min for 35 L V. In practice, you could continue the twice-weekly dialysis with the same parameters until the next check-up.
    """)

    st.subheader("Table 2b: Example 2: stdKt/V & EKRUN on 2HD/wk")
    table2b_data = {
        '#': [1, 2, 3, 4, 5, 6],
        'Input': [
            "Patient identifier", "Number of HD per week", "Normalised KRU",
            "delivered eKt/V", "Preceding interdialytic interval",
            "Weight gain during PIDI"
        ],
        'Symbols': ["PTID", "NHDWK", "KRUN", "eKt/V", "PIDI", "IDWG"],
        'Units': ["", "number", "ml/min per 35l V", "number", "days", "kg"],
        'Min': ["", 1, 0, 0.5, 2, 0.1],
        'Max': ["", 3, 7, 2.0, 7, 5],
        'Example': ["N.N.", 2, 3, 1.0, 4, 1]
    }
    df_table2b_input = pd.DataFrame(table2b_data)
    st.dataframe(df_table2b_input, hide_index=True)

    table2b_output_data = {
        '#': [1, 2, 3, 4, 5],
        'Output': [
            "Weekly net Ultrafiltration", "Standard Kt/V",
            "Normalised Equivalent Renal Urea Clearance", "EKRUN variable target",
            "EKRUN minimum adequate"
        ],
        'Symbols': ["UFwk", "StdKt/V", "EKRUN", "EKRUN_VTM", "EKRUN min"],
        'Units': ["l", "v/wk", "ml/min per 35l V", "ml/min per 35l V", "ml/min per 35l V"],
        'Results': [1.75, 2.12, 9.1, 9.0, 5.5]
    }
    df_table2b_output = pd.DataFrame(table2b_output_data)
    st.dataframe(df_table2b_output, hide_index=True)

    st.markdown("""
    *Note.* In this patient on a 2HD/week regimen, with KRUN=3 ml/min for 35 l V and eKt/V=1.0, the calculated stdKt/V is 2.12, which is below the prescription target (2.3), but above the adequate minimum (2.1). In practice, you could continue the twice-weekly dialysis with the same parameters until the next check-up.
    Normalized EKRU is 9.1 ml/min for 35 l V, which is higher than the prescription target (9.0 ml/min for 35 l V), and even more so than the adequate minimum (4 ml/min for 35 l V).
    In conclusion, pending specific evidence, it can be hypothesized that dialysis prescription and assessment should preferentially use EKRUN in 1HD/wk regimen, and indifferently EKRUN or stdKt/V in 2HD/wk regimen.
    """)

    # --- Module 3: eKt/V ---
    st.header("3. The 'eKt/V' Module")
    st.write("""
    This module calculates the dialysis doses to be prescribed to achieve targets based on both stdKt/V and EKRUN with the selected treatment schedule, for given values of length of the previous interdialytic interval and associated weight gain, KRU and V of the patient.
    """)
    st.subheader("Table 3: eKt/V to be prescribed")

    table3_input_data = {
        '#': [1, 2, 3, 4, 5],
        'Input': [
            "Patient identifier", "Number of HD per week", "Normalised KRU",
            "Preceding interdialytic interval", "Weight gain during PIDI"
        ],
        'Symbols': ["PTID", "NHDWK", "KRUN", "PIDI", "IDWG"],
        'Units': ["", "number", "ml/min per 35l V", "days", "kg"],
        'Example': ["N.N.", 2, 3, 4, 1]
    }
    df_table3_input = pd.DataFrame(table3_input_data)
    st.dataframe(df_table3_input, hide_index=True)

    table3_output_data = {
        '#': [1, 2, 3],
        'Output': [
            "Weekly net Ultrafiltration", "eKt/V to get EKRUN = 12 - KRUN",
            "eKt/V to get stdKt/V = 2.3"
        ],
        'Symbols': ["UFwk", "EKRUN", "stdKt/V"],
        'Units': ["l", "ml/min per 35l V", "v/wk"],
        'Results': [3.50, 0.98, 1.18]
    }
    df_table3_output = pd.DataFrame(table3_output_data)
    st.dataframe(df_table3_output, hide_index=True)

    # --- Module 4: Kd&Qb ---
    st.header("4. The 'Kd&Qb' Module")
    st.write("""
    This module first calculates the dialysis clearance (Kd) of urea necessary (Kdn) to reach the target eKt/V as a function of V and KRU, and then the blood flow rate necessary (Qbn) to reach Kdn, based on the characteristics of the dialyzer, i.e., the dialyzer mass transfer coefficient for urea (KoA), and the values of the other parameters that determine Kd.
    """)
    st.subheader("Table 4: Dialyzer clearance and blood flow rate needed to reach the target value of eKt/V")

    table4_input_data = {
        '#': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'Input': [
            "Patient identifier", "Select a date", "Patient’s urea volume",
            "Expected intradialysis weight loss", "In vitro KoA of the dialyzer",
            "Pre-dialyzer infusion rate (set 0 in HD)",
            "Post-dialyzer infusion rate (set 0 in HD)", "Dialysate flow rate",
            "Session length", "eKt/V target"
        ],
        'Symbols': [
            "PTID", "date", "V", "UF", "KoA", "HDFPRE", "HDFPOST", "QD", "T", "eKt/V"
        ],
        'Units': [
            "", "dd/mm/yyyy", "l", "Kg = l", "ml/min", "ml/min", "ml/min",
            "ml/min", "min", "dimensionless"
        ],
        'Example': [
            "N.N.", "3/02/2025", 35, 2, 900, 0, 0, 500, 210, 1.2
        ]
    }
    df_table4_input = pd.DataFrame(table4_input_data)
    st.dataframe(df_table4_input, hide_index=True)

    table4_output_data = {
        '#': [1, 2],
        'Output': ["Dialyzer urea clearance needed", "Blod flow rate needed"],
        'Symbols': ["Kdn", "Qbn"],
        'Units': ["ml/min", "ml/min"],
        'Example': [187.4, 263]
    }
    df_table4_output = pd.DataFrame(table4_output_data)
    st.dataframe(df_table4_output, hide_index=True)

    # --- Module 5: KoA ---
    st.header("5. The 'KoA' Module")
    st.write("""
    This module calculates the in vitro value of the dialyzer mass transfer-area coefficient (KoA) for urea.

    The value of KoA in vitro is required as an input of the routine “Adequacy”, where it is first converted it into an estimated KoA in vivo value and then used to calculate the diffusive dialyzer clearance and total dialyzer clearance. It is also required by the Kd&Qb module, which calculates the Dialyzer clearance and blood flow rate needed to reach the target value of eKt/V.

    The in vitro KoA value can be obtained in three different ways:
    1. reading it on the dialyzer's technical data sheet, if available.
    2. Reading it on a list of the most commonly used dialyzers and their KoA values
    3. Entering the dialysis clearance data measured by the manufacturer under standard conditions with blood flow (Qb) typically of 200 or 300 ml/min and dialysate flow (Qd) of 500 or 800 ml/min, and low (<30 ml/min) or no ultrafiltration into the EuReCa "KoA" routine.
    """)
    st.subheader("Table 5: Calculating the dialyzer mass-transfer-area coefficient (KoA) for urea")

    table5_input_data = {
        '#': [1, 2, 3, 4],
        'Input': [
            "Blood flow rate", "Dialysate flow rate",
            "Ultrafiltration rate (<30 ml/min)",
            "Measured Dialyzer urea clearance"
        ],
        'Symbols': ["Qb", "Qd", "Qf", "Kd"],
        'Units': ["ml/min", "ml/min", "ml/min", "ml/min"],
        'Example': [300, 500, 0, 250]
    }
    df_table5_input = pd.DataFrame(table5_input_data)
    st.dataframe(df_table5_input, hide_index=True)

    table5_output_data = {
        '#': [1, 2],
        'Output': [
            "Diffusive Kd", "KoA in vitro of the dialyzer"
        ],
        'Symbols': ["Kd0", "KoA"],
        'Units': ["ml/min", "ml/min"],
        'Results': [250, 824]
    }
    df_table5_output = pd.DataFrame(table5_output_data)
    st.dataframe(df_table5_output, hide_index=True)