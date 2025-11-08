from flask import Flask, render_template, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)

# In-memory storage with categories
workouts = {
    "Warm-up": [],
    "Workout": [],
    "Cool-down": []
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/workouts', methods=['GET'])
def get_workouts():
    """Get all categorized workouts"""
    total_time = sum(sum(w['duration'] for w in cat) for cat in workouts.values())
    return jsonify({
        "workouts": workouts,
        "total_time": total_time,
        "status": "success"
    })

@app.route('/api/workouts', methods=['POST'])
def add_workout():
    """Add a new workout to a category"""
    data = request.json

    category = data.get('category')
    exercise = data.get('exercise')
    duration = data.get('duration')

    if category not in workouts:
        return jsonify({"status": "error", "message": "Invalid category"}), 400

    if not exercise or not duration:
        return jsonify({"status": "error", "message": "Please provide exercise and duration"}), 400

    try:
        duration = int(duration)
        workout_entry = {
            "id": len(workouts[category]) + 1,
            "exercise": exercise,
            "duration": duration,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        workouts[category].append(workout_entry)

        # Calculate total time
        total_time = sum(sum(w['duration'] for w in cat) for cat in workouts.values())

        # Motivational message
        if total_time >= 60:
            message = "🎉 Great job! You've logged over 60 minutes!"
        elif total_time >= 30:
            message = "💪 Keep going! You're making progress!"
        else:
            message = f"✅ '{exercise}' added successfully!"

        return jsonify({
            "status": "success",
            "message": message,
            "workout": workout_entry,
            "total_time": total_time
        })
    except ValueError:
        return jsonify({"status": "error", "message": "Duration must be a number"}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
