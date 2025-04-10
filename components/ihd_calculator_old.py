import streamlit as st
import numpy as np
import math

def calculate_ihd(inputs):
    # --- Input ---
    PTID = inputs['PTID']
    LABDATE = inputs['LABDATE']
    NHDWK = inputs['NHDWK']
    PIDI = inputs['PIDI']
    BW0 = inputs['BW0']
    BWT = inputs['BWT']
    T = inputs['T']
    QB = inputs['QB']
    HDFPRE = inputs['HDFPRE']
    HDFPOST = inputs['HDFPOST']
    QD = inputs['QD']
    KOAvitro = inputs['KOAvitro']
    C0 = inputs['C0']
    CT = inputs['CT']
    KRUw = inputs['KRUw']
    UO = inputs['UO']
    UUN = inputs['UUN']


    # --- Calculations ---
    if BWT == BW0:
        BWT = BW0 - 0.1

    UF = (BW0 - BWT) * 1000
    Qf = UF / T

    if QD < 501:
        QDFAC = 1 + 0.0549 * (QD - 500) / 300
    else:
        QDFAC = 1

    KOA = 0.537 * KOAvitro * QDFAC
    QBW = 0.894 * QB + HDFPRE
    EZ = np.exp(KOA / QBW * (1 - QBW / QD))
    KDIF = QBW * (EZ - 1) / (EZ - QBW / QD)
    KCONV = (QBW - KDIF) / QBW * (Qf + HDFPRE + HDFPOST)
    DILUTIONFACTOR = 0.894 * QB / QBW
    KTOT = (KDIF + KCONV) * DILUTIONFACTOR

    if NHDWK > 2:
        GFAC = 0.0174 / PIDI
    else:
        GFAC = 0.0035

    SPKTV = -np.log(CT / C0 - GFAC * T / 60) + (4 - 3.5 * CT / C0) * (BW0 - BWT) / BWT
    VSP = KTOT * T / SPKTV / 1000
    EKTV = SPKTV * (T / (T + 30.7))
    FDPI = CT / (np.exp(np.log(C0) - EKTV / (SPKTV / np.log(C0 / CT))))
    VRATIO = np.log(FDPI * C0 / CT) / (FDPI * np.log(C0 / CT))
    VDP = VSP / VRATIO
    VBWRATIO = VDP / BWT

    if KRUw == 999:
        if PIDI == 7:
            TAC_SUN_water = C0 / 0.93
        else:
            TAC_SUN_water = C0 * (1.075 - (0.38 * (1 - CT / C0) + 0.059) * 1440 / (PIDI * 1440 - T))
        Kru = UO * UUN / TAC_SUN_water / 1440
    else:
        Kru = KRUw

    KR35 = Kru / VDP * 35

    # ... (Rest of the calculations - PCRn, EKR, StdKt/V, etc.) ...
    if NHDWK == 1:
        a = -0.5082 * math.pow(EKTV,2)
        b = 3.6195 * EKTV
        C = -0.0032
        PCRn = -0.46 + 0.01 * C0 + 0.09 * EKTV + 3.94 * Kru / VDP
    elif NHDWK == 2:
        a = -0.9646 * math.pow(EKTV,2)
        b = 7.5954 * EKTV
        C = -0.1598
        d = -1.15
        e = 4.56
        if PIDI == 4:
            f = 48
            g = 5.14
            h = 79            
        elif PIDI == 3:
            f = 33
            g = 3.6
            h = 83.2                
    elif NHDWK == 3:
        a = -1.6259 * math.pow(EKTV,2)
        b = 11.305 * EKTV
        C = -0.1925
        d = 0.7
        e = 3.08
        if PIDI == 3:
            f = 36.3
            g = 5.48
            h = 53.5
        elif PIDI == 2:
            f = 25.8
            g = 1.15
            h = 56.4

    if NHDWK > 1:
      AdjC0 = C0 * (1 + (d + e / EKTV) * Kru / VDP) # d and e need to be defined based on NHDWK
      PCRn = AdjC0 / (f + g * EKTV + h / EKTV) + 0.168 # f, g, and h need to be defined based on NHDWK and PIDI


    EKR35 = Kru / VDP * 35 + a + b + C  # a, b, and C need to be defined based on NHDWK

    AdeqEKR = "Yes" if (EKR35 - KR35) * 0.4 + KR35 > 3.999 else "No"

    num = 10080 * (1 - np.exp(-EKTV)) / T
    den1 = (1 - np.exp(-EKTV)) / EKTV + 10080 / (NHDWK * T) - 1
    S = num / den1
    den2 = 1 - 0.74 / NHDWK * UF / 1000 / VDP
    STDKTV = S / den2 + Kru * 10.08 / VDP

    AdeqStdKTV = "Yes" if STDKTV > 2.0999 else "No"

    UFR = UF / BWT / (T / 60)

    AdeqUFR = "Yes" if UFR < 13 else "No"

    TDN = UF / BWT / 13 * 60

    EKTV_1HDwk_EKRVTM = 0.1532 * KR35**2 - 2.225 * KR35 + 7.9006
    EKTV_2HDwk_EKRVTM = 0.0221 * KR35**2 - 0.4979 * KR35 + 2.24
    EKTV_3HDwk_EKRVTM = 0.0068 * KR35**2 - 0.2514 * KR35 + 1.2979

    EKTV_1HDwk_STDKTV = 0.1755 * KR35**2 - 2.7563 * KR35 + 10.999
    EKTV_2HDwk_STDKTV = 0.0776 * KR35**2 - 0.9091 * KR35 + 3.157
    EKTV_3HDwk_STDKTV = 0.0145 * KR35**2 - 0.2549 * KR35 + 1.2496


    # --- Output ---
    results = {
        "KTOT": KTOT, "SPKTV": SPKTV, "EKTV": EKTV, "VDP": VDP, "Kru": Kru,
        "KR35": KR35, "EKR35": EKR35, "AdeqEKR": AdeqEKR, "STDKTV": STDKTV,
        "AdeqStdKTV": AdeqStdKTV, "UFR": UFR, "AdeqUFR": AdeqUFR, "TDN": TDN,
        "PCRn": PCRn, "EKTV_1HDwk_EKRVTM": EKTV_1HDwk_EKRVTM,
        "EKTV_2HDwk_EKRVTM": EKTV_2HDwk_EKRVTM, "EKTV_3HDwk_EKRVTM": EKTV_3HDwk_EKRVTM,
        "EKTV_1HDwk_STDKTV": EKTV_1HDwk_STDKTV, "EKTV_2HDwk_STDKTV": EKTV_2HDwk_STDKTV,
        "EKTV_3HDwk_STDKTV": EKTV_3HDwk_STDKTV
    }
    return results
