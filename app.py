import streamlit as st
from datetime import date
from db import (
    save_full_workout,
    get_workouts_by_date,
    delete_workout_by_id
)

st.title("🏋️ FitProof: Supabase-Backed Workout Logger")

# Session state setup
if "date" not in st.session_state:
    st.session_state.date = str(date.today())
if "exercises" not in st.session_state:
    st.session_state.exercises = []
if "editing_workout_id" not in st.session_state:
    st.session_state.editing_workout_id = None

# Date selector
selected_date = st.date_input("Workout Date", value=date.fromisoformat(st.session_state.date))
selected_date_str = selected_date.strftime('%Y-%m-%d')

if selected_date_str != st.session_state.date:
    st.session_state.date = selected_date_str
    st.session_state.exercises = []
    st.session_state.editing_workout_id = None

# Add exercise
if st.button("➕ Add Exercise"):
    st.session_state.exercises.append({"name": "", "sets": []})

# Workout label
label = st.text_input("Workout Label (optional)", placeholder="e.g., Push Day")

# Render exercises and sets
for i, exercise in enumerate(st.session_state.exercises):
    with st.expander(f"Exercise {i + 1}"):
        exercise["name"] = st.text_input("Exercise Name", value=exercise["name"], key=f"ex_name_{i}")

        if st.button("➕ Add Set", key=f"add_set_{i}"):
            exercise["sets"].append({"reps": 0, "weight": 0.0, "notes": ""})

        for j, s in enumerate(exercise["sets"]):
            st.markdown(f"**Set {j + 1}**")
            s["reps"] = st.number_input("Reps", min_value=0, value=s["reps"], key=f"reps_{i}_{j}")
            s["weight"] = st.number_input("Weight (lbs)", min_value=0.0, value=s["weight"], key=f"weight_{i}_{j}")
            s["notes"] = st.text_input("Notes", value=s["notes"], key=f"notes_{i}_{j}")
            st.markdown("---")

# Save workout
if st.button("✅ Save Workout"):
    if st.session_state.editing_workout_id:
        delete_workout_by_id(st.session_state.editing_workout_id)
    save_full_workout({
        "date": st.session_state.date,
        "label": label,
        "exercises": st.session_state.exercises
    })
    st.session_state.editing_workout_id = None
    st.success("💾 Workout saved!")

# Show saved workouts for selected date
st.markdown("## 📅 Saved Workouts for This Date")
workouts = get_workouts_by_date(st.session_state.date)
if not workouts:
    st.info("No saved workouts for this date.")
else:
    for workout in workouts:
        with st.expander(f"{workout['label'] or 'Unnamed'} — {workout['date']}"):
            for exercise in workout["exercises"]:
                st.markdown(f"**{exercise['name']}**")
                for s in exercise["sets"]:
                    st.markdown(f"- {s['reps']} reps @ {s['weight']} lbs — {s['notes']}")
            col1, col2 = st.columns(2)
            if col1.button(f"✏️ Edit Workout {workout['id']}", key=f"edit_{workout['id']}"):
                st.session_state.exercises = workout["exercises"]
                st.session_state.date = workout["date"]
                st.session_state.editing_workout_id = workout["id"]
                st.experimental_rerun()
            if col2.button(f"🗑️ Delete Workout {workout['id']}", key=f"del_{workout['id']}"):
                delete_workout_by_id(workout["id"])
                st.success("Workout deleted.")
                st.rerun()
