import sqlite3
from typing import List, Dict

DB_NAME = 'fittracker.db'


def create_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def create_tables():
    conn = create_connection()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            label TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (workout_id) REFERENCES workouts(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS sets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exercise_id INTEGER NOT NULL,
            reps INTEGER,
            weight REAL,
            notes TEXT,
            FOREIGN KEY (exercise_id) REFERENCES exercises(id)
        )
    ''')

    conn.commit()
    conn.close()


def save_full_workout(workout_data: Dict):
    conn = create_connection()
    c = conn.cursor()

    # Insert the workout
    c.execute(
        'INSERT INTO workouts (date, label) VALUES (?, ?)',
        (workout_data['date'], workout_data.get('label', None))
    )
    workout_id = c.lastrowid

    for exercise in workout_data['exercises']:
        c.execute(
            'INSERT INTO exercises (workout_id, name) VALUES (?, ?)',
            (workout_id, exercise['name'])
        )
        exercise_id = c.lastrowid

        for s in exercise['sets']:
            c.execute(
                'INSERT INTO sets (exercise_id, reps, weight, notes) VALUES (?, ?, ?, ?)',
                (exercise_id, s['reps'], s['weight'], s['notes'])
            )

    conn.commit()
    conn.close()


def get_workouts_by_date(date: str) -> List[Dict]:
    conn = create_connection()
    c = conn.cursor()

    c.execute('SELECT id, label FROM workouts WHERE date = ? ORDER BY id DESC', (date,))
    workout_rows = c.fetchall()

    results = []
    for workout_id, label in workout_rows:
        c.execute('SELECT id, name FROM exercises WHERE workout_id = ?', (workout_id,))
        exercise_rows = c.fetchall()

        exercises = []
        for exercise_id, name in exercise_rows:
            c.execute('SELECT reps, weight, notes FROM sets WHERE exercise_id = ?', (exercise_id,))
            sets = [{'reps': r, 'weight': w, 'notes': n} for r, w, n in c.fetchall()]
            exercises.append({'name': name, 'sets': sets})

        results.append({'id': workout_id, 'label': label, 'date': date, 'exercises': exercises})

    conn.close()
    return results


def delete_workout_by_id(workout_id: int):
    conn = create_connection()
    c = conn.cursor()

    c.execute('DELETE FROM sets WHERE exercise_id IN (SELECT id FROM exercises WHERE workout_id = ?)', (workout_id,))
    c.execute('DELETE FROM exercises WHERE workout_id = ?', (workout_id,))
    c.execute('DELETE FROM workouts WHERE id = ?', (workout_id,))

    conn.commit()
    conn.close()
