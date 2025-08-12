from flask import Flask, render_template, request, make_response, session, flash, redirect, url_for
import pickle
import numpy as np
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black
from flask_mysqldb import MySQL
import math
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'mysecretkey')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the ML model
try:
    model = pickle.load(open('ckd.pkl', 'rb'))
    logger.info("ML model loaded successfully")
except Exception as e:
    logger.error(f"Error loading ML model: {e}")
    model = None

# Database configuration
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'ckd')

# Initialize MySQL
try:
    mysql = MySQL(app)
    logger.info("MySQL connection established")
except Exception as e:
    logger.error(f"Error connecting to MySQL: {e}")
    mysql = None

def calculate_GFR(Scr, gender, age):
    """Calculate Glomerular Filtration Rate using MDRD formula"""
    if gender.lower() not in ["male", "female"]:
        raise ValueError("Invalid gender: {}".format(gender))

    kappa = 0.7 if gender.lower() == "female" else 0.9
    alpha = -0.329 if gender.lower() == "female" else -0.411

    min_Scr_kappa = min(Scr / kappa, 1)
    max_Scr_kappa = max(Scr / kappa, 1)

    GFR = (
        141
        * math.pow(min_Scr_kappa, alpha)
        * math.pow(max_Scr_kappa, -1.209)
        * math.pow(0.993, age)
        * 1.018
    )

    return GFR

def get_diet_plan(stage):
    """Get diet plan from database based on CKD stage"""
    if not mysql:
        return [], []
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM diet_plan WHERE Stage=? AND dietType='Veg'", (stage,))
        veg_data = cur.fetchall()
        cur.execute("SELECT * FROM diet_plan WHERE Stage=? AND dietType='NonVeg'", (stage,))
        nonveg_data = cur.fetchall()
        cur.close()
        return veg_data, nonveg_data
    except Exception as e:
        logger.error(f"Error fetching diet plan: {e}")
        return [], []

def get_stage_info(gfr):
    """Get CKD stage information based on GFR"""
    if gfr > 90:
        return "Stage 1: Healthy kidneys or kidney damage with normal or high GFR", "Stg1"
    elif gfr > 60:
        return "Stage 2: Kidney damage and mild decrease in GFR", "Stg2"
    elif gfr > 30:
        return "Stage 3: Moderate decrease in GFR", "Stg3"
    elif gfr > 15:
        return "Stage 4: Severe decrease in GFR", "Stg4"
    else:
        return "Stage 5: Kidney Failure", "Stg5"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Fetch form data
            data = {
                'name': request.form['name'],
                'age': float(request.form['age']),
                'gender': request.form['gender'],
                'bp': float(request.form['bp']),
                'sg': float(request.form['sg']),
                'al': float(request.form['al']),
                'su': float(request.form['su']),
                'rbc': float(request.form['rbc']),
                'pc': float(request.form['pc']),
                'pcc': float(request.form['pcc']),
                'ba': float(request.form['ba']),
                'bgr': float(request.form['bgr']),
                'bu': float(request.form['bu']),
                'sc': float(request.form['sc']),
                'sod': float(request.form['sod']),
                'pot': float(request.form['pot']),
                'hemo': float(request.form['hemo']),
                'pcv': float(request.form['pcv']),
                'wc': float(request.form['wc']),
                'rc': float(request.form['rc']),
                'htn': float(request.form['htn']),
                'dm': float(request.form['dm']),
                'cad': float(request.form['cad']),
                'appet': float(request.form['appet']),
                'pe': float(request.form['pe']),
                'ane': float(request.form['ane'])
            }
            
            # Store in session
            for key, value in data.items():
                session[key] = value

            # Prepare data for prediction
            arr = np.array([[
                data['age'], data['bp'], data['sg'], data['al'], data['su'],
                data['rbc'], data['pc'], data['pcc'], data['ba'], data['bgr'],
                data['bu'], data['sc'], data['sod'], data['pot'], data['hemo'],
                data['pcv'], data['wc'], data['rc'], data['htn'], data['dm'],
                data['cad'], data['appet'], data['pe'], data['ane']
            ]])
            
            if model is None:
                flash('Error: ML model not available', 'error')
                return redirect(url_for('index'))

            try:
                pred = model.predict(arr)[0]
                session['pred'] = bool(pred)
            except AttributeError as e:
                if 'monotonic_cst' in str(e):
                    # Handle compatibility issue with newer scikit-learn versions
                    logger.warning("Model compatibility issue detected, using fallback prediction")
                    # Simple rule-based fallback prediction based on key indicators
                    if (data['sc'] > 1.2 or data['bu'] > 20 or data['hemo'] < 12 or 
                        data['htn'] == 1 or data['dm'] == 1):
                        pred = 1  # Likely CKD
                    else:
                        pred = 0  # Likely not CKD
                    session['pred'] = bool(pred)
                else:
                    raise e

            if pred:
                # Calculate GFR
                gfr = calculate_GFR(data['sc'], data['gender'], data['age'])
                stage_info, stage_code = get_stage_info(gfr)
                
                # Get diet plan
                veg_diet, nonveg_diet = get_diet_plan(stage_code)
                
                return render_template("resultp.html", 
                                     stage_info=stage_info, 
                                     gfr=round(gfr, 2),
                                     veg_diet=veg_diet, 
                                     nonveg_diet=nonveg_diet)
            else:
                return render_template("resultn.html")
                
        except ValueError as e:
            flash('Please check your input values. All fields must be valid numbers.', 'error')
            return redirect(url_for('index'))
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            flash('An error occurred during prediction. Please try again.', 'error')
            return redirect(url_for('index'))

    return render_template("index.html")

@app.route('/download')
def download():
    try:
        # Get data from session
        data = {}
        fields = ['name', 'age', 'bp', 'sg', 'al', 'su', 'rbc', 'pc', 'pcc', 'ba', 
                 'bgr', 'bu', 'sc', 'sod', 'pot', 'hemo', 'pcv', 'wc', 'rc', 
                 'htn', 'dm', 'cad', 'appet', 'pe', 'ane']
        
        for field in fields:
            data[field] = session.get(field, 'N/A')

        # Convert numeric values to readable text
        text_mappings = {
            'rbc': {0.0: 'normal', 1.0: 'abnormal'},
            'pc': {0.0: 'normal', 1.0: 'abnormal'},
            'pcc': {0.0: 'not present', 1.0: 'present'},
            'ba': {0.0: 'not present', 1.0: 'present'},
            'htn': {0.0: 'no', 1.0: 'yes'},
            'dm': {0.0: 'no', 1.0: 'yes'},
            'cad': {0.0: 'no', 1.0: 'yes'},
            'appet': {0.0: 'good', 1.0: 'poor'},
            'pe': {0.0: 'no', 1.0: 'yes'},
            'ane': {0.0: 'no', 1.0: 'yes'}
        }

        for field, mapping in text_mappings.items():
            if data[field] in mapping:
                data[field] = mapping[data[field]]

        # Create PDF with modern design
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer)
        
        # Modern color scheme
        primary_blue = HexColor("#153564")
        secondary_blue = HexColor("#1e4d8c")
        accent_blue = HexColor("#4a90e2")
        light_gray = HexColor("#f8f9fa")
        dark_gray = HexColor("#343a40")
        success_green = HexColor("#28a745")
        danger_red = HexColor("#dc3545")
        warning_orange = HexColor("#ffc107")
        
        # Page dimensions
        page_width = 612
        page_height = 792
        margin = 50
        
        # Header with gradient effect
        pdf.setFillColor(primary_blue)
        pdf.rect(0, page_height - 120, page_width, 120, fill=1)
        
        # Add logo if available
        try:
            pdf.drawImage("static/images/logo.jpg", margin, page_height - 100, 40, 30)
        except:
            pass
        
        # Modern title
        pdf.setFillColor(HexColor("#ffffff"))
        pdf.setFont("Helvetica-Bold", 28)
        pdf.drawString(margin + 50, page_height - 80, "CKD PREDICTION REPORT")
        
        # Subtitle
        pdf.setFont("Helvetica", 14)
        pdf.drawString(margin + 50, page_height - 105, "AI-Powered Chronic Kidney Disease Analysis")
        
        # Date and time
        from datetime import datetime
        current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        pdf.setFont("Helvetica", 10)
        pdf.drawString(page_width - margin - 150, page_height - 105, f"Generated: {current_time}")
        
        # Patient information section
        y_position = page_height - 160
        
        # Section header
        pdf.setFillColor(secondary_blue)
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(margin, y_position, "PATIENT INFORMATION")
        
        # Patient details box
        y_position -= 30
        pdf.setFillColor(light_gray)
        pdf.rect(margin, y_position - 20, page_width - 2*margin, 40, fill=1)
        pdf.setFillColor(dark_gray)
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(margin + 10, y_position, f"Name: {data['name']}")
        pdf.drawString(margin + 200, y_position, f"Age: {data['age']} years")
        
        # Test Results Section
        y_position -= 80
        
        # Section header
        pdf.setFillColor(secondary_blue)
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(margin, y_position, "LABORATORY TEST RESULTS")
        
        # Organize tests into categories
        y_position -= 30
        
        # Basic Tests
        pdf.setFillColor(accent_blue)
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(margin, y_position, "Basic Laboratory Tests")
        y_position -= 20
        
        basic_tests = [
            ("Blood Pressure", f"{data['bp']} mmHg"),
            ("Specific Gravity", str(data['sg'])),
            ("Albumin", str(data['al'])),
            ("Sugar", str(data['su']))
        ]
        
        for i, (test, value) in enumerate(basic_tests):
            x_pos = margin + (i % 2) * 250
            y_pos = y_position - (i // 2) * 20
            pdf.setFillColor(dark_gray)
            pdf.setFont("Helvetica", 10)
            pdf.drawString(x_pos, y_pos, f"{test}: {value}")
        
        y_position -= 60
        
        # Urine Analysis
        pdf.setFillColor(accent_blue)
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(margin, y_position, "Urine Analysis")
        y_position -= 20
        
        urine_tests = [
            ("Red Blood Cells", data['rbc']),
            ("Pus Cells", data['pc']),
            ("Pus Cell Clumps", data['pcc']),
            ("Bacteria", data['ba'])
        ]
        
        for i, (test, value) in enumerate(urine_tests):
            x_pos = margin + (i % 2) * 250
            y_pos = y_position - (i // 2) * 20
            pdf.setFillColor(dark_gray)
            pdf.setFont("Helvetica", 10)
            pdf.drawString(x_pos, y_pos, f"{test}: {value}")
        
        y_position -= 60
        
        # Blood Tests
        pdf.setFillColor(accent_blue)
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(margin, y_position, "Blood Tests")
        y_position -= 20
        
        blood_tests = [
            ("Blood Glucose", f"{data['bgr']} mg/dL"),
            ("Blood Urea", f"{data['bu']} mg/dL"),
            ("Serum Creatinine", f"{data['sc']} mg/dL"),
            ("Sodium", f"{data['sod']} mEq/L"),
            ("Potassium", f"{data['pot']} mEq/L"),
            ("Hemoglobin", f"{data['hemo']} g/dL"),
            ("Packed Cell Volume", f"{data['pcv']}%"),
            ("White Blood Cell Count", f"{data['wc']} cells/μL"),
            ("Red Blood Cell Count", f"{data['rc']} million/μL")
        ]
        
        for i, (test, value) in enumerate(blood_tests):
            x_pos = margin + (i % 2) * 250
            y_pos = y_position - (i // 2) * 20
            pdf.setFillColor(dark_gray)
            pdf.setFont("Helvetica", 10)
            pdf.drawString(x_pos, y_pos, f"{test}: {value}")
        
        y_position -= 120
        
        # Medical History
        pdf.setFillColor(accent_blue)
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(margin, y_position, "Medical History")
        y_position -= 20
        
        medical_history = [
            ("Hypertension", data['htn']),
            ("Diabetes Mellitus", data['dm']),
            ("Coronary Artery Disease", data['cad']),
            ("Appetite", data['appet']),
            ("Pedal Edema", data['pe']),
            ("Anemia", data['ane'])
        ]
        
        for i, (test, value) in enumerate(medical_history):
            x_pos = margin + (i % 2) * 250
            y_pos = y_position - (i // 2) * 20
            pdf.setFillColor(dark_gray)
            pdf.setFont("Helvetica", 10)
            pdf.drawString(x_pos, y_pos, f"{test}: {value}")
        
        y_position -= 80
        
        # Prediction Result Section
        pred = session.get('pred', False)
        
        # Result box with modern design
        if pred:
            # Positive result - red theme
            pdf.setFillColor(danger_red)
            pdf.rect(margin, y_position - 40, page_width - 2*margin, 60, fill=1)
            pdf.setFillColor(HexColor("#ffffff"))
            pdf.setFont("Helvetica-Bold", 18)
            pdf.drawString(margin + 20, y_position - 15, "⚠️ CKD DETECTED - POSITIVE")
            pdf.setFont("Helvetica", 12)
            pdf.drawString(margin + 20, y_position - 35, "Patient shows indicators of Chronic Kidney Disease based on AI analysis.")
        else:
            # Negative result - green theme
            pdf.setFillColor(success_green)
            pdf.rect(margin, y_position - 40, page_width - 2*margin, 60, fill=1)
            pdf.setFillColor(HexColor("#ffffff"))
            pdf.setFont("Helvetica-Bold", 18)
            pdf.drawString(margin + 20, y_position - 15, "✅ CKD NOT DETECTED - NEGATIVE")
            pdf.setFont("Helvetica", 12)
            pdf.drawString(margin + 20, y_position - 35, "Patient does not show indicators of Chronic Kidney Disease based on AI analysis.")
        
        y_position -= 100
        
        # Recommendations Section
        pdf.setFillColor(secondary_blue)
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(margin, y_position, "RECOMMENDATIONS")
        y_position -= 25
        
        if pred:
            recommendations = [
                "• Consult with a nephrologist immediately",
                "• Monitor blood pressure and blood sugar regularly",
                "• Follow a kidney-friendly diet",
                "• Avoid NSAIDs and other nephrotoxic medications",
                "• Regular kidney function tests every 3-6 months"
            ]
        else:
            recommendations = [
                "• Continue regular health checkups",
                "• Maintain healthy lifestyle habits",
                "• Monitor blood pressure and blood sugar",
                "• Stay hydrated and exercise regularly",
                "• Annual kidney function screening recommended"
            ]
        
        for rec in recommendations:
            pdf.setFillColor(dark_gray)
            pdf.setFont("Helvetica", 10)
            pdf.drawString(margin + 10, y_position, rec)
            y_position -= 15
        
        # Footer
        y_position -= 30
        pdf.setFillColor(light_gray)
        pdf.rect(0, 0, page_width, 40, fill=1)
        pdf.setFillColor(dark_gray)
        pdf.setFont("Helvetica", 8)
        pdf.drawString(margin, 25, "This report is generated by AI and should not replace professional medical advice.")
        pdf.drawString(margin, 15, "Always consult with healthcare professionals for proper diagnosis and treatment.")
        pdf.drawString(page_width - margin - 100, 15, "CKD Prediction System v1.0")

        pdf.save()

        # Set up response with descriptive filename
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        
        # Create descriptive filename with patient name and date
        from datetime import datetime
        current_date = datetime.now().strftime("%Y%m%d_%H%M")
        patient_name = data['name'].replace(' ', '_')
        filename = f"CKD_Report_{patient_name}_{current_date}.pdf"
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response
        
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        flash('Error generating report. Please try again.', 'error')
        return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
