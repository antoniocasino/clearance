# Haemodialysis Prescription Calculator

The App “Haemodialysis prescription calculator” provides guidance for the assessment and prescription of haemodialysis (HD) in general and of incremental HD (IHD) in particular. It is reserved exclusively for nephrologists involved in the treatment of patients on maintenance HD, as all calculations must necessarily be confirmed by qualified medical professionals before clinical use or for diagnostic purposes.

This App is an updated version of the software “SPEEDY”, acronym for “Spreadsheet for the Prescription of incrEmental haEmoDalYsis” (1), which uses the same equations as “Solute Solver” (2), the software recommended by the KDOQI clinical practice guidelines for HD adequacy (3), and provides comparable results.

The App is particularly useful in the early stages of kidney replacement treatment (KRT), where the presence of some residual kidney function (RKF) may allow an incremental approach to KRT. The latter consists of starting HD with a low frequency of sessions and/or low dialysis dose (Kt/V), to be increased progressively and appropriately as RKF decreases, to maintain the amount of dialysis delivered during the week in an adequate range, i.e., above the minimum permitted level. This entails the need to monthly monitor both RKF, expressed by the residual renal clearance of urea (KRU), and total weekly clearance (dialysis + renal), expressed by one of the two current adequacy indices, i.e., the standard Kt/V (stdKt/V) (3,4,5) and/or the equivalent renal clearance of urea (EKR) (6,7) to verify that they are at least equal to 2.1 volumes/week (3) or 10 - 1.5 x KRU (8), respectively.

The App is made up of 3 subroutines. The first one, called "Adequacy", calculates all the main parameters of the double pool urea kinetic model (UKM), and shows the dialysis dose values (eKt/V) necessary to prescribe adequacy with one, two, and three weekly sessions, respectively, according to criteria based alternately on stdKt/V or EKR with variable target (7), in order to choose the most suitable frequency and dose for the individual patient.

The second subroutine, called "Kd&Qb", first calculates the dialysis clearance (Kd) of urea necessary (Kdn) to reach the target eKt/V as a function of urea distribution volume (V) and KRU, and then the blood flow rate necessary (Qbn) to reach Kdn, based on the characteristics of the dialyzer, i.e., the dialyzer mass transfer coefficient for urea (KoA), and the values of the other parameters that determine Kd.

The third subroutine, called KoA, calculates the in vitro value of KoA, starting from the Kd data reported in the technical data sheet of the dialyzer together with the other relevant parameters

Check out the live demo:  [Clearance App](https://clearance.streamlit.app/)
