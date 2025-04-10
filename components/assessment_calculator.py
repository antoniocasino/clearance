def assessment_calculation(inputs): 
    """
    Performs assessment calculations based on input parameters.

    Args:
        nhdwk: Number of HD sessions per week.
        krun: KRUN value.
        ektv: ektv value.
        pidi: PIDI value.
        idwg: IDWG value.

    Returns:
        A dictionary containing the calculated output values.
    """
    nhdwk = inputs['nhdwk']
    krun  = inputs['krun']
    ektv  = inputs['ektv']
    pidi  = inputs['pidi']
    idwg  = inputs['idwg']
    results = {}

    # Calculations
    ufwk = idwg / pidi * 7

    if nhdwk == 1:
        a1 = 0.7491; b1 = 0.9543; c1 = 2.3544; d1 = 0.0225; e1 = 0
        ekrun = a1 + b1 * krun + c1 * ektv + d1 * ufwk + e1 * pidi
        a1 = 0.251; b1 = 0.2871; c1 = 0.4072; d1 = 0.0115; e1 = 0
        stdktv = a1 + b1 * krun + c1 * ektv + d1 * ufwk + e1 * pidi
        a2 = 4.7787; b2 = -0.8301; d2 = -0.0096; e2 = 0
        ektv_ekru = a2 + b2 * krun + d2 * ufwk + e2 * pidi
        a2 = 5.0319; b2 = -0.7051; d2 = -0.0282; e2 = 0
        ektv_stdktv = a2 + b2 * krun + d2 * ufwk + e2 * pidi
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

    # Output
    results['ufwk'] = ufwk
    results['stdktv'] = stdktv
    results['ekrun'] = ekrun
    results['12_minus_krun'] = 12 - krun
    results['10_minus_1.5_krun'] = 10 - 1.5 * krun

    return results

