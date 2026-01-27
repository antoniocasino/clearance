from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
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

def create_complex_table(data_values):
    """
    Creates the specific 5-column table with merged headers 
    shown in the image.
    Expects data_values to be a list of 3 rows (lists), 
    each containing 4 numbers corresponding to the columns.
    """
    # 1. Define the Header Rows
    # Row 0: Top headers with placeholders for spanned cells
    # Row 1: Sub headers
    table_data = [
        ['', 'To obtain stdKt/V target', '', 'To obtain EKRUN target', ''], 
        ['', 'eKt/V', 'spKt/V', 'eKt/V', 'spKt/V']
    ]
    
    # 2. Define the Row Labels
    row_labels = ["1 HD/week", "2 HD/week", "3 HD/week"]
    
    # 3. Combine Labels with Data
    # If data_values is missing or incomplete, we fill with placeholders
    if not data_values:
        data_values = [["-"]*4 for _ in range(3)]

    for i, label in enumerate(row_labels):
        # Safety check to ensure we don't crash if data is missing rows
        row_vals = data_values[i] if i < len(data_values) else ["-", "-", "-", "-"]
        # Create the full row: [Label, val1, val2, val3, val4]
        table_data.append([label] + row_vals)

    # 4. Create Table Object
    # We set specific column widths to match the look: first col slightly wider
    t = Table(table_data, colWidths=[1.2*inch, 1*inch, 1*inch, 1*inch, 1*inch])

    # 5. Apply Styling
    t.setStyle(TableStyle([
        # --- Merging Cells (Spans) ---
        # Span 'To obtain stdKt/V target' across col 1 and 2 (indices 1,2) of row 0
        ('SPAN', (1, 0), (2, 0)),
        # Span 'To obtain EKRUN target' across col 3 and 4 (indices 3,4) of row 0
        ('SPAN', (3, 0), (4, 0)),
        # Span the empty corner cell (optional, but keeps it clean)
        ('SPAN', (0, 0), (0, 1)),

        # --- Fonts & Alignment ---
        ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'), # Bold headers
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),           # Center all text
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),          # Vertically center
        
        # --- Background Colors ---
        # Top Header Row (White or Light Grey)
        ('BACKGROUND', (1, 0), (-1, 0), colors.whitesmoke),
        # Sub-header Row + First Column (Grey)
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey), # First column
        ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey), # Sub-headers

        # --- Borders ---
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    return t

def create_pdf(input_data,output_data,simulated_data=None,pageBreak=False):
    pdf_buffer = BytesIO()        
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
    elements = []
          
    styles = getSampleStyleSheet()
    style_heading = ParagraphStyle(name='Heading', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=colors.blue, alignment=1)

    elements.append(Paragraph("Input Data", style_heading))
    elements.append(Spacer(1, 0.5*inch))
    
    patient_data1 = []
    for key, value in input_data.items():       
        patient_data1.append([key, value])
        
    table1 = create_vertical_table(patient_data1)
    elements.append(table1)
    elements.append(Spacer(1, 0.5*inch)) 
   
    if pageBreak:
        elements.append(PageBreak())
    elements.append(Paragraph("Output Data", style_heading))
    elements.append(Spacer(1, 0.5*inch))
    patient_outputs = []

    for key, value in output_data.items():        
        patient_outputs.append([key, value])        
    
    table2 = create_vertical_table(patient_outputs)        
    elements.append(table2)
    elements.append(Spacer(1, 0.2*inch)) 
    
    if simulated_data:
        elements.append(Spacer(1, 0.5*inch))    
        elements.append(Paragraph("Simulated Prescriptions", style_heading))
        elements.append(Spacer(1, 0.5*inch))           
        
        table3 = create_complex_table(simulated_data)
        elements.append(table3)
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
