from flask import Flask, render_template, request, jsonify, send_file
import os
from datetime import datetime, date
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors as rl_colors
import io

app = Flask(__name__)

# User info storage
user_info = {}

# Workouts organized by date and category
workouts_by_date = {}

# MET values
MET_VALUES = {
    "Warm-up": 3,
    "Workout": 6,
    "Cool-down": 2.5
}

def calculate_bmi(height_cm, weight_kg):
    """Calculate BMI"""
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 2)

def calculate_bmr(age, gender, height_cm, weight_kg):
    """Calculate BMR using Mifflin-St Jeor Equation"""
    if gender.upper() == 'M':
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    return round(bmr, 2)

def calculate_calories(met_value, weight_kg, duration_min):
    """Calculate calories burned"""
    return round((met_value * 3.5 * weight_kg / 200) * duration_min, 2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/user-info', methods=['GET'])
def get_user_info():
    """Get user information"""
    return jsonify({"user_info": user_info, "status": "success"})

@app.route('/api/user-info', methods=['POST'])
def save_user_info():
    """Save user information and calculate BMI/BMR"""
    global user_info
    data = request.json

    try:
        name = data.get('name')
        regn_id = data.get('regn_id')
        age = int(data.get('age'))
        gender = data.get('gender')
        height = float(data.get('height'))
        weight = float(data.get('weight'))

        bmi = calculate_bmi(height, weight)
        bmr = calculate_bmr(age, gender, height, weight)

        user_info = {
            "name": name,
            "regn_id": regn_id,
            "age": age,
            "gender": gender,
            "height": height,
            "weight": weight,
            "bmi": bmi,
            "bmr": bmr
        }

        return jsonify({
            "status": "success",
            "message": "User info saved!",
            "user_info": user_info
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/workouts', methods=['GET'])
def get_workouts():
    """Get all workouts"""
    return jsonify({
        "workouts": workouts_by_date,
        "status": "success"
    })

@app.route('/api/workouts', methods=['POST'])
def add_workout():
    """Add workout with calorie calculation"""
    data = request.json

    category = data.get('category')
    exercise = data.get('exercise')
    duration = data.get('duration')

    if category not in MET_VALUES:
        return jsonify({"status": "error", "message": "Invalid category"}), 400

    if not exercise or not duration:
        return jsonify({"status": "error", "message": "Please provide exercise and duration"}), 400

    if not user_info.get('weight'):
        return jsonify({"status": "error", "message": "Please save user info first to track calories"}), 400

    try:
        duration = int(duration)
        today = date.today().isoformat()

        # Calculate calories
        calories = calculate_calories(MET_VALUES[category], user_info['weight'], duration)

        workout_entry = {
            "category": category,
            "exercise": exercise,
            "duration": duration,
            "calories": calories,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if today not in workouts_by_date:
            workouts_by_date[today] = []

        workouts_by_date[today].append(workout_entry)

        return jsonify({
            "status": "success",
            "message": f"✅ '{exercise}' added! Burned {calories} calories!",
            "workout": workout_entry
        })
    except ValueError:
        return jsonify({"status": "error", "message": "Duration must be a number"}), 400

@app.route('/api/workout-stats', methods=['GET'])
def get_workout_stats():
    """Get workout statistics for charts"""
    category_totals = {"Warm-up": 0, "Workout": 0, "Cool-down": 0}

    for day_workouts in workouts_by_date.values():
        for workout in day_workouts:
            category_totals[workout['category']] += workout['duration']

    stats = {
        "categories": list(category_totals.keys()),
        "durations": list(category_totals.values()),
        "total_time": sum(category_totals.values())
    }
    return jsonify(stats)

@app.route('/api/export-pdf', methods=['GET'])
def export_pdf():
    """Export weekly fitness report as PDF"""
    if not user_info:
        return jsonify({"status": "error", "message": "Please save user info first"}), 400

    # Create PDF in memory
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Title
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(50, height - 50, "ACEest Fitness & Gym - Weekly Report")

    # User Info
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, height - 100, "User Information")
    pdf.setFont("Helvetica", 12)
    y = height - 120
    pdf.drawString(50, y, f"Name: {user_info['name']}")
    pdf.drawString(50, y - 20, f"Registration ID: {user_info['regn_id']}")
    pdf.drawString(50, y - 40, f"Age: {user_info['age']} | Gender: {user_info['gender']}")
    pdf.drawString(50, y - 60, f"Height: {user_info['height']} cm | Weight: {user_info['weight']} kg")
    pdf.drawString(50, y - 80, f"BMI: {user_info['bmi']} | BMR: {user_info['bmr']} cal/day")

    # Workouts Table
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y - 120, "Workout Log")

    y_pos = y - 150
    pdf.setFont("Helvetica", 10)

    for workout_date, workouts in workouts_by_date.items():
        pdf.drawString(50, y_pos, f"Date: {workout_date}")
        y_pos -= 20

        for workout in workouts:
            pdf.drawString(70, y_pos,
                           f"• {workout['category']}: {workout['exercise']} - {workout['duration']} min - {workout['calories']} cal")
            y_pos -= 15

            if y_pos < 100:  # New page if running out of space
                pdf.showPage()
                y_pos = height - 50

        y_pos -= 10

    pdf.save()
    buffer.seek(0)

    filename = f"{user_info['name'].replace(' ', '_')}_weekly_report.pdf"

    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
