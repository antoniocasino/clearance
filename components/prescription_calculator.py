def prescription_calculation(inputs):
    """
    Performs prescription calculations based on input parameters.

    Args:
        nhdwk: Number of HD sessions per week.
        krun: KRUN value.
        pidi: PIDI value.
        idwg: IDWG value.

    Returns:
        A dictionary containing the calculated output values.
    """
    nhdwk = inputs['nhdwk']
    krun  = inputs['krun']    
    pidi  = inputs['pidi']
    idwg  = inputs['idwg']
    results = {}

    # Calculations
    ufwk = idwg / pidi * 7

    if nhdwk == 1:
        a2 = 4.7787; b2 = -0.8301; d2 = -0.0096; e2 = 0
        ektv_ekru = a2 + b2 * krun + d2 * ufwk + e2 * pidi
        a2 = 5.0319; b2 = -0.7051; d2 = -0.0282; e2 = 0
        ektv_stdktv = a2 + b2 * krun + d2 * ufwk + e2 * pidi
    elif nhdwk == 2:
        a2 = 2.0418; b2 = -0.3694; d2 = -0.0031; e2 = 0.0131
        ektv_ekru = a2 + b2 * krun + d2 * ufwk + e2 * pidi
        a2 = 2.1771; b2 = -0.3351; d2 = -0.0131; e2 = 0.0144
        ektv_stdktv = a2 + b2 * krun + d2 * ufwk + e2 * pidi
    elif nhdwk == 3:
        a2 = 1.2972; b2 = -0.2436; d2 = -0.0017; e2 = 0.0125
        ektv_ekru = a2 + b2 * krun + d2 * ufwk + e2 * pidi
        a2 = 1.2915; b2 = -0.2232; d2 = -0.0085; e2 = 0.0137
        ektv_stdktv = a2 + b2 * krun + d2 * ufwk + e2 * pidi

    # Output
    results['ufwk'] = ufwk
    results['ektv_ekru'] = ektv_ekru
    results['ektv_stdktv'] = ektv_stdktv

    return results
