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

# Enhanced HTML template with cutting-edge UI and premium animations
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Patient Bill Generator - MYNX SOFTWARES</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
  <style>
    :root {
      --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
      --secondary-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
      --accent-gradient: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
      --success-gradient: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
      --error-gradient: linear-gradient(135deg, #fc466b 0%, #3f5efb 100%);
      --warning-gradient: linear-gradient(135deg, #FDBB2D 0%, #22C1C3 100%);
      
      --glass-primary: rgba(255, 255, 255, 0.15);
      --glass-secondary: rgba(255, 255, 255, 0.08);
      --glass-border: rgba(255, 255, 255, 0.2);
      --glass-backdrop: rgba(16, 16, 24, 0.4);
      
      --text-primary: #ffffff;
      --text-secondary: rgba(255, 255, 255, 0.9);
      --text-muted: rgba(255, 255, 255, 0.7);
      --text-faded: rgba(255, 255, 255, 0.5);
      
      --shadow-xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
      --shadow-2xl: 0 35px 70px -15px rgba(0, 0, 0, 0.3);
      --shadow-glow: 0 0 40px rgba(255, 255, 255, 0.1);
      --shadow-colored: 0 20px 60px rgba(102, 126, 234, 0.4);
      
      --border-radius-sm: 12px;
      --border-radius-md: 20px;
      --border-radius-lg: 30px;
      --border-radius-xl: 40px;
      
      --transition-fast: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
      --transition-smooth: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
      --transition-bounce: all 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    html {
      scroll-behavior: smooth;
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
      background-attachment: fixed;
      background-size: 400% 400%;
      animation: gradientShift 15s ease infinite;
    }

    @keyframes gradientShift {
      0%, 100% { background-position: 0% 50%; }
      50% { background-position: 100% 50%; }
    }

    /* Sophisticated animated background */
    body::before {
      content: '';
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-image: 
        radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
        radial-gradient(circle at 40% 40%, rgba(120, 255, 198, 0.3) 0%, transparent 50%);
      animation: backgroundPulse 20s ease-in-out infinite;
      pointer-events: none;
      z-index: 0;
    }

    @keyframes backgroundPulse {
      0%, 100% { opacity: 0.3; transform: scale(1) rotate(0deg); }
      33% { opacity: 0.7; transform: scale(1.1) rotate(120deg); }
      66% { opacity: 0.4; transform: scale(0.9) rotate(240deg); }
    }

    .cosmic-particles {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 1;
      overflow: hidden;
    }

    .particle {
      position: absolute;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.8);
      animation: float 20s linear infinite;
      opacity: 0;
    }

    .particle:nth-child(odd) {
      background: rgba(102, 126, 234, 0.6);
      animation-duration: 25s;
    }

    .particle:nth-child(3n) {
      background: rgba(240, 147, 251, 0.6);
      animation-duration: 30s;
    }

    @keyframes float {
      0% {
        opacity: 0;
        transform: translateY(100vh) scale(0) rotate(0deg);
      }
      10% {
        opacity: 1;
        transform: translateY(90vh) scale(1) rotate(36deg);
      }
      90% {
        opacity: 1;
        transform: translateY(-10vh) scale(1) rotate(324deg);
      }
      100% {
        opacity: 0;
        transform: translateY(-20vh) scale(0) rotate(360deg);
      }
    }

    .container {
      background: var(--glass-primary);
      backdrop-filter: blur(40px);
      -webkit-backdrop-filter: blur(40px);
      border: 2px solid var(--glass-border);
      padding: 50px 45px;
      border-radius: var(--border-radius-xl);
      box-shadow: var(--shadow-2xl), var(--shadow-glow);
      width: 100%;
      max-width: 520px;
      z-index: 10;
      position: relative;
      transition: var(--transition-smooth);
      animation: containerEntrance 1.2s cubic-bezier(0.4, 0, 0.2, 1) forwards;
      transform: translateY(50px) scale(0.9);
      opacity: 0;
    }

    @keyframes containerEntrance {
      0% {
        opacity: 0;
        transform: translateY(50px) scale(0.9) rotateX(10deg);
        filter: blur(10px);
      }
      50% {
        opacity: 0.8;
        transform: translateY(-5px) scale(1.02) rotateX(-2deg);
        filter: blur(2px);
      }
      100% {
        opacity: 1;
        transform: translateY(0) scale(1) rotateX(0deg);
        filter: blur(0px);
      }
    }

    .container:hover {
      transform: translateY(-8px) scale(1.02);
      box-shadow: var(--shadow-2xl), var(--shadow-colored);
      border-color: rgba(255, 255, 255, 0.4);
    }

    .header {
      text-align: center;
      margin-bottom: 40px;
      position: relative;
    }

    .header::before {
      content: '';
      position: absolute;
      top: -20px;
      left: 50%;
      transform: translateX(-50%);
      width: 60px;
      height: 4px;
      background: var(--secondary-gradient);
      border-radius: 20px;
      animation: headerAccent 2s ease-in-out infinite alternate;
    }

    @keyframes headerAccent {
      0% { width: 60px; opacity: 0.6; }
      100% { width: 100px; opacity: 1; }
    }

    .header h1 {
      color: var(--text-primary);
      font-size: 36px;
      font-weight: 900;
      margin-bottom: 12px;
      background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 50%, #e0e7ff 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      text-shadow: none;
      animation: titleShine 3s ease-in-out infinite;
      letter-spacing: -0.5px;
      line-height: 1.2;
    }

    @keyframes titleShine {
      0%, 100% {
        background-position: 0% 50%;
        filter: brightness(1);
      }
      50% {
        background-position: 100% 50%;
        filter: brightness(1.2);
      }
    }

    .subtitle {
      color: var(--text-muted);
      font-size: 16px;
      font-weight: 500;
      opacity: 0;
      animation: subtitleSlide 1s ease-out 0.5s forwards;
      margin-bottom: 8px;
    }

    @keyframes subtitleSlide {
      0% {
        opacity: 0;
        transform: translateY(20px);
      }
      100% {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .company-tag {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: var(--glass-secondary);
      border: 1px solid var(--glass-border);
      border-radius: 20px;
      padding: 6px 16px;
      font-size: 12px;
      font-weight: 600;
      color: var(--text-secondary);
      margin-top: 8px;
      backdrop-filter: blur(10px);
      animation: tagGlow 2s ease-in-out infinite alternate;
    }

    @keyframes tagGlow {
      0% { box-shadow: 0 0 10px rgba(255, 255, 255, 0.1); }
      100% { box-shadow: 0 0 20px rgba(255, 255, 255, 0.3); }
    }

    .status-indicator {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      margin-bottom: 35px;
      padding: 16px 20px;
      border-radius: var(--border-radius-md);
      background: var(--glass-secondary);
      border: 1px solid var(--glass-border);
      backdrop-filter: blur(20px);
      transition: var(--transition-smooth);
      animation: statusPulse 2s ease-in-out infinite;
    }

    @keyframes statusPulse {
      0%, 100% { transform: scale(1); }
      50% { transform: scale(1.02); }
    }

    .status-dot {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      background: var(--success-gradient);
      box-shadow: 0 0 20px rgba(67, 233, 123, 0.6);
      animation: dotPulse 1.5s ease-in-out infinite;
    }

    @keyframes dotPulse {
      0%, 100% { transform: scale(1); opacity: 1; }
      50% { transform: scale(1.2); opacity: 0.8; }
    }

    .status-text {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-secondary);
    }

    .form-section {
      margin-bottom: 35px;
    }

    .input-group {
      position: relative;
      opacity: 0;
      animation: inputSlideIn 0.8s ease-out 0.8s forwards;
    }

    @keyframes inputSlideIn {
      0% {
        opacity: 0;
        transform: translateX(-30px);
      }
      100% {
        opacity: 1;
        transform: translateX(0);
      }
    }

    .input-label {
      display: block;
      margin-bottom: 12px;
      color: var(--text-primary);
      font-weight: 600;
      font-size: 15px;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      font-size: 12px;
    }

    .input-wrapper {
      position: relative;
      margin-bottom: 8px;
    }

    .input-field {
      width: 100%;
      padding: 20px 55px 20px 20px;
      border: 2px solid var(--glass-border);
      border-radius: var(--border-radius-md);
      font-size: 16px;
      font-weight: 500;
      background: var(--glass-secondary);
      color: var(--text-primary);
      backdrop-filter: blur(20px);
      transition: var(--transition-smooth);
      outline: none;
      letter-spacing: 0.5px;
    }

    .input-field::placeholder {
      color: var(--text-faded);
      font-weight: 400;
    }

    .input-field:focus {
      border-color: rgba(79, 172, 254, 0.8);
      background: var(--glass-primary);
      box-shadow: 
        0 0 30px rgba(79, 172, 254, 0.3),
        0 8px 25px rgba(0, 0, 0, 0.15);
      transform: translateY(-2px);
    }

    .input-field:focus + .input-icon {
      color: #4facfe;
      transform: scale(1.2) translateY(-50%);
      filter: drop-shadow(0 0 8px rgba(79, 172, 254, 0.5));
    }

    .input-icon {
      position: absolute;
      right: 18px;
      top: 50%;
      transform: translateY(-50%);
      font-size: 20px;
      color: var(--text-faded);
      transition: var(--transition-smooth);
      pointer-events: none;
    }

    .input-hint {
      font-size: 12px;
      color: var(--text-faded);
      margin-top: 8px;
      padding-left: 4px;
      font-weight: 500;
    }

    .submit-button {
      width: 100%;
      margin-top: 8px;
      padding: 22px 30px;
      background: var(--accent-gradient);
      border: none;
      color: white;
      font-size: 18px;
      font-weight: 700;
      border-radius: var(--border-radius-md);
      cursor: pointer;
      transition: var(--transition-bounce);
      position: relative;
      overflow: hidden;
      box-shadow: var(--shadow-xl);
      opacity: 0;
      animation: buttonSlideIn 1s ease-out 1.2s forwards;
      text-transform: uppercase;
      letter-spacing: 1px;
    }

    @keyframes buttonSlideIn {
      0% {
        opacity: 0;
        transform: translateY(30px) scale(0.9);
      }
      100% {
        opacity: 1;
        transform: translateY(0) scale(1);
      }
    }

    .submit-button::before {
      content: '';
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 100%;
      background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
      transition: left 0.8s ease;
    }

    .submit-button:hover::before {
      left: 100%;
    }

    .submit-button:hover {
      transform: translateY(-4px) scale(1.02);
      box-shadow: 
        0 20px 40px rgba(250, 112, 154, 0.4),
        0 0 50px rgba(250, 112, 154, 0.2);
      filter: brightness(1.1);
    }

    .submit-button:active {
      transform: translateY(-2px) scale(0.98);
      transition: var(--transition-fast);
    }

    .submit-button:disabled {
      opacity: 0.8;
      cursor: not-allowed;
      transform: none;
      background: var(--warning-gradient);
    }

    .submit-button.loading {
      background: var(--success-gradient);
      animation: buttonPulse 2s ease-in-out infinite;
      pointer-events: none;
    }

    @keyframes buttonPulse {
      0%, 100% { transform: scale(1); }
      50% { transform: scale(1.05); }
    }

    /* Enhanced Premium Loading Overlay */
    .loading-overlay {
      display: none;
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: var(--glass-backdrop);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      z-index: 99999;
      justify-content: center;
      align-items: center;
      animation: overlayFadeIn 0.5s ease-out;
    }

    @keyframes overlayFadeIn {
      0% { opacity: 0; }
      100% { opacity: 1; }
    }

    .loading-container {
      background: var(--glass-primary);
      backdrop-filter: blur(40px);
      border: 2px solid var(--glass-border);
      border-radius: var(--border-radius-lg);
      padding: 50px 40px;
      text-align: center;
      color: white;
      box-shadow: var(--shadow-2xl);
      animation: loadingContainerSlide 0.8s cubic-bezier(0.4, 0, 0.2, 1);
      min-width: 400px;
    }

    @keyframes loadingContainerSlide {
      0% {
        opacity: 0;
        transform: translateY(50px) scale(0.8);
      }
      100% {
        opacity: 1;
        transform: translateY(0) scale(1);
      }
    }

    .loading-spinner {
      position: relative;
      width: 120px;
      height: 120px;
      margin: 0 auto 30px;
    }

    .spinner-ring {
      position: absolute;
      width: 100%;
      height: 100%;
      border-radius: 50%;
      animation: spin 2s linear infinite;
    }

    .spinner-ring:nth-child(1) {
      border: 4px solid transparent;
      border-top: 4px solid #4facfe;
      animation-duration: 2s;
    }

    .spinner-ring:nth-child(2) {
      border: 4px solid transparent;
      border-right: 4px solid #00f2fe;
      animation-duration: 2.5s;
      animation-direction: reverse;
    }

    .spinner-ring:nth-child(3) {
      border: 4px solid transparent;
      border-bottom: 4px solid #fa709a;
      animation-duration: 3s;
      width: 80%;
      height: 80%;
      top: 10%;
      left: 10%;
    }

    .spinner-ring:nth-child(4) {
      border: 4px solid transparent;
      border-left: 4px solid #fee140;
      animation-duration: 3.5s;
      animation-direction: reverse;
      width: 60%;
      height: 60%;
      top: 20%;
      left: 20%;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    .loading-text {
      font-size: 22px;
      font-weight: 700;
      margin-bottom: 12px;
      animation: textGlow 2s ease-in-out infinite alternate;
      background: linear-gradient(135deg, #ffffff 0%, #4facfe 50%, #00f2fe 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    @keyframes textGlow {
      0% { filter: brightness(1); }
      100% { filter: brightness(1.2); }
    }

    .loading-subtitle {
      font-size: 14px;
      color: var(--text-muted);
      margin-bottom: 25px;
      font-weight: 500;
    }

    .progress-tracker {
      display: flex;
      flex-direction: column;
      gap: 15px;
      margin-top: 25px;
    }

    .progress-step {
      display: flex;
      align-items: center;
      gap: 15px;
      padding: 12px 16px;
      border-radius: var(--border-radius-sm);
      background: var(--glass-secondary);
      border: 1px solid var(--glass-border);
      transition: var(--transition-smooth);
      opacity: 0.5;
    }

    .progress-step.active {
      opacity: 1;
      background: var(--glass-primary);
      border-color: rgba(79, 172, 254, 0.5);
      box-shadow: 0 0 20px rgba(79, 172, 254, 0.2);
      animation: stepGlow 1.5s ease-in-out infinite alternate;
    }

    @keyframes stepGlow {
      0% { box-shadow: 0 0 20px rgba(79, 172, 254, 0.2); }
      100% { box-shadow: 0 0 30px rgba(79, 172, 254, 0.4); }
    }

    .progress-step.completed {
      opacity: 1;
      background: var(--success-gradient);
      border-color: rgba(67, 233, 123, 0.5);
      animation: stepComplete 0.6s ease-out;
    }

    @keyframes stepComplete {
      0% { transform: scale(0.95); }
      50% { transform: scale(1.05); }
      100% { transform: scale(1); }
    }

    .step-indicator {
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: var(--glass-border);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      font-weight: 600;
      transition: var(--transition-smooth);
      position: relative;
    }

    .progress-step.active .step-indicator {
      background: var(--secondary-gradient);
      color: white;
      box-shadow: 0 0 15px rgba(79, 172, 254, 0.5);
      animation: indicatorPulse 1s ease-in-out infinite;
    }

    @keyframes indicatorPulse {
      0%, 100% { transform: scale(1); }
      50% { transform: scale(1.1); }
    }

    .progress-step.completed .step-indicator {
      background: #43e97b;
      color: white;
    }

    .progress-step.completed .step-indicator::after {
      content: '✓';
      position: absolute;
      animation: checkmarkPop 0.4s ease-out;
    }

    @keyframes checkmarkPop {
      0% { transform: scale(0); }
      100% { transform: scale(1); }
    }

    .step-text {
      font-size: 14px;
      font-weight: 500;
      color: var(--text-secondary);
    }

    .progress-step.active .step-text {
      color: var(--text-primary);
      font-weight: 600;
    }

    /* Enhanced Status Messages */
    .notification {
      margin-top: 25px;
      padding: 20px 25px;
      border-radius: var(--border-radius-md);
      display: none;
      font-weight: 600;
      text-align: center;
      animation: notificationSlide 0.6s cubic-bezier(0.4, 0, 0.2, 1);
      backdrop-filter: blur(20px);
      border: 2px solid transparent;
      position: relative;
      overflow: hidden;
    }

    @keyframes notificationSlide {
      0% {
        opacity: 0;
        transform: translateY(-30px) scale(0.9);
      }
      100% {
        opacity: 1;
        transform: translateY(0) scale(1);
      }
    }

    .notification::before {
      content: '';
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 100%;
      background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
      animation: notificationShimmer 2s ease-in-out infinite;
    }

    @keyframes notificationShimmer {
      0%, 100% { left: -100%; }
      50% { left: 100%; }
    }

    .notification.success {
      background: rgba(67, 233, 123, 0.15);
      color: #e8fffe;
      border-color: rgba(67, 233, 123, 0.4);
      box-shadow: 
        0 0 30px rgba(67, 233, 123, 0.3),
        0 8px 25px rgba(0, 0, 0, 0.15);
    }

    .notification.error {
      background: rgba(252, 70, 107, 0.15);
      color: #ffe8ee;
      border-color: rgba(252, 70, 107, 0.4);
      box-shadow: 
        0 0 30px rgba(252, 70, 107, 0.3),
        0 8px 25px rgba(0, 0, 0, 0.15);
    }

    .notification-content {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      position: relative;
      z-index: 1;
    }

    .notification-icon {
      font-size: 24px;
      animation: iconBounce 0.6s ease-out;
    }

    @keyframes iconBounce {
      0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
      40% { transform: translateY(-8px); }
      60% { transform: translateY(-4px); }
    }

    .footer {
      text-align: center;
      margin-top: 35px;
      opacity: 0;
      animation: footerFadeIn 1s ease-out 1.5s forwards;
    }

    @keyframes footerFadeIn {
      0% { opacity: 0; transform: translateY(20px); }
      100% { opacity: 1; transform: translateY(0); }
    }

    .footer-content {
      font-size: 13px;
      color: var(--text-faded);
      line-height: 1.6;
    }

    .footer-brand {
      font-weight: 700;
      color: var(--text-secondary);
      margin-bottom: 4px;
    }

    .footer-link {
      color: var(--text-muted);
      text-decoration: none;
      transition: var(--transition-smooth);
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }

    .footer-link:hover {
      color: var(--text-primary);
      text-shadow: 0 0 15px rgba(255, 255, 255, 0.5);
      transform: translateY(-1px);
    }

    /* Responsive Design */
    @media (max-width: 768px) {
      .container {
        padding: 40px 30px;
        margin: 15px;
        max-width: 90vw;
      }
      
      .header h1 {
        font-size: 30px;
      }
      
      .loading-container {
        min-width: 300px;
        padding: 40px 30px;
      }

      .progress-step {
        padding: 10px 12px;
        gap: 12px;
      }

      .step-text {
        font-size: 13px;
      }
    }

    @media (max-width: 480px) {
      body {
        padding: 10px;
      }
      
      .container {
        padding: 30px 20px;
      }
      
      .header h1 {
        font-size: 26px;
      }

      .input-field {
        padding: 18px 50px 18px 18px;
        font-size: 15px;
      }

      .submit-button {
        padding: 20px 25px;
        font-size: 16px;
      }

      .loading-container {
        min-width: 280px;
        padding: 35px 25px;
      }

      .loading-spinner {
        width: 100px;
        height: 100px;
        margin-bottom: 25px;
      }
    }

    /* Advanced Accessibility */
    @media (prefers-reduced-motion: reduce) {
      * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
      }
    }

    @media (prefers-color-scheme: dark) {
      .container {
        background: rgba(0, 0, 0, 0.3);
        border-color: rgba(255, 255, 255, 0.1);
      }
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
      width: 8px;
    }

    ::-webkit-scrollbar-track {
      background: rgba(255, 255, 255, 0.1);
      border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb {
      background: var(--secondary-gradient);
      border-radius: 10px;
      transition: var(--transition-smooth);
    }

    ::-webkit-scrollbar-thumb:hover {
      background: var(--accent-gradient);
    }

    /* Focus styles for accessibility */
    .submit-button:focus-visible,
    .input-field:focus-visible {
      outline: 3px solid rgba(79, 172, 254, 0.6);
      outline-offset: 2px;
    }
  </style>
</head>
<body>
  <!-- Dynamic particle system -->
  <div class="cosmic-particles" id="particleSystem"></div>

  <!-- Premium loading overlay with enhanced progress tracking -->
  <div class="loading-overlay" id="loadingOverlay">
    <div class="loading-container">
      <div class="loading-spinner">
        <div class="spinner-ring"></div>
        <div class="spinner-ring"></div>
        <div class="spinner-ring"></div>
        <div class="spinner-ring"></div>
      </div>
      <div class="loading-text" id="loadingText">Generating Your Bill</div>
      <div class="loading-subtitle">Please wait while we process your request...</div>
      
      <div class="progress-tracker" id="progressTracker">
        <div class="progress-step" id="step1">
          <div class="step-indicator">1</div>
          <div class="step-text">Searching patient records...</div>
        </div>
        <div class="progress-step" id="step2">
          <div class="step-indicator">2</div>
          <div class="step-text">Calculating charges and fees...</div>
        </div>
        <div class="progress-step" id="step3">
          <div class="step-indicator">3</div>
          <div class="step-text">Generating PDF document...</div>
        </div>
        <div class="progress-step" id="step4">
          <div class="step-indicator">4</div>
          <div class="step-text">Preparing secure download...</div>
        </div>
        <div class="progress-step" id="step5">
          <div class="step-indicator">5</div>
          <div class="step-text">Finalizing and optimizing...</div>
        </div>
      </div>
    </div>
  </div>

  <div class="container">
    <div class="header">
      <h1>Patient Bill Generator</h1>
      <div class="subtitle">Advanced billing statement generation system</div>
      <div class="company-tag">
        <span>⚡</span>
        <span>MYNX SOFTWARES INC</span>
      </div>
    </div>

    <div class="status-indicator">
      <div class="status-dot" id="statusDot"></div>
      <div class="status-text" id="statusText">Checking system status...</div>
    </div>

    <form id="billGeneratorForm" class="form-section">
      <div class="input-group">
        <label for="patientId" class="input-label">Patient Identification</label>
        <div class="input-wrapper">
          <input 
            type="text" 
            id="patientId" 
            name="patient_id" 
            class="input-field"
            required 
            placeholder="Enter Patient ID (e.g., P001, 12345, ABC123)"
            autocomplete="off"
            spellcheck="false"
          >
          <div class="input-icon">👤</div>
        </div>
        <div class="input-hint">
          Enter the unique patient identifier to generate billing statement
        </div>
      </div>

      <button type="submit" class="submit-button" id="generateButton">
        <span id="buttonText">Generate & Download Bill</span>
      </button>
    </form>

    <div class="notification" id="notificationArea"></div>

    <div class="footer">
      <div class="footer-content">
        <div class="footer-brand">© 2024 MYNX SOFTWARES INC</div>
        <div>
          Deployed with ❤️ on 
          <a href="#" class="footer-link" target="_blank">
            <span>Render</span>
            <span>↗</span>
          </a>
        </div>
      </div>
    </div>
  </div>

  <script>
    // Enhanced application with advanced animations and interactions
    class BillGeneratorApp {
      constructor() {
        this.form = document.getElementById('billGeneratorForm');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.notificationArea = document.getElementById('notificationArea');
        this.generateButton = document.getElementById('generateButton');
        this.buttonText = document.getElementById('buttonText');
        this.statusDot = document.getElementById('statusDot');
        this.statusText = document.getElementById('statusText');
        this.patientIdInput = document.getElementById('patientId');
        this.loadingText = document.getElementById('loadingText');
        
        this.progressSteps = [
          'step1', 'step2', 'step3', 'step4', 'step5'
        ];
        
        this.isGenerating = false;
        this.particleSystem = null;
        
        this.init();
      }

      init() {
        this.setupEventListeners();
        this.createParticleSystem();
        this.checkSystemHealth();
        this.setupPeriodicHealthCheck();
        this.setupKeyboardShortcuts();
        this.setupAdvancedInteractions();
      }

      setupEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        
        // Enhanced input interactions
        this.patientIdInput.addEventListener('input', (e) => this.handleInputChange(e));
        this.patientIdInput.addEventListener('focus', () => this.handleInputFocus());
        this.patientIdInput.addEventListener('blur', () => this.handleInputBlur());
        
        // Button hover effects
        this.generateButton.addEventListener('mouseenter', () => this.handleButtonHover());
        this.generateButton.addEventListener('mouseleave', () => this.handleButtonLeave());
      }

      createParticleSystem() {
        const particleContainer = document.getElementById('particleSystem');
        const particleCount = 50;
        
        for (let i = 0; i < particleCount; i++) {
          const particle = document.createElement('div');
          particle.className = 'particle';
          
          // Random positioning and sizing
          const size = Math.random() * 4 + 2;
          const startX = Math.random() * 100;
          const delay = Math.random() * 20;
          
          particle.style.cssText = `
            width: ${size}px;
            height: ${size}px;
            left: ${startX}%;
            animation-delay: ${delay}s;
          `;
          
          particleContainer.appendChild(particle);
        }
      }

      async checkSystemHealth() {
        try {
          const response = await fetch('/health');
          const data = await response.json();
          
          const isHealthy = data.status === 'healthy';
          this.updateSystemStatus(isHealthy, data);
          
        } catch (error) {
          console.error('Health check failed:', error);
          this.updateSystemStatus(false, { error: 'Connection failed' });
        }
      }

      updateSystemStatus(isHealthy, data) {
        const statusMessages = {
          healthy: '✨ System operational & ready',
          degraded: '⚠️ System issues detected',
          unhealthy: '🔴 System maintenance required',
          error: '❌ Unable to connect to server'
        };

        const status = data.error ? 'error' : data.status;
        const message = statusMessages[status] || statusMessages.error;
        
        this.statusText.textContent = message;
        
        // Update status dot color
        const colors = {
          healthy: 'var(--success-gradient)',
          degraded: 'var(--warning-gradient)',
          unhealthy: 'var(--error-gradient)',
          error: 'var(--error-gradient)'
        };
        
        this.statusDot.style.background = colors[status];
        
        // Animate status change
        this.statusDot.style.transform = 'scale(1.3)';
        setTimeout(() => {
          this.statusDot.style.transform = 'scale(1)';
        }, 300);
      }

      setupPeriodicHealthCheck() {
        // Check health every 30 seconds
        setInterval(() => this.checkSystemHealth(), 30000);
      }

      setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
          // Ctrl/Cmd + Enter to submit
          if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && !this.isGenerating) {
            e.preventDefault();
            this.form.dispatchEvent(new Event('submit'));
          }
          
          // Escape to clear and focus input
          if (e.key === 'Escape' && !this.isGenerating) {
            this.patientIdInput.value = '';
            this.patientIdInput.focus();
            this.hideNotification();
          }
          
          // F5 to refresh health status
          if (e.key === 'F5') {
            e.preventDefault();
            this.checkSystemHealth();
          }
        });
      }

      setupAdvancedInteractions() {
        // Advanced form validation with real-time feedback
        this.patientIdInput.addEventListener('keyup', (e) => {
          const value = e.target.value.trim();
          if (value.length > 0) {
            this.validatePatientId(value);
          }
        });
      }

      validatePatientId(patientId) {
        const isValid = /^[A-Za-z0-9_-]{1,20}$/.test(patientId);
        
        if (!isValid && patientId.length > 0) {
          this.patientIdInput.style.borderColor = 'rgba(252, 70, 107, 0.6)';
          this.patientIdInput.style.boxShadow = '0 0 20px rgba(252, 70, 107, 0.3)';
        } else {
          this.patientIdInput.style.borderColor = '';
          this.patientIdInput.style.boxShadow = '';
        }
      }

      handleInputChange(e) {
        const value = e.target.value;
        if (value.length > 0) {
          this.hideNotification();
        }
      }

      handleInputFocus() {
        this.patientIdInput.parentElement.style.transform = 'translateY(-3px) scale(1.01)';
      }

      handleInputBlur() {
        this.patientIdInput.parentElement.style.transform = 'translateY(0) scale(1)';
      }

      handleButtonHover() {
        if (!this.isGenerating) {
          this.generateButton.style.transform = 'translateY(-2px) scale(1.02)';
        }
      }

      handleButtonLeave() {
        if (!this.isGenerating) {
          this.generateButton.style.transform = 'translateY(0) scale(1)';
        }
      }

      async handleFormSubmit(e) {
        e.preventDefault();
        
        if (this.isGenerating) return;
        
        const patientId = this.patientIdInput.value.trim();
        
        if (!patientId) {
          this.showNotification('Please enter a valid Patient ID', 'error');
          this.patientIdInput.focus();
          return;
        }

        if (!/^[A-Za-z0-9_-]{1,20}$/.test(patientId)) {
          this.showNotification('Patient ID contains invalid characters', 'error');
          this.patientIdInput.focus();
          return;
        }

        await this.generateBill(patientId);
      }

      async generateBill(patientId) {
        this.isGenerating = true;
        this.showLoadingOverlay();
        this.updateButtonState('loading');
        
        try {
          this.animateProgressSteps();
          
          const response = await fetch(`/patient-pdf?patient_id=${encodeURIComponent(patientId)}`);

          if (!response.ok) {
            const errorText = await response.text();
            throw new Error(errorText || `Server error: ${response.status}`);
          }

          // Simulate additional processing time for better UX
          await new Promise(resolve => setTimeout(resolve, 1000));

          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          
          link.href = url;
          link.download = `${patientId}_bill.pdf`;
          link.style.display = 'none';
          
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          
          window.URL.revokeObjectURL(url);
          
          this.showNotification(`🎉 Bill for Patient ${patientId} generated successfully!`, 'success');
          
          // Clear form after successful generation
          setTimeout(() => {
            this.patientIdInput.value = '';
          }, 2000);
          
        } catch (error) {
          console.error('Generation error:', error);
          this.showNotification(`Failed to generate bill: ${error.message}`, 'error');
        } finally {
          this.hideLoadingOverlay();
          this.updateButtonState('normal');
          this.isGenerating = false;
        }
      }

      showLoadingOverlay() {
        this.loadingOverlay.style.display = 'flex';
        document.body.style.overflow = 'hidden';
      }

      hideLoadingOverlay() {
        this.loadingOverlay.style.display = 'none';
        document.body.style.overflow = '';
        this.resetProgressSteps();
      }

      updateButtonState(state) {
        const states = {
          normal: {
            text: 'Generate & Download Bill',
            className: '',
            disabled: false
          },
          loading: {
            text: '🔄 Generating...',
            className: 'loading',
            disabled: true
          }
        };
        
        const config = states[state];
        this.buttonText.textContent = config.text;
        this.generateButton.className = `submit-button ${config.className}`;
        this.generateButton.disabled = config.disabled;
      }

      animateProgressSteps() {
        const stepTimings = [300, 1200, 2500, 4000, 5200];
        const loadingTexts = [
          'Searching patient records...',
          'Processing medical data...',
          'Calculating charges...',
          'Generating PDF document...',
          'Finalizing download...'
        ];
        
        this.progressSteps.forEach((stepId, index) => {
          setTimeout(() => {
            // Complete previous step
            if (index > 0) {
              const prevStep = document.getElementById(this.progressSteps[index - 1]);
              prevStep.classList.remove('active');
              prevStep.classList.add('completed');
            }
            
            // Activate current step
            const currentStep = document.getElementById(stepId);
            currentStep.classList.add('active');
            
            // Update loading text
            this.loadingText.textContent = loadingTexts[index] || 'Processing...';
            
            // Complete final step
            if (index === this.progressSteps.length - 1) {
              setTimeout(() => {
                currentStep.classList.remove('active');
                currentStep.classList.add('completed');
                this.loadingText.textContent = 'Download ready!';
              }, 800);
            }
          }, stepTimings[index]);
        });
      }

      resetProgressSteps() {
        this.progressSteps.forEach(stepId => {
          const step = document.getElementById(stepId);
          step.classList.remove('active', 'completed');
        });
        this.loadingText.textContent = 'Generating Your Bill';
      }

      showNotification(message, type) {
        const icons = {
          success: '✅',
          error: '❌',
          warning: '⚠️',
          info: 'ℹ️'
        };
        
        const icon = icons[type] || icons.info;
        
        this.notificationArea.innerHTML = `
          <div class="notification-content">
            <div class="notification-icon">${icon}</div>
            <div>${message}</div>
          </div>
        `;
        
        this.notificationArea.className = `notification ${type}`;
        this.notificationArea.style.display = 'block';
        
        // Auto-hide after 8 seconds
        setTimeout(() => this.hideNotification(), 8000);
      }

      hideNotification() {
        this.notificationArea.style.opacity = '0';
        setTimeout(() => {
          this.notificationArea.style.display = 'none';
          this.notificationArea.style.opacity = '1';
        }, 300);
      }
    }

    // Initialize the application when DOM is loaded
    document.addEventListener('DOMContentLoaded', () => {
      new BillGeneratorApp();
    });

    // Service Worker Registration for offline capabilities (optional)
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
          .then(registration => console.log('SW registered'))
          .catch(error => console.log('SW registration failed'));
      });
    }

    // Performance monitoring
    window.addEventListener('load', () => {
      const loadTime = performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart;
      console.log(`App loaded in ${loadTime}ms`);
    });
  </script>
</body>
</html>
"""

# [Rest of the Python backend code remains exactly the same]

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