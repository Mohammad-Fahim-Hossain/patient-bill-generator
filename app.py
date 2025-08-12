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

# Enhanced HTML template with modern UI and animations
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Patient Bill Generator</title>
  <style>
    :root {
      --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
      --error-gradient: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
      --glass-bg: rgba(255, 255, 255, 0.25);
      --glass-border: rgba(255, 255, 255, 0.18);
      --text-primary: #2d3748;
      --text-secondary: #4a5568;
      --text-light: #718096;
      --shadow-soft: 0 20px 40px rgba(0, 0, 0, 0.1);
      --shadow-hover: 0 30px 60px rgba(0, 0, 0, 0.15);
      --border-radius: 20px;
      --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      background: var(--primary-gradient);
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
      position: relative;
      overflow-x: hidden;
    }

    /* Animated background elements */
    body::before {
      content: '';
      position: fixed;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E") repeat;
      animation: float 20s ease-in-out infinite;
      pointer-events: none;
      z-index: 0;
    }

    @keyframes float {
      0%, 100% { transform: translateY(0px) rotate(0deg); }
      50% { transform: translateY(-20px) rotate(180deg); }
    }

    .floating-shapes {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 1;
    }

    .shape {
      position: absolute;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.1);
      animation: floatingShapes 15s ease-in-out infinite;
    }

    .shape:nth-child(1) {
      width: 80px;
      height: 80px;
      top: 10%;
      left: 10%;
      animation-delay: -2s;
    }

    .shape:nth-child(2) {
      width: 120px;
      height: 120px;
      top: 20%;
      right: 15%;
      animation-delay: -4s;
    }

    .shape:nth-child(3) {
      width: 60px;
      height: 60px;
      bottom: 20%;
      left: 20%;
      animation-delay: -6s;
    }

    .shape:nth-child(4) {
      width: 100px;
      height: 100px;
      bottom: 15%;
      right: 20%;
      animation-delay: -8s;
    }

    @keyframes floatingShapes {
      0%, 100% {
        transform: translateY(0px) translateX(0px) scale(1);
        opacity: 0.7;
      }
      25% {
        transform: translateY(-30px) translateX(20px) scale(1.1);
        opacity: 0.4;
      }
      50% {
        transform: translateY(-20px) translateX(-15px) scale(0.9);
        opacity: 0.8;
      }
      75% {
        transform: translateY(10px) translateX(25px) scale(1.05);
        opacity: 0.5;
      }
    }

    .container {
      background: var(--glass-bg);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid var(--glass-border);
      padding: 40px;
      border-radius: var(--border-radius);
      box-shadow: var(--shadow-soft);
      width: 100%;
      max-width: 480px;
      z-index: 10;
      position: relative;
      transition: var(--transition);
      animation: containerSlideIn 0.8s ease-out;
    }

    .container:hover {
      transform: translateY(-5px);
      box-shadow: var(--shadow-hover);
    }

    @keyframes containerSlideIn {
      0% {
        opacity: 0;
        transform: translateY(30px) scale(0.95);
      }
      100% {
        opacity: 1;
        transform: translateY(0) scale(1);
      }
    }

    .header {
      text-align: center;
      margin-bottom: 35px;
    }

    .header h1 {
      color: white;
      font-size: 32px;
      font-weight: 800;
      margin-bottom: 8px;
      text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
      animation: titleGlow 2s ease-in-out infinite alternate;
    }

    @keyframes titleGlow {
      0% { text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2); }
      100% { text-shadow: 0 2px 20px rgba(255, 255, 255, 0.3); }
    }

    .subtitle {
      color: rgba(255, 255, 255, 0.9);
      font-size: 16px;
      font-weight: 400;
      opacity: 0;
      animation: fadeInUp 0.8s ease-out 0.3s forwards;
    }

    @keyframes fadeInUp {
      0% {
        opacity: 0;
        transform: translateY(20px);
      }
      100% {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .health-status {
      text-align: center;
      margin-bottom: 25px;
      padding: 12px;
      border-radius: 12px;
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 255, 255, 0.2);
      transition: var(--transition);
    }

    .health-status span {
      font-size: 14px;
      font-weight: 600;
      color: rgba(255, 255, 255, 0.9);
    }

    .form-group {
      margin-bottom: 25px;
      opacity: 0;
      animation: fadeInUp 0.8s ease-out 0.5s forwards;
    }

    label {
      display: block;
      margin-bottom: 8px;
      color: white;
      font-weight: 600;
      font-size: 15px;
      text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
    }

    .input-container {
      position: relative;
    }

    input[type="text"] {
      width: 100%;
      padding: 16px 20px;
      border: 2px solid rgba(255, 255, 255, 0.2);
      border-radius: 15px;
      font-size: 16px;
      background: rgba(255, 255, 255, 0.1);
      color: white;
      backdrop-filter: blur(10px);
      transition: var(--transition);
      outline: none;
    }

    input[type="text"]::placeholder {
      color: rgba(255, 255, 255, 0.6);
    }

    input[type="text"]:focus {
      border-color: rgba(255, 255, 255, 0.6);
      background: rgba(255, 255, 255, 0.15);
      box-shadow: 0 0 20px rgba(255, 255, 255, 0.2);
      transform: scale(1.02);
    }

    .input-icon {
      position: absolute;
      right: 15px;
      top: 50%;
      transform: translateY(-50%);
      color: rgba(255, 255, 255, 0.6);
      transition: var(--transition);
    }

    input[type="text"]:focus + .input-icon {
      color: rgba(255, 255, 255, 0.9);
      transform: translateY(-50%) scale(1.2);
    }

    .submit-btn {
      width: 100%;
      padding: 18px;
      background: var(--secondary-gradient);
      border: none;
      color: white;
      font-size: 18px;
      font-weight: 700;
      border-radius: 15px;
      cursor: pointer;
      transition: var(--transition);
      position: relative;
      overflow: hidden;
      opacity: 0;
      animation: fadeInUp 0.8s ease-out 0.7s forwards;
    }

    .submit-btn::before {
      content: '';
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 100%;
      background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
      transition: left 0.6s;
    }

    .submit-btn:hover::before {
      left: 100%;
    }

    .submit-btn:hover {
      transform: translateY(-3px);
      box-shadow: 0 15px 30px rgba(245, 87, 108, 0.4);
    }

    .submit-btn:active {
      transform: translateY(-1px);
    }

    .submit-btn:disabled {
      opacity: 0.7;
      cursor: not-allowed;
      transform: none;
    }

    .submit-btn.generating {
      background: var(--success-gradient);
      animation: pulse 1.5s ease-in-out infinite;
    }

    @keyframes pulse {
      0%, 100% { transform: scale(1); }
      50% { transform: scale(1.05); }
    }

    /* Enhanced loading spinner */
    .spinner-overlay {
      display: none;
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.8);
      backdrop-filter: blur(10px);
      z-index: 9999;
      justify-content: center;
      align-items: center;
      animation: fadeIn 0.3s ease-out;
    }

    @keyframes fadeIn {
      0% { opacity: 0; }
      100% { opacity: 1; }
    }

    .spinner-container {
      text-align: center;
      color: white;
    }

    .spinner {
      width: 80px;
      height: 80px;
      border: 4px solid rgba(255, 255, 255, 0.3);
      border-top: 4px solid #ffffff;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 20px;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    .loading-text {
      font-size: 18px;
      font-weight: 600;
      margin-bottom: 10px;
      animation: loadingPulse 1.5s ease-in-out infinite;
    }

    .loading-subtext {
      font-size: 14px;
      color: rgba(255, 255, 255, 0.8);
    }

    @keyframes loadingPulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.7; }
    }

    /* Enhanced status messages */
    .status {
      margin-top: 20px;
      padding: 16px 20px;
      border-radius: 12px;
      display: none;
      font-weight: 600;
      text-align: center;
      animation: statusSlideIn 0.5s ease-out;
      backdrop-filter: blur(10px);
    }

    @keyframes statusSlideIn {
      0% {
        opacity: 0;
        transform: translateY(-20px);
      }
      100% {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .status.success {
      background: rgba(76, 175, 80, 0.2);
      color: #e8f5e8;
      border: 2px solid rgba(76, 175, 80, 0.3);
      box-shadow: 0 4px 20px rgba(76, 175, 80, 0.2);
    }

    .status.error {
      background: rgba(244, 67, 54, 0.2);
      color: #ffebee;
      border: 2px solid rgba(244, 67, 54, 0.3);
      box-shadow: 0 4px 20px rgba(244, 67, 54, 0.2);
    }

    .footer {
      text-align: center;
      margin-top: 30px;
      font-size: 13px;
      color: rgba(255, 255, 255, 0.7);
      opacity: 0;
      animation: fadeInUp 0.8s ease-out 1s forwards;
    }

    .footer a {
      color: rgba(255, 255, 255, 0.9);
      text-decoration: none;
      transition: var(--transition);
    }

    .footer a:hover {
      color: white;
      text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
    }

    /* Progress indicator */
    .progress-steps {
      display: none;
      margin-top: 15px;
    }

    .progress-steps.active {
      display: block;
      animation: fadeInUp 0.5s ease-out;
    }

    .step {
      display: flex;
      align-items: center;
      margin-bottom: 8px;
      font-size: 14px;
      color: rgba(255, 255, 255, 0.8);
    }

    .step-icon {
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.3);
      margin-right: 10px;
      transition: var(--transition);
    }

    .step.completed .step-icon {
      background: #4CAF50;
      animation: checkmark 0.5s ease-out;
    }

    .step.active .step-icon {
      background: #2196F3;
      animation: pulse 1s ease-in-out infinite;
    }

    @keyframes checkmark {
      0% { transform: scale(0.5); }
      100% { transform: scale(1); }
    }

    /* Responsive design */
    @media (max-width: 768px) {
      .container {
        padding: 30px 25px;
        margin: 15px;
      }
      
      .header h1 {
        font-size: 28px;
      }
      
      .subtitle {
        font-size: 14px;
      }

      .submit-btn {
        padding: 16px;
        font-size: 16px;
      }
    }

    @media (max-width: 480px) {
      body {
        padding: 10px;
      }
      
      .container {
        padding: 25px 20px;
      }
      
      .header h1 {
        font-size: 24px;
      }
    }

    /* Dark mode enhancements */
    @media (prefers-color-scheme: dark) {
      .container {
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
      }
      
      input[type="text"] {
        background: rgba(0, 0, 0, 0.2);
        border-color: rgba(255, 255, 255, 0.1);
      }
    }
  </style>
</head>
<body>
  <!-- Animated background shapes -->
  <div class="floating-shapes">
    <div class="shape"></div>
    <div class="shape"></div>
    <div class="shape"></div>
    <div class="shape"></div>
  </div>

  <!-- Enhanced loading spinner -->
  <div class="spinner-overlay" id="loadingSpinner">
    <div class="spinner-container">
      <div class="spinner"></div>
      <div class="loading-text">Generating Your Bill</div>
      <div class="loading-subtext">Please wait while we process your request...</div>
      <div class="progress-steps" id="progressSteps">
        <div class="step" id="step1">
          <div class="step-icon"></div>
          <span>Searching patient records...</span>
        </div>
        <div class="step" id="step2">
          <div class="step-icon"></div>
          <span>Calculating charges...</span>
        </div>
        <div class="step" id="step3">
          <div class="step-icon"></div>
          <span>Generating PDF document...</span>
        </div>
        <div class="step" id="step4">
          <div class="step-icon"></div>
          <span>Preparing download...</span>
        </div>
      </div>
    </div>
  </div>

  <div class="container">
    <div class="header">
      <h1>Patient Bill Generator</h1>
      <div class="subtitle">Generate and download professional billing statements</div>
    </div>

    <div class="health-status">
      <span id="healthStatus">🔄 Checking system status...</span>
    </div>

    <form id="billForm">
      <div class="form-group">
        <label for="patient_id">Patient ID</label>
        <div class="input-container">
          <input type="text" id="patient_id" name="patient_id" required 
                 placeholder="Enter Patient ID (e.g., P001, 12345)">
          <div class="input-icon">👤</div>
        </div>
      </div>

      <button type="submit" class="submit-btn" id="submitBtn">
        <span>Generate & Download Bill</span>
      </button>
    </form>

    <div class="status" id="statusDiv"></div>

    <div class="footer">
      <strong>&copy; 2024 MYNX SOFTWARES INC</strong><br>
      Deployed with ❤️ on <a href="#" target="_blank">Render</a>
    </div>
  </div>

  <script>
    const form = document.getElementById('billForm');
    const spinner = document.getElementById('loadingSpinner');
    const statusDiv = document.getElementById('statusDiv');
    const submitBtn = document.getElementById('submitBtn');
    const healthStatus = document.getElementById('healthStatus');
    const progressSteps = document.getElementById('progressSteps');

    // Enhanced health status check
    function checkHealthStatus() {
      fetch('/health')
        .then(response => response.json())
        .then(data => {
          const isHealthy = data.status === 'healthy';
          healthStatus.innerHTML = isHealthy 
            ? '✅ System operational & ready' 
            : '⚠️ System issues detected';
          healthStatus.style.color = isHealthy ? '#4CAF50' : '#f44336';
          
          // Add subtle animation
          healthStatus.style.transform = 'scale(1.05)';
          setTimeout(() => {
            healthStatus.style.transform = 'scale(1)';
          }, 200);
        })
        .catch(() => {
          healthStatus.innerHTML = '❌ Unable to check system status';
          healthStatus.style.color = '#f44336';
        });
    }

    // Progress step animation
    function animateProgress() {
      const steps = ['step1', 'step2', 'step3', 'step4'];
      const timings = [500, 1500, 3000, 4000]; // Staggered timings
      
      progressSteps.classList.add('active');
      
      steps.forEach((stepId, index) => {
        setTimeout(() => {
          const step = document.getElementById(stepId);
          step.classList.add('active');
          
          // Complete previous steps
          if (index > 0) {
            document.getElementById(steps[index - 1]).classList.remove('active');
            document.getElementById(steps[index - 1]).classList.add('completed');
          }
        }, timings[index]);
      });
    }

    // Enhanced status display
    function showStatus(message, type) {
      statusDiv.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: center; gap: 10px;">
          <span style="font-size: 20px;">${type === 'success' ? '✅' : '❌'}</span>
          <span>${message}</span>
        </div>
      `;
      statusDiv.className = `status ${type}`;
      statusDiv.style.display = 'block';
      
      // Auto-hide after 6 seconds
      setTimeout(() => {
        statusDiv.style.opacity = '0';
        setTimeout(() => {
          statusDiv.style.display = 'none';
          statusDiv.style.opacity = '1';
        }, 300);
      }, 6000);
    }

    // Enhanced form submission
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      
      // Visual feedback
      spinner.style.display = 'flex';
      submitBtn.disabled = true;
      submitBtn.classList.add('generating');
      submitBtn.innerHTML = '<span>🔄 Generating...</span>';
      
      // Start progress animation
      animateProgress();

      const patientId = document.getElementById('patient_id').value.trim();
      if (!patientId) {
        showStatus("Please enter a valid Patient ID", "error");
        resetForm();
        return;
      }

      try {
        const response = await fetch(`/patient-pdf?patient_id=${encodeURIComponent(patientId)}`);

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(errorText || `Server responded with status ${response.status}`);
        }

        // Complete all progress steps
        setTimeout(() => {
          document.getElementById('step4').classList.add('completed');
          document.getElementById('step4').classList.remove('active');
        }, 4500);

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${patientId}_bill.pdf`;
        
        // Enhanced download experience
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
        
        showStatus(`🎉 Bill for Patient ${patientId} generated successfully!`, "success");
        
        // Reset form after successful download
        setTimeout(() => {
          document.getElementById('patient_id').value = '';
        }, 2000);
        
      } catch (error) {
        console.error('Download error:', error);
        showStatus(`Failed to generate bill: ${error.message}`, "error");
      } finally {
        resetForm();
      }
    });

    function resetForm() {
      spinner.style.display = 'none';
      submitBtn.disabled = false;
      submitBtn.classList.remove('generating');
      submitBtn.innerHTML = '<span>Generate & Download Bill</span>';
      progressSteps.classList.remove('active');
      
      // Reset progress steps
      ['step1', 'step2', 'step3', 'step4'].forEach(stepId => {
        const step = document.getElementById(stepId);
        step.classList.remove('active', 'completed');
      });
    }

    // Initialize
    window.addEventListener('load', function() {
      checkHealthStatus();
      
      // Auto-refresh health status every 30 seconds
      setInterval(checkHealthStatus, 30000);
      
      // Add subtle hover effects to input
      const input = document.getElementById('patient_id');
      input.addEventListener('focus', function() {
        this.parentElement.style.transform = 'translateY(-2px)';
      });
      
      input.addEventListener('blur', function() {
        this.parentElement.style.transform = 'translateY(0)';
      });
    });

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
      // Ctrl/Cmd + Enter to submit
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        form.dispatchEvent(new Event('submit'));
      }
      
      // Escape to clear input
      if (e.key === 'Escape') {
        document.getElementById('patient_id').value = '';
        document.getElementById('patient_id').focus();
      }
    });
  </script>
</body>
</html>
"""

# [Rest of the Python code remains the same - search_rows, extract functions, PDF generation, routes, etc.]

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
    print(f"Starting Enhanced Patient Bill Generator...")
    print(f"Data file path: {FILE_PATH}")
    print(f"File exists: {os.path.exists(FILE_PATH)}")
    print(f"Running on port: {port}")
    print(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)