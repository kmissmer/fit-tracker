import unittest
from main import app
from unittest.mock import patch
import json

class TestWorkoutAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health_check(self):
        res = self.client.get("/api/health")
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["status"], "healthy")  # update your route if it's different

    @patch("main.save_full_workout")
    def test_create_workout_success(self, mock_save):
        sample_workout = {
            "date": "2025-05-25",
            "exercises": [
                {
                    "name": "Push Up",
                    "sets": [{"reps": 10, "weight": 0}]
                }
            ]
        }
        res = self.client.post("/api/workouts", json=sample_workout)
        self.assertEqual(res.status_code, 201)



    def test_create_workout_missing_data(self):
        res = self.client.post("/api/workouts", json=None)
        self.assertEqual(res.status_code, 400)

    def test_get_workouts_empty(self):
        with patch("db.get_workouts_by_date", return_value=[]):
            res = self.client.get("/api/workouts")
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.get_json()["data"], [])

    def test_get_workouts_invalid_date(self):
        res = self.client.get("/api/workouts?date=invalid-date")
        self.assertEqual(res.status_code, 400)

    def test_update_workout_no_data(self):
        res = self.client.put("/api/workouts/1", json=None)
        self.assertEqual(res.status_code, 400)

    def test_update_workout_success(self):
        sample_update = {
            "exercises": [
                {
                    "name": "Squat",
                    "sets": [{"reps": 5, "weight": 100}]
                }
            ]
        }
        res = self.client.put("/api/workouts/1", json=sample_update)
        self.assertEqual(res.status_code, 200)
        self.assertIn("updated successfully", res.get_json()["message"].lower())

    @patch("main.delete_workout_by_id", return_value=True)
    def test_delete_workout_success(self, mock_delete):
        res = self.client.delete("/api/workouts/1")
        self.assertEqual(res.status_code, 200)


    def test_delete_workout_not_found(self):
        with patch("db.delete_workout_by_id", return_value=False):
            res = self.client.delete("/api/workouts/999")
            self.assertEqual(res.status_code, 404)
            self.assertIn("not found", res.get_json()["error"].lower())

if __name__ == "__main__":
    unittest.main()
