from flask import Flask, render_template, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)

workouts = {
    "Warm-up": [],
    "Workout": [],
    "Cool-down": []
}

# Workout chart data
workout_chart = {
    "Warm-up": ["Jumping Jacks", "Arm Circles", "Leg Swings", "Dynamic Stretches"],
    "Workout": ["Push-ups", "Squats", "Lunges", "Planks", "Burpees"],
    "Cool-down": ["Static Stretching", "Deep Breathing", "Walking"]
}

# Diet chart data
diet_chart = {
    "Weight Loss": {
        "breakfast": "Oatmeal with berries",
        "lunch": "Grilled chicken salad",
        "dinner": "Steamed fish with vegetables",
        "snacks": "Almonds, Greek yogurt"
    },
    "Muscle Gain": {
        "breakfast": "Scrambled eggs with toast",
        "lunch": "Chicken breast with rice",
        "dinner": "Steak with sweet potato",
        "snacks": "Protein shake, peanut butter"
    },
    "Endurance": {
        "breakfast": "Banana smoothie with oats",
        "lunch": "Pasta with lean meat",
        "dinner": "Salmon with quinoa",
        "snacks": "Energy bars, fruits"
    }
}

@app.route('/')
def index():
    return render_template('index_v12.html')

@app.route('/api/workouts', methods=['GET'])
def get_workouts():
    total_time = sum(sum(w['duration'] for w in cat) for cat in workouts.values())
    return jsonify({
        "workouts": workouts,
        "total_time": total_time,
        "status": "success"
    })

@app.route('/api/workouts', methods=['POST'])
def add_workout():
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

        return jsonify({
            "status": "success",
            "message": f"✅ '{exercise}' added successfully!",
            "workout": workout_entry
        })
    except ValueError:
        return jsonify({"status": "error", "message": "Duration must be a number"}), 400

@app.route('/api/workout-chart', methods=['GET'])
def get_workout_chart():
    return jsonify(workout_chart)

@app.route('/api/diet-chart', methods=['GET'])
def get_diet_chart():
    return jsonify(diet_chart)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
