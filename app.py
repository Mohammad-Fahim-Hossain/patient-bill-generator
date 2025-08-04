import os
import sys
import io
import zipfile
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
      <button type="submit" id="submitBtn">Generate & Download Bills</button>
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
        submitBtn.textContent = 'Generate & Download Bills';
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
        link.download = `${patientId}_bills.zip`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
        
        showStatus("Bills generated and downloaded successfully!", "success");
      } catch (error) {
        console.error('Download error:', error);
        showStatus("Error: " + error.message, "error");
      } finally {
        spinner.style.display = 'none';
        submitBtn.disabled = false;
        submitBtn.textContent = 'Generate & Download Bills';
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
    """Extract patient and provider information"""
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
    provider = ', '.join(sorted(rendering_providers)) if rendering_providers else 'N/A'
    return provider, "9741 Preston Road Frisco, TX 75033-2793, (972) 335-2004"

def extract_service_date_icd_codes(rows):
    """Extract ICD codes by service date"""
    service_date_diagnosis = defaultdict(set)
    for row in rows:
        service_date = row.get('date_of_service', '').strip()
        diagnosis_dxs = row.get('diagnosis_dxs', '').strip()
        if service_date and diagnosis_dxs:
            raw_diagnosis = get_raw_diagnosis_data(diagnosis_dxs)
            if raw_diagnosis:
                service_date_diagnosis[service_date].add(raw_diagnosis)
    return {date: list(codes) for date, codes in service_date_diagnosis.items()}

def generate_pdf(rows, provider, location, service_date_icds):
    """Generate PDF bill for patient"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER

    MARGIN_LEFT = 50
    MARGIN_RIGHT = 50
    y = height - 60

    def draw_title():
        nonlocal y
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, y, "PATIENT BILLING STATEMENT")
        y -= 40

    def draw_patient_info():
        nonlocal y
        patient = rows[0]
        name = patient.get('patient_name', 'N/A')
        pid = patient.get('patient_id', 'N/A')
        address_parts = [
            patient.get('patient_address1', '').strip(),
            patient.get('patient_city', '').strip(),
            patient.get('patient_state', '').strip(),
            patient.get('patient_zip', '').strip()
        ]
        address = ", ".join([part for part in address_parts if part])
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(MARGIN_LEFT, y, "PATIENT INFORMATION")
        y -= 20
        c.setFont("Helvetica", 11)
        c.drawString(MARGIN_LEFT, y, f"Name: {name}    Patient ID: #{pid}")
        y -= 18
        c.drawString(MARGIN_LEFT, y, f"Address: {address}")
        y -= 30

    def draw_provider_info():
        nonlocal y
        c.setFont("Helvetica-Bold", 12)
        c.drawString(MARGIN_LEFT, y, "PROVIDER INFORMATION")
        y -= 20
        c.setFont("Helvetica", 11)
        c.drawString(MARGIN_LEFT, y, f"Provider: {provider}")
        y -= 18
        c.drawString(MARGIN_LEFT, y, f"Location: {location}")
        y -= 30

    def draw_services_table():
        nonlocal y
        c.setFont("Helvetica-Bold", 12)
        c.drawString(MARGIN_LEFT, y, "SERVICES & CHARGES")
        y -= 25
        total = 0.0

        headers = ["Sr.", "Date", "Code", "Description", "Modifier", "Units", "Charge"]
        col_positions = [
            MARGIN_LEFT,             # Sr.
            MARGIN_LEFT + 25,        # Date
            MARGIN_LEFT + 85,        # Code
            MARGIN_LEFT + 130,       # Description (wider space)
            MARGIN_LEFT + 400,       # Modifier
            MARGIN_LEFT + 450,       # Units
            MARGIN_LEFT + 490        # Charge
        ]

        c.setFont("Helvetica-Bold", 11)
        for i, header in enumerate(headers):
            c.drawString(col_positions[i], y, header)
        y -= 15
        c.setLineWidth(0.5)
        c.line(MARGIN_LEFT, y, width - MARGIN_RIGHT, y)
        y -= 10

        c.setFont("Helvetica", 9)  # Smaller font for more text
        for i, row in enumerate(rows, 1):
            desc = row.get('code_desc', '').strip().upper()
            # Handle potential None or non-numeric values in Charges
            try:
                cost = float(row.get('Charges', '0') or 0)
            except (ValueError, TypeError):
                cost = 0.0
            
            total += cost
            
            # Calculate available space for description (from col 3 to col 4)
            desc_width = col_positions[4] - col_positions[3] - 5  # 5 points padding
            
            # Check if we need multiple lines for description
            if desc and len(desc) > 0:
                # Calculate approximate characters that fit in the available width
                char_width = 5  # Approximate character width in points for size 9 font
                chars_per_line = int(desc_width / char_width)
                
                # Split description into lines if needed
                desc_lines = []
                if len(desc) <= chars_per_line:
                    desc_lines = [desc]
                else:
                    # Split long descriptions into multiple lines
                    words = desc.split(' ')
                    current_line = ""
                    for word in words:
                        test_line = current_line + " " + word if current_line else word
                        if len(test_line) <= chars_per_line:
                            current_line = test_line
                        else:
                            if current_line:
                                desc_lines.append(current_line)
                                current_line = word
                            else:
                                # Word is too long, split it
                                desc_lines.append(word[:chars_per_line])
                                current_line = word[chars_per_line:]
                    if current_line:
                        desc_lines.append(current_line)
            else:
                desc_lines = [""]
            
            # Draw the first line with all other values
            values = [
                str(i),
                str(row.get('date_of_service', '') or ''),
                str(row.get('code', '') or ''),
                desc_lines[0] if desc_lines else "",
                str(row.get('code_modifier_1', '') or ''),
                str(row.get('ChargeUnits', '1') or '1'),
                f"${cost:,.2f}"
            ]
            
            for j, val in enumerate(values):
                c.drawString(col_positions[j], y, val)
            
            # Draw additional description lines if needed
            if len(desc_lines) > 1:
                for desc_line in desc_lines[1:]:
                    y -= 12  # Smaller line spacing for continuation
                    c.drawString(col_positions[3], y, desc_line)
            
            y -= 20  # Standard row spacing

        y -= 5
        c.setFont("Helvetica-Bold", 11)
        c.drawString(col_positions[-2], y, "TOTAL:")
        c.drawString(col_positions[-1], y, f"${total:,.2f}")
        y -= 30

    def draw_icd_section():
        nonlocal y
        c.setFont("Helvetica-Bold", 12)
        c.drawString(MARGIN_LEFT, y, "DIAGNOSIS CODES (ICD):")
        y -= 20
        c.setFont("Helvetica", 10)
        all_icds = []
        for icds in service_date_icds.values():
            all_icds.extend(icds)
        icd_text = ', '.join(dict.fromkeys(all_icds)) or "N/A"
        # Handle long ICD text by wrapping lines
        words = icd_text.split(', ')
        current_line = ""
        line_width = 70  # Maximum characters per line
        
        for word in words:
            test_line = current_line + word + ", " if current_line else word + ", "
            if len(test_line) > line_width and current_line:
                # Draw current line and start new one
                c.drawString(MARGIN_LEFT, y, current_line.rstrip(', '))
                y -= 15
                current_line = word + ", "
            else:
                current_line = test_line
                
        # Draw the last line
        if current_line:
            c.drawString(MARGIN_LEFT, y, current_line.rstrip(', '))
            y -= 15
        y -= 10

    def draw_footer():
        now = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(MARGIN_LEFT, 30, f"Generated on {now}")
        c.drawRightString(width - MARGIN_RIGHT, 30, "Page 1")

    # Draw all sections
    draw_title()
    draw_patient_info()
    draw_provider_info()
    draw_services_table()
    draw_icd_section()
    draw_footer()

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
    """Generate and return patient PDF bills as ZIP"""
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
        
        # Group rows by date of service
        grouped = defaultdict(list)
        for row in rows:
            date_key = row.get('date_of_service', 'Unknown_Date')
            grouped[date_key].append(row)

        # Create ZIP file with all PDFs
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
            for date_of_service, group_rows in grouped.items():
                provider, location = extract_patient_data(group_rows)
                filtered_icds = {date_of_service: service_date_icds.get(date_of_service, [])}
                pdf_buffer = generate_pdf(group_rows, provider, location, filtered_icds)
                
                # Create safe filename - remove/replace problematic characters
                safe_date = date_of_service.replace('/', '-').replace(' ', '_').replace(':', '-')
                safe_patient_id = str(patient_id).replace(' ', '_').replace('/', '-').replace('\\', '-')
                filename = f"bill_{safe_patient_id}_{safe_date}.pdf"
                
                zf.writestr(filename, pdf_buffer.read())
        
        zip_buffer.seek(0)
        
        # Create safe download filename
        safe_download_name = f"{str(patient_id).replace(' ', '_')}_bills.zip"
        
        # Return ZIP file
        return send_file(
            zip_buffer, 
            mimetype='application/zip', 
            as_attachment=True, 
            download_name=safe_download_name
        )
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return f"Error generating bills: {str(e)}", 500

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