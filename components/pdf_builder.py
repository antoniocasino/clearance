from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from io import BytesIO

def create_vertical_table(data):
    """Creates a vertical table for a single patient's data."""

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),  # Header background
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),  # Header font
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),  # Center header text
        ('GRID', (0, 0), (1, -1), 1, colors.black),  # Add a grid
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Align keys to the left
        ('ALIGN', (1, 1), (1, -1), 'CENTER'), # Align values to the center
        ('VALIGN', (0,0), (1,-1), 'MIDDLE') # Vertically center content

    ]))
    return table

def create_pdf(form_data):
    pdf_buffer = BytesIO()        
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
    elements = []
          
    styles = getSampleStyleSheet()
    style_heading = ParagraphStyle(name='Heading', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=colors.blue, alignment=1)

    elements.append(Paragraph("Input Data", style_heading))
    elements.append(Spacer(1, 0.5*inch))

    count = 0
    patient_data1 = []
    for key, value in form_data.items():
        if count < len(form_data) - 2:  # Exclude the last two items
            patient_data1.append([key, value])
        count += 1  
    table1 = create_vertical_table(patient_data1)
    elements.append(table1)
    elements.append(Spacer(1, 0.5*inch)) 
   
    elements.append(Paragraph("Output Data", style_heading))
    elements.append(Spacer(1, 0.5*inch))
    patient_and_last_two_items = []
    count = 0
    for key, value in form_data.items():
        if count == 0 or count >= len(form_data) - 2:
           patient_and_last_two_items.append([key, value])
        count += 1
    table2 = create_vertical_table(patient_and_last_two_items)    
    
    elements.append(table2)
    elements.append(Spacer(1, 0.2*inch)) 
    doc.build(elements)

    pdf_buffer.seek(0)
    return pdf_buffer 

    """Converts a dictionary to a 2D array (list of lists).

    Args:
        data_dict: A dictionary where keys represent column headers
                   and values are lists of data for each column.
                   All value lists must have the same length.

    Returns:
        A 2D list (list of lists) representing the data, or None if
        the input dictionary is invalid (e.g., inconsistent value lengths).
    """

    if not isinstance(data_dict, dict):
        return None  # Or raise an exception: TypeError("Input must be a dictionary")

    if not data_dict:  # Handle empty dictionary case
        return []

    headers = list(data_dict.keys())    

    array_2d = [headers]  # Add the header row

    row = []
    for header in headers:
        row.append(data_dict[header])
        array_2d.append(row)

    return array_2d
