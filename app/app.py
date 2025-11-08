from flask import Flask, render_template, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)

# In-memory storage (for demo purposes)
workouts = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/workouts', methods=['GET'])
def get_workouts():
    """Get all workouts"""
    return jsonify({"workouts": workouts, "status": "success"})

@app.route('/api/workouts', methods=['POST'])
def add_workout():
    """Add a new workout"""
    data = request.json

    workout_name = data.get('workout')
    duration = data.get('duration')

    if not workout_name or not duration:
        return jsonify({"status": "error", "message": "Please provide both workout and duration"}), 400

    try:
        duration = int(duration)
        workout_entry = {
            "id": len(workouts) + 1,
            "workout": workout_name,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        workouts.append(workout_entry)
        return jsonify({"status": "success", "message": f"'{workout_name}' added successfully!", "workout": workout_entry})
    except ValueError:
        return jsonify({"status": "error", "message": "Duration must be a number"}), 400

@app.route('/api/workouts/<int:workout_id>', methods=['DELETE'])
def delete_workout(workout_id):
    """Delete a workout by ID"""
    global workouts
    workouts = [w for w in workouts if w['id'] != workout_id]
    return jsonify({"status": "success", "message": "Workout deleted"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
