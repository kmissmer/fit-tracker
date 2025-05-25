from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import re
from db import (
    save_full_workout,
    get_workouts_by_date,
    delete_workout_by_id
)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Health check route
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

# Create workout
@app.route('/api/workouts', methods=['POST'])
def create_workout():
    """Create a new workout"""
    try:
        data = request.get_json(silent=True)

        if data is None:
            return jsonify({"error": "No data provided"}), 400

        if "date" not in data:
            return jsonify({"error": "Date is required"}), 400

        if "exercises" not in data or not isinstance(data["exercises"], list):
            return jsonify({"error": "Exercises array is required"}), 400


        for i, ex in enumerate(data["exercises"]):
            if "name" not in ex:
                return jsonify({"error": f"Exercise {i + 1} missing name"}), 400
            if "sets" not in ex or not isinstance(ex["sets"], list):
                return jsonify({"error": f"Exercise {i + 1} has invalid sets"}), 400


        save_full_workout(data)
        return jsonify({"message": "Workout created successfully", "data": data}), 201

    except Exception as e:
        return jsonify({"error": "Failed to create workout", "details": str(e)}), 500

# Update workout
@app.route('/api/workouts/<int:workout_id>', methods=['PUT'])
def update_workout(workout_id):
    """Update a workout by ID"""
    try:
        data = request.get_json(silent=True)

        if data is None:
            return jsonify({"error": "No data provided"}), 400

        # Implement your update logic here if needed
        return jsonify({"message": "Workout updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": "Failed to update workout", "details": str(e)}), 500

# Get workouts
@app.route('/api/workouts', methods=['GET'])
def get_workouts():
    try:
        date = request.args.get("date")
        if date and not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
            return jsonify({"error": "Invalid date format"}), 400

        workouts = get_workouts_by_date(date) if date else []
        return jsonify({"data": workouts}), 200

    except Exception as e:
        return jsonify({"error": "Failed to fetch workouts", "details": str(e)}), 500



@app.route('/api/workouts/<int:workout_id>', methods=['DELETE'])
def delete_workout(workout_id):
    """Delete a workout by ID"""
    try:
        success = delete_workout_by_id(workout_id)
        if not success:
            return jsonify({"error": "Workout not found"}), 404

        return jsonify({"message": "Workout deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": "Failed to delete workout", "details": str(e)}), 500

