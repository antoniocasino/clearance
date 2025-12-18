import math

def ihd_calculation(inputs):
    """
    Performs hemodialysis calculations based on input parameters.

    Args:
        ptid: Patient ID.
        labdate: Lab date.
        nhdwk: Number of HD sessions per week.
        pidi: PIDI value.
        bw0: Initial body weight (kg).
        bwt: Final body weight (kg).
        t: Treatment time (minutes).
        qb: Blood flow rate (mL/min).
        hdfpre: Pre-hemofiltration volume (mL).
        hdfpost: Post-hemofiltration volume (mL).
        qd: Dialysate flow rate (mL/min).
        koavitro: In vitro KOA value.
        c0: Initial concentration.
        ct: Final concentration.
        kruw: Kru value (or 999 if calculated).
        uo: Urine output.
        uun: Urine urea nitrogen.

    Returns:
        A dictionary containing the calculated output values.
    """

    # --- Input ---
    ptid = inputs['PTID']
    labdate = inputs['LABDATE']
    nhdwk = inputs['NHDWK']
    pidi = inputs['PIDI']
    bw0 = inputs['BW0']
    bwt = inputs['BWT']
    t = inputs['T']
    qb = inputs['QB']
    hdfpre = inputs['HDFPRE']
    hdfpost = inputs['HDFPOST']
    qd = inputs['QD']
    koavitro = inputs['KOAvitro']
    c0 = inputs['C0']/inputs['BUN']
    ct = inputs['CT']/inputs['BUN']
    kruw = inputs['KRUw']
    uo = inputs['UO']
    uun = inputs['UUN']/inputs['BUN']


    results = {}

    # BWT, QD & QBW, KTOT
    if bwt == bw0:
        bwt = bw0 - 0.1

    uf = (bw0 - bwt) * 1000
    qf = uf / t

    if qd < 501:
        qdfac = 1 + 0.0549 * (qd - 500) / 300
    else:
        qdfac = 1

    koa = 0.537 * koavitro * qdfac
    qbw = 0.894 * qb + hdfpre
    ez = math.exp(koa / qbw * (1 - qbw / qd))
    kdif = qbw * (ez - 1) / (ez - qbw / qd)
    kconv = (qbw - kdif) / qbw * (qf + hdfpre + hdfpost)
    dilutionfactor = 0.894 * qb / qbw
    ktot = (kdif + kconv) * dilutionfactor

    # Vsp & Vdp, spKt/V & eKt/V
    if nhdwk > 1:
        gfac = 0.0174 / pidi
    else:
        gfac = 0.0035

    gfac = 0.0174 / pidi
    spktv = -math.log(ct / c0 - gfac * t / 60) + (4 - 3.5 * ct / c0) * (bw0 - bwt) / bwt
    vsp = ktot * t / spktv / 1000
    ektv = spktv * (t / (t + 30.7))
    fdpi = ct / (math.exp(math.log(c0) - ektv / (spktv / math.log(c0 / ct))))
    vratio = math.log(fdpi * c0 / ct) / (fdpi * math.log(c0 / ct))
    vdp = vsp / vratio
    vbwratio = vdp / bwt

    # KRU & KR35
    if pidi == 7:
        tac_sun_water = c0 / 0.93
    else:
        tac_sun_water = c0 * (1.075 - (0.38 * (1 - ct / c0) + 0.059) * 1440 / (pidi * 1440 - t))

    if kruw == 999:
        kru = uo * uun / tac_sun_water / 1440
    else:
        kru = kruw
    kr35 = kru / vdp * 35

    # EKRUN & stdKt/V + eKtV_EKRU & eKtV_stdKtV
    ufwk = (bw0 - bwt) / (pidi * 1440 - t) * (10080 - nhdwk * t)
    krun = kr35

    if nhdwk == 1:
        a1 = 0.7491; b1 = 0.9543; c1 = 2.3544; d1 = 0.0225; e1 = 0
        ekrun = a1 + b1 * krun + c1 * ektv + d1 * ufwk + e1 * pidi
        a1 = 0.251; b1 = 0.2871; c1 = 0.4072; d1 = 0.0115; e1 = 0
        stdktv = a1 + b1 * krun + c1 * ektv + d1 * ufwk + e1 * pidi
        a2 = 4.7787; b2 = -0.8301; d2 = -0.0096; e2 = 0
        ektv_ekru = a2 + b2 * krun + d2 * ufwk + e2 * pidi
        a2 = 5.0319; b2 = -0.7051; d2 = -0.0282; e2 = 0
        ektv_stdktv = a2 + b2 * krun + d2 * ufwk + e2 * pidi
        pcrn = -0.46 + 0.01 * c0 + 0.09 * ektv + 3.94 * kru / vdp
    elif nhdwk == 2:
        a1 = 1.1843; b1 = 0.9565; c1 = 5.2971; d1 = 0.0166; e1 = -0.0694
        ekrun = a1 + b1 * krun + c1 * ektv + d1 * ufwk + e1 * pidi
        a1 = 0.4262; b1 = 0.2884; c1 = 0.8607; d1 = 0.0113; e1 = -0.0124
        stdktv = a1 + b1 * krun + c1 * ektv + d1 * ufwk + e1 * pidi
        a2 = 2.0418; b2 = -0.3694; d2 = -0.0031; e2 = 0.0131
        ektv_ekru = a2 + b2 * krun + d2 * ufwk + e2 * pidi
        a2 = 2.1771; b2 = -0.3351; d2 = -0.0131; e2 = 0.0144
        ektv_stdktv = a2 + b2 * krun + d2 * ufwk + e2 * pidi
        d = -1.15; e = 4.56
        if pidi == 4:
            f = 48; g = 5.14; h = 79
        elif pidi == 3:
            f = 33; g = 3.6; h = 83.2
        adjc0 = c0 * (1 + (d + e / ektv) * kru / vdp)
        pcrn = adjc0 / (f + g * ektv + h / ektv) + 0.168
    elif nhdwk == 3:
        a1 = 1.5813; b1 = 0.9561; c1 = 8.0314; d1 = 0.0135; e1 = -0.1001
        ekrun = a1 + b1 * krun + c1 * ektv + d1 * ufwk + e1 * pidi
        a1 = 0.6302; b1 = 0.2886; c1 = 1.2929; d1 = 0.011; e1 = -0.0177
        stdktv = a1 + b1 * krun + c1 * ektv + d1 * ufwk + e1 * pidi
        a2 = 1.2972; b2 = -0.2436; d2 = -0.0017; e2 = 0.0125
        ektv_ekru = a2 + b2 * krun + d2 * ufwk + e2 * pidi
        a2 = 1.2915; b2 = -0.2232; d2 = -0.0085; e2 = 0.0137
        ektv_stdktv = a2 + b2 * krun + d2 * ufwk + e2 * pidi
        d = 0.7; e = 3.08
        if pidi == 3:
            f = 36.3; g = 5.48; h = 53.5
        elif pidi == 2:
            f = 25.8; g = 1.15; h = 56.4
        adjc0 = c0 * (1 + (d + e / ektv) * kru / vdp)
        pcrn = adjc0 / (f + g * ektv + h / ektv) + 0.168

    ekrun_min = 10 - 1.5 * krun
    adeqekr = "Yes" if ekrun > ekrun_min else "No"
    adeqstdktv = "Yes" if stdktv > 2.0999 else "No"
    ufr = uf / bwt / (t / 60)
    adequfr = "Yes" if ufr < 13 else "No"
    tdn = uf / bwt / 13 * 60

    # Simulated prescriptions for different treatments per week
    # 1 treatment per week
    a2 = 4.7787
    b2 = -0.8301
    d2 = -0.0096
    e2 = 0
    ektv_E1 = compute_ektv(a2,b2,d2,e2,krun,ufwk,pidi)
    a2 = 5.0319
    b2 = -0.7051
    d2 = -0.0282
    e2 = 0
    ektv_s1 = compute_ektv(a2,b2,d2,e2,krun,ufwk,pidi)
    # 2 treatments per week
    a2 = 2.0418
    b2 = -0.3694
    d2 = -0.0031
    e2 = 0.0131
    ektv_E2 = compute_ektv(a2,b2,d2,e2,krun,ufwk,pidi)
    a2 = 2.1771
    b2 = -0.3351
    d2 = -0.0131
    e2 = 0.0144
    ektv_s2 = compute_ektv(a2,b2,d2,e2,krun,ufwk,pidi)
    ## 3 treatments per week
    a2 = 1.2972
    b2 = -0.2436
    d2 = -0.0017
    e2 = 0.0125
    ektv_E3 = compute_ektv(a2,b2,d2,e2,krun,ufwk,pidi)
    a2 = 1.2915
    b2 = -0.2232
    d2 = -0.0085
    e2 = 0.0137
    ektv_s3 = compute_ektv(a2,b2,d2,e2,krun,ufwk,pidi)


    # --- Output ---
    results = {
        "KTOT": ktot, "SPKTV": spktv, "EKTV": ektv, "VDP": vdp,"PCRN":pcrn, "Kru": kru,
        "krun": krun, "ekrun": ekrun, "ekrun_min":ekrun_min, "AdeqEKR": adeqekr, "STDKTV": stdktv,
        "AdeqStdKTV": adeqstdktv, "UFR": ufr, "AdeqUFR": adequfr, "TDN": tdn,
        "Ufwk": ufwk, "Ektv_ekru": ektv_ekru,
        "Ektv_stdktv": ektv_stdktv, "ektv_E1":ektv_E1,"ektv_s1":ektv_s1,"ektv_E2":ektv_E2,"ektv_s2":ektv_s2,
        "ektv_E3":ektv_E3,"ektv_s3":ektv_s3
    }  
    
    return results

def compute_ektv(a2,b2,d2,e2,krun,ufwk,pidi):
    return a2 + b2 * krun + d2 * ufwk + e2 * pidi