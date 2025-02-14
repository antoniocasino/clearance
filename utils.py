import math
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

def create_pdf(form_data):
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    for key, value in form_data.items():
        elements.append(Paragraph(f"{key}: {value}", styles['Normal']))

    doc.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer



def calculate_kdn_qbwn( vdp, uf, koavitro, hdfpre, hdfpost, qd, t, ekvt):
    """
    Calculates KDN, Qbw, and Qbn based on provided input parameters.

    Args:        
        vdp: Volume of distribution (L)
        uf: Ultrafiltration rate (mL/min)
        koavitro: In vitro mass transfer coefficient (mL/min)
        hdfpre: Pre-dialysis hematocrit (%)
        hdfpost: Post-dialysis hematocrit (%)
        qd: Blood flow rate (mL/min)
        t: Treatment time (min)
        ekvt: Dialyzer clearance (mL/min)

    Returns:
        A dictionary containing the calculated values of KDN and Qbn.
        Returns an error message if input values are outside acceptable ranges.
    """

    # Input validation
    if not (20 <= vdp <= 50):
        return "Error: VDP must be between 20 and 50."
    if not (0.1 <= uf <= 5):
        return "Error: UF must be between 0.1 and 5."
    if not (600 <= koavitro <= 2000):
        return "Error: KOAvitro must be between 600 and 2000."
    if not (0 <= hdfpre <= 250):
        return "Error: HDFPRE must be between 0 and 250."
    if not (0 <= hdfpost <= 150):
        return "Error: HDFPOST must be between 0 and 150."
    if not (300 <= qd <= 800):
        return "Error: QD must be between 300 and 800."
    if not (60 <= t <= 480):
        return "Error: T must be between 60 and 480."
    if not (0.3 <= ekvt <= 2.0):
        return "Error: EKVT must be between 0.3 and 2.0."


    # Calculate KDN
    spktv = (t + 30.7) * ekvt / t
    rpred = math.exp(-spktv / 1.18)
    f = 1 - 0.44 * spktv / (t / 60)
    vratio = math.log(f / rpred) / (f * math.log(1 / rpred))
    vsp = vdp * vratio
    kru = 0  # Assuming Kru is 0, as it's not defined in the VBA code.  Adjust if needed.
    kdn = spktv * vsp / t * 1000 - kru

    if qd < 501:
        qdfac = 1 + 0.0549 * (qd - 500) / 300
    else:
        qdfac = 1

    koa = 0.537 * koavitro * qdfac

    # Calculate Qbw, KTOT, and Qbn
    qf = uf * 1000 / t
    qbw = 300

    for _ in range(10):
        ez = math.exp(koa / qbw * (1 - qbw / qd))
        kdif = qbw * (ez - 1) / (ez - qbw / qd)
        kconv = (qbw - kdif) / qbw * (qf + hdfpre + hdfpost)
        dilution_factor = (qbw - hdfpre) / qbw
        ktot = (kdif + kconv) * dilution_factor
        kratio = ktot / kdn
        qbw = qbw / kratio

    qbn = (qbw - hdfpre) / 0.894

    return {"kdn": kdn, "qbn": qbn}


