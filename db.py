import os
from supabase import create_client
from typing import List, Dict
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_full_workout(workout_data: Dict):
    # Insert the workout
    workout_resp = supabase.table("workouts").insert({
        "date": workout_data["date"],
        "label": workout_data.get("label", None)
    }).execute()
    workout_id = workout_resp.data[0]["id"]

    for exercise in workout_data["exercises"]:
        exercise_resp = supabase.table("exercises").insert({
            "workout_id": workout_id,
            "name": exercise["name"]
        }).execute()
        exercise_id = exercise_resp.data[0]["id"]

        for s in exercise["sets"]:
            supabase.table("sets").insert({
                "exercise_id": exercise_id,
                "reps": s["reps"],
                "weight": s["weight"],
                "notes": s["notes"]
            }).execute()

def get_workouts_by_date(date: str) -> List[Dict]:
    workout_resp = supabase.table("workouts").select("*").eq("date", date).order("id", desc=True).execute()
    workouts = []

    for w in workout_resp.data:
        workout_id = w["id"]
        label = w["label"]
        ex_resp = supabase.table("exercises").select("*").eq("workout_id", workout_id).execute()

        exercises = []
        for ex in ex_resp.data:
            ex_id = ex["id"]
            sets_resp = supabase.table("sets").select("*").eq("exercise_id", ex_id).execute()
            sets = [{"reps": s["reps"], "weight": s["weight"], "notes": s["notes"]} for s in sets_resp.data]
            exercises.append({"name": ex["name"], "sets": sets})

        workouts.append({
            "id": workout_id,
            "date": date,
            "label": label,
            "exercises": exercises
        })

    return workouts

def delete_workout_by_id(workout_id: int):
    # Supabase does not cascade deletes via the API, so do it manually
    ex_resp = supabase.table("exercises").select("id").eq("workout_id", workout_id).execute()
    exercise_ids = [ex["id"] for ex in ex_resp.data]

    for ex_id in exercise_ids:
        supabase.table("sets").delete().eq("exercise_id", ex_id).execute()

    supabase.table("exercises").delete().eq("workout_id", workout_id).execute()
    supabase.table("workouts").delete().eq("id", workout_id).execute()
