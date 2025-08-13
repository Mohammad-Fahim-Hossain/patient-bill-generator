import os
import sys
import io
from collections import defaultdict
from datetime import datetime
from flask import Flask, request, send_file, render_template_string, jsonify
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

app = Flask(__name__)

# Configuration for production
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def get_file_path():
    """Get the path to the financials data file"""
    # Check if running as PyInstaller bundle
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'Financials.txt')
    # In production/development, the file should be in the same directory as app.py
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Financials.txt')

FILE_PATH = get_file_path()

# HTML template embedded in Python for Render deployment
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Patient Bill Generator</title>
  <style>
    body {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      padding: 40px;
      display: flex;
      justify-content: center;
      min-height: 100vh;
      margin: 0;
    }

    .container {
      background: #fff;
      padding: 30px 40px;
      border-radius: 12px;
      box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
      width: 100%;
      max-width: 500px;
      z-index: 1;
      margin: auto;
    }

    h1 {
      text-align: center;
      color: #333;
      margin-bottom: 30px;
      font-size: 28px;
    }

    label {
      display: block;
      margin-top: 15px;
      color: #333;
      font-weight: 600;
      font-size: 16px;
    }

    input[type="text"] {
      width: 100%;
      padding: 15px;
      margin-top: 10px;
      border: 2px solid #ddd;
      border-radius: 8px;
      font-size: 18px;
      background: #fdfdfd;
      transition: border-color 0.3s ease;
      box-sizing: border-box;
    }

    input[type="text"]:focus {
      outline: none;
      border-color: #667eea;
      box-shadow: 0 0 5px rgba(102, 126, 234, 0.3);
    }

    button {
      margin-top: 30px;
      width: 100%;
      padding: 16px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border: none;
      color: white;
      font-size: 18px;
      font-weight: bold;
      border-radius: 8px;
      cursor: pointer;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    button:hover {
      transform: translateY(-2px);
      box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }

    button:active {
      transform: translateY(0);
    }

    button:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      transform: none;
    }

    .footer {
      text-align: center;
      margin-top: 25px;
      font-size: 14px;
      color: #777;
    }

    .description {
      text-align: center;
      color: #666;
      margin-bottom: 20px;
      font-size: 14px;
    }

    .status {
      margin-top: 15px;
      padding: 10px;
      border-radius: 5px;
      display: none;
    }

    .status.success {
      background-color: #d4edda;
      color: #155724;
      border: 1px solid #c3e6cb;
    }

    .status.error {
      background-color: #f8d7da;
      color: #721c24;
      border: 1px solid #f5c6cb;
    }

    .spinner-overlay {
      display: none;
      position: fixed;
      top: 0; 
      left: 0;
      width: 100%; 
      height: 100%;
      background: rgba(255, 255, 255, 0.8);
      z-index: 999;
      justify-content: center;
      align-items: center;
    }

    .spinner {
      border: 8px solid #f3f3f3;
      border-top: 8px solid #667eea;
      border-radius: 50%;
      width: 60px;
      height: 60px;
      animation: spin 1s linear infinite;
    }

    @keyframes spin {
      0%   { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    .health-status {
      text-align: center;
      margin-bottom: 20px;
      font-size: 12px;
      color: #888;
    }

    @media (max-width: 600px) {
      body {
        padding: 20px;
      }
      
      .container {
        padding: 20px;
      }
      
      h1 {
        font-size: 24px;
      }
    }
  </style>
</head>
<body>
  <div class="spinner-overlay" id="loadingSpinner">
    <div class="spinner"></div>
  </div>

  <div class="container">
    <h1>Generate Patient Bills</h1>
    <div class="health-status">
      <span id="healthStatus">Checking system status...</span>
    </div>
    <div class="description">
      Enter the Patient ID to generate and download billing statements
    </div>

    <form id="billForm">
      <label for="patient_id">Patient ID:</label>
      <input type="text" id="patient_id" name="patient_id" required placeholder="Enter Patient ID">
      <button type="submit" id="submitBtn">Generate & Download Bill</button>
    </form>

    <div class="status" id="statusDiv"></div>

    <div class="footer">
      &copy; MYNX SOFTWARES INC | Deployed on Render
    </div>
  </div>

  <script>
    const form = document.getElementById('billForm');
    const spinner = document.getElementById('loadingSpinner');
    const statusDiv = document.getElementById('statusDiv');
    const submitBtn = document.getElementById('submitBtn');
    const healthStatus = document.getElementById('healthStatus');

    // Check health status on load
    window.addEventListener('load', function() {
      fetch('/health')
        .then(response => response.json())
        .then(data => {
          healthStatus.textContent = data.status === 'healthy' ? 'System operational ✓' : 'System issues detected';
          healthStatus.style.color = data.status === 'healthy' ? '#28a745' : '#dc3545';
        })
        .catch(() => {
          healthStatus.textContent = 'Unable to check system status';
          healthStatus.style.color = '#dc3545';
        });
    });

    function showStatus(message, type) {
      statusDiv.textContent = message;
      statusDiv.className = `status ${type}`;
      statusDiv.style.display = 'block';
      setTimeout(() => {
        statusDiv.style.display = 'none';
      }, 5000);
    }

    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      spinner.style.display = 'flex';
      submitBtn.disabled = true;
      submitBtn.textContent = 'Generating...';

      const patientId = document.getElementById('patient_id').value.trim();
      if (!patientId) {
        showStatus("Please enter a Patient ID", "error");
        spinner.style.display = 'none';
        submitBtn.disabled = false;
        submitBtn.textContent = 'Generate & Download Bill';
        return;
      }

      try {
        const response = await fetch(`/patient-pdf?patient_id=${encodeURIComponent(patientId)}`);

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(errorText || `Server responded with status ${response.status}`);
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${patientId}_bill.pdf`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
        
        showStatus("Bill generated and downloaded successfully!", "success");
      } catch (error) {
        console.error('Download error:', error);
        showStatus("Error: " + error.message, "error");
      } finally {
        spinner.style.display = 'none';
        submitBtn.disabled = false;
        submitBtn.textContent = 'Generate & Download Bill';
      }
    });
  </script>
</body>
</html>
"""

def search_rows(patient_id):
    """Search for patient rows in the data file"""
    rows = []
    try:
        if not os.path.exists(FILE_PATH):
            print(f"Warning: Data file not found at {FILE_PATH}")
            return rows
            
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            headers = f.readline().strip().split('|')
            for line in f:
                cols = line.strip().split('|')
                if len(cols) != len(headers):
                    continue
                row = dict(zip(headers, cols))
                if row.get('patient_id', '').lower() == patient_id.lower():
                    rows.append(row)
    except Exception as e:
        print(f"Error reading file: {e}")
    return rows

def get_raw_diagnosis_data(diagnosis_string):
    """Extract raw diagnosis data"""
    return diagnosis_string.strip() if diagnosis_string else ""

def extract_patient_data(rows):
    """Extract patient information (common for all services)"""
    return "9741 Preston Road Frisco, TX 75033-2793, (972) 335-2004"

def extract_provider_data_for_rows(rows):
    """Extract provider information for specific rows"""
    rendering_providers = set()
    for row in rows:
        first_name = row.get('rendering_first_name', '').strip()
        last_name = row.get('rendering_last_name', '').strip()
        if first_name and last_name:
            rendering_providers.add(f"Dr. {first_name} {last_name}")
        elif first_name:
            rendering_providers.add(f"Dr. {first_name}")
        elif last_name:
            rendering_providers.add(f"Dr. {last_name}")
    return ', '.join(sorted(rendering_providers)) if rendering_providers else 'N/A'

def extract_service_date_icd_codes(rows):
    """Extract ICD codes by service date - FIXED to properly match service dates"""
    service_date_diagnosis = defaultdict(set)
    for row in rows:
        service_date = row.get('date_of_service', '').strip()
        diagnosis_dxs = row.get('diagnosis_dxs', '').strip()
        if service_date and diagnosis_dxs:
            raw_diagnosis = get_raw_diagnosis_data(diagnosis_dxs)
            if raw_diagnosis:
                # Split multiple ICD codes if they are comma-separated or space-separated
                icd_codes = [code.strip() for code in raw_diagnosis.replace(',', ' ').split() if code.strip()]
                for code in icd_codes:
                    service_date_diagnosis[service_date].add(code)
    
    # Convert sets to sorted lists for consistent output
    return {date: sorted(list(codes)) for date, codes in service_date_diagnosis.items()}

def generate_merged_pdf(rows, location, service_date_icds):
    """Generate single merged PDF bill for patient with grand total on first page and one service date per page"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER

    MARGIN_LEFT = 50
    MARGIN_RIGHT = 50
    BOTTOM_MARGIN = 80  # Increased bottom margin to prevent overflow
    
    # Pre-calculate font metrics for speed
    font_metrics = {
        'title': ('Helvetica-Bold', 16),
        'section': ('Helvetica-Bold', 12),
        'normal': ('Helvetica', 11),
        'small': ('Helvetica', 9),
        'table_header': ('Helvetica-Bold', 10)  # Slightly smaller table headers
    }

    def set_font(font_type):
        font_name, font_size = font_metrics[font_type]
        c.setFont(font_name, font_size)

    def draw_title(y_pos):
        set_font('title')
        c.drawCentredString(width / 2, y_pos, "PATIENT BILLING STATEMENT")
        return y_pos - 40

    def draw_patient_info(y_pos):
        patient = rows[0]  # Use first row for patient info
        name = patient.get('patient_name', 'N/A')
        pid = patient.get('patient_id', 'N/A')
        
        # Pre-build address string
        address_parts = [
            patient.get('patient_address1', '').strip(),
            patient.get('patient_city', '').strip(),
            patient.get('patient_state', '').strip(),
            patient.get('patient_zip', '').strip()
        ]
        address = ", ".join(filter(None, address_parts))
        
        set_font('section')
        c.drawString(MARGIN_LEFT, y_pos, "PATIENT INFORMATION")
        y_pos -= 20
        set_font('normal')
        c.drawString(MARGIN_LEFT, y_pos, f"Name: {name}    Patient ID: #{pid}")
        y_pos -= 18
        c.drawString(MARGIN_LEFT, y_pos, f"Address: {address}")
        return y_pos - 30

    def draw_grand_total_summary(y_pos, grand_total, service_dates_count):
        """Draw grand total summary on first page"""
        set_font('section')
        c.drawString(MARGIN_LEFT, y_pos, "BILLING SUMMARY")
        y_pos -= 25
        
        # Draw summary box
        c.setLineWidth(1)
        box_height = 80
        box_width = 400
        c.rect(MARGIN_LEFT, y_pos - box_height, box_width, box_height)
        
        # Summary content
        set_font('normal')
        y_pos -= 20
        c.drawString(MARGIN_LEFT + 15, y_pos, f"Total Service Dates: {service_dates_count}")
        y_pos -= 20
        c.drawString(MARGIN_LEFT + 15, y_pos, f"Total Amount Due:")
        
        # Grand total amount - larger and prominent
        set_font('title')
        c.drawString(MARGIN_LEFT + 200, y_pos, f"${grand_total:,.2f}")
        
        y_pos -= 25
        set_font('small')
        c.drawString(MARGIN_LEFT + 15, y_pos, "Detailed billing information for each service date follows on subsequent pages.")
        
        return y_pos - 40

    def draw_provider_info(y_pos, provider):
        set_font('section')
        c.drawString(MARGIN_LEFT, y_pos, "PROVIDER INFORMATION")
        y_pos -= 20
        set_font('normal')
        c.drawString(MARGIN_LEFT, y_pos, f"Provider: {provider}")
        y_pos -= 18
        c.drawString(MARGIN_LEFT, y_pos, f"Location: {location}")
        return y_pos - 30

    def draw_services_table(y_pos, service_rows, service_date, page_num):
        set_font('section')
        c.drawString(MARGIN_LEFT, y_pos, f"SERVICES & CHARGES - {service_date}")
        y_pos -= 25

        headers = ["Sr.", "Date", "Code", "Description", "Modifier", "Units", "Charge"]
        # Column positions - keeping charge column position consistent
        col_positions = [MARGIN_LEFT, MARGIN_LEFT + 30, MARGIN_LEFT + 85, 
                        MARGIN_LEFT + 130, MARGIN_LEFT + 380, MARGIN_LEFT + 440, MARGIN_LEFT + 485]

        set_font('table_header')
        for i, header in enumerate(headers):
            c.drawString(col_positions[i], y_pos, header)
        
        y_pos -= 15
        c.setLineWidth(0.5)
        c.line(MARGIN_LEFT, y_pos, width - MARGIN_RIGHT, y_pos)
        y_pos -= 10

        # Pre-calculate total and prepare all row data
        total = 0.0
        processed_rows = []
        
        set_font('small')
        for i, row in enumerate(service_rows, 1):
            desc = str(row.get('code_desc', '') or '').strip().upper()
            
            # Fast numeric conversion
            try:
                cost = float(row.get('Charges') or 0)
            except (ValueError, TypeError):
                cost = 0.0
            
            total += cost
            
            # Improved description wrapping - optimized for available space
            desc_width_chars = 35  # Reduced to prevent overflow
            
            if len(desc) <= desc_width_chars:
                desc_lines = [desc] if desc else [""]
            else:
                # Simple word wrapping - faster than complex calculations
                words = desc.split()
                desc_lines = []
                current_line = ""
                
                for word in words:
                    test_line = f"{current_line} {word}" if current_line else word
                    if len(test_line) <= desc_width_chars:
                        current_line = test_line
                    else:
                        if current_line:
                            desc_lines.append(current_line)
                        current_line = word
                
                if current_line:
                    desc_lines.append(current_line)
            
            processed_rows.append({
                'sr': str(i),
                'date': str(row.get('date_of_service') or ''),
                'code': str(row.get('code') or ''),
                'desc_lines': desc_lines,
                'modifier': str(row.get('code_modifier_1') or ''),
                'units': str(row.get('ChargeUnits') or '1'),
                'charge': f"${cost:,.2f}",
                'cost': cost
            })

        # Draw all rows
        for row_data in processed_rows:
            # Better overflow prevention - check for more space including ICD section
            estimated_height = len(row_data['desc_lines']) * 12 + 80  # More space for subtotal and ICD
            if y_pos - estimated_height < BOTTOM_MARGIN + 60:  # Increased margin check
                # Draw page footer
                draw_footer(page_num)
                c.showPage()
                page_num += 1
                y_pos = height - 60
                
                # Redraw table headers on new page
                set_font('section')
                c.drawString(MARGIN_LEFT, y_pos, f"SERVICES & CHARGES - {service_date} (continued)")
                y_pos -= 25
                
                set_font('table_header')
                for i, header in enumerate(headers):
                    c.drawString(col_positions[i], y_pos, header)
                
                y_pos -= 15
                c.line(MARGIN_LEFT, y_pos, width - MARGIN_RIGHT, y_pos)
                y_pos -= 10
                set_font('small')
            
            # Draw first line with all columns
            values = [row_data['sr'], row_data['date'], row_data['code'], 
                     row_data['desc_lines'][0], row_data['modifier'], 
                     row_data['units'], row_data['charge']]
            
            for j, val in enumerate(values):
                c.drawString(col_positions[j], y_pos, val)
            
            # Draw additional description lines if any
            for desc_line in row_data['desc_lines'][1:]:
                y_pos -= 12
                c.drawString(col_positions[3], y_pos, desc_line)
            
            y_pos -= 18  # Reduced spacing between rows

        # FIXED: Draw subtotal aligned with charge column
        y_pos -= 10
        c.setLineWidth(0.5)
        c.line(MARGIN_LEFT, y_pos, width - MARGIN_RIGHT, y_pos)
        y_pos -= 15
        
        set_font('table_header')
        # FIXED: Align subtotal with the charge column (col_positions[6])
        charge_col_pos = col_positions[6]  # This is the charge column position
        
        # Draw subtotal label and value aligned with charge column
        c.drawRightString(charge_col_pos - 10, y_pos, "SUBTOTAL:")
        c.drawString(charge_col_pos, y_pos, f"${total:,.2f}")
        
        return y_pos - 25, page_num, total

    def draw_icd_section(y_pos, service_date, icds):
        # Better space checking for ICD section
        min_space_needed = 60  # Minimum space needed for ICD section
        
        if y_pos < BOTTOM_MARGIN + min_space_needed:
            return y_pos  # Skip if not enough space
            
        set_font('section')
        c.drawString(MARGIN_LEFT, y_pos, f"DIAGNOSIS CODES (ICD) - {service_date}:")
        y_pos -= 20
        
        # FIXED: Use the correct ICD codes for this specific service date
        icd_text = ', '.join(icds) if icds else "N/A"
        
        set_font('small')
        
        # Improved line wrapping for ICD codes
        max_chars = 75  # Adjusted for better fit
        if len(icd_text) <= max_chars:
            c.drawString(MARGIN_LEFT, y_pos, icd_text)
            y_pos -= 15
        else:
            words = icd_text.split(', ')
            current_line = ""
            
            for word in words:
                test_line = f"{current_line}, {word}" if current_line else word
                if len(test_line) <= max_chars:
                    current_line = test_line
                else:
                    if current_line:
                        c.drawString(MARGIN_LEFT, y_pos, current_line)
                        y_pos -= 15
                        # Better space checking
                        if y_pos < BOTTOM_MARGIN + 20:
                            break
                    current_line = word
            
            if current_line and y_pos >= BOTTOM_MARGIN + 20:
                c.drawString(MARGIN_LEFT, y_pos, current_line)
                y_pos -= 15
        
        return y_pos - 15  # Extra space after ICD section

    def draw_footer(page_num):
        # Pre-format timestamp
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(MARGIN_LEFT, 30, f"Generated on {timestamp}")
        c.drawRightString(width - MARGIN_RIGHT, 30, f"Page {page_num}")

    # Group rows by service date first to calculate grand total
    grouped_by_date = defaultdict(list)
    for row in rows:
        service_date = row.get('date_of_service', 'Unknown_Date')
        grouped_by_date[service_date].append(row)
    
    # Sort service dates
    sorted_dates = sorted(grouped_by_date.keys())
    
    # Calculate grand total first
    grand_total = 0.0
    for service_date in sorted_dates:
        service_rows = grouped_by_date[service_date]
        for row in service_rows:
            try:
                cost = float(row.get('Charges') or 0)
            except (ValueError, TypeError):
                cost = 0.0
            grand_total += cost

    # Start with first page - Summary page
    page_num = 1
    y = height - 60
    
    # Draw header sections on first page
    y = draw_title(y)
    y = draw_patient_info(y)
    y = draw_grand_total_summary(y, grand_total, len(sorted_dates))
    
    # Draw footer for summary page
    draw_footer(page_num)
    
    # Now create separate pages for each service date
    for service_date in sorted_dates:
        service_rows = grouped_by_date[service_date]
        
        # Start new page for each service date
        c.showPage()
        page_num += 1
        y = height - 60
        
        # Extract provider info specific to this service date
        provider = extract_provider_data_for_rows(service_rows)
        
        # Draw page title for this service date
        set_font('title')
        c.drawCentredString(width / 2, y, f"SERVICE DATE: {service_date}")
        y -= 50
        
        # Draw provider info for this service date
        y = draw_provider_info(y, provider)
        
        # Draw services table for this service date
        y, page_num, subtotal = draw_services_table(y, service_rows, service_date, page_num)
        
        # FIXED: Get ICD codes specific to current service date only
        current_service_icds = service_date_icds.get(service_date, [])
        print(f"DEBUG: Service date {service_date} has ICD codes: {current_service_icds}")  # Debug print
        y = draw_icd_section(y, service_date, current_service_icds)
        
        # Draw footer for this service date page
        draw_footer(page_num)

    # Single save operation
    c.save()
    buffer.seek(0)
    return buffer

# Routes
@app.route('/')
def serve_index():
    """Serve the main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        file_exists = os.path.exists(FILE_PATH)
        return jsonify({
            'status': 'healthy' if file_exists else 'degraded',
            'timestamp': datetime.now().isoformat(),
            'data_file_exists': file_exists,
            'data_file_path': FILE_PATH
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/patient-pdf')
def patient_pdf():
    """Generate and return patient PDF bill as single merged document"""
    patient_id = request.args.get('patient_id', '').strip()
    
    if not patient_id:
        return "Patient ID is required.", 400
    
    # Search for patient records
    rows = search_rows(patient_id)
    if not rows:
        return f"No records found for patient ID: {patient_id}", 404
    
    try:
        # Extract service date and ICD codes
        service_date_icds = extract_service_date_icd_codes(rows)
        print(f"DEBUG: Extracted ICD codes by date: {service_date_icds}")  # Debug print
        
        # Extract location data
        location = extract_patient_data(rows)
        
        # Generate single merged PDF with separate sections for each service date
        pdf_buffer = generate_merged_pdf(rows, location, service_date_icds)
        
        # Create safe download filename
        safe_patient_id = str(patient_id).replace(' ', '_').replace('/', '-').replace('\\', '-')
        download_name = f"{safe_patient_id}_bill.pdf"
        
        # Return single PDF file
        return send_file(
            pdf_buffer, 
            mimetype='application/pdf', 
            as_attachment=True, 
            download_name=download_name
        )
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return f"Error generating bill: {str(e)}", 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

# Production configuration
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'production') == 'development'
    
    # Print startup info
    print(f"Starting Patient Bill Generator...")
    print(f"Data file path: {FILE_PATH}")
    print(f"File exists: {os.path.exists(FILE_PATH)}")
    print(f"Running on port: {port}")
    print(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)