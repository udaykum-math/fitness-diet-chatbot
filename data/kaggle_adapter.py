"""
kaggle_adapter.py
=================
Transforms the Kaggle "Gym Members Exercise Dataset"
(valakhorasani/gym-members-exercise-dataset)
into the unified format used by FitBot's ML pipeline.

Kaggle columns  →  FitBot columns
--------------------------------------------------
Age             → age
Gender          → gender
Weight (kg)     → weight_kg
Height (m)×100  → height_cm
BMI             → bmi            (kept as-is)
Experience_Level→ activity_level (mapped 1→Sedentary/Light, 2→Moderate, 3→Active)
Workout_Type    → workout_plan   (direct label)
Calories_Burned → calorie_target (session-level; scaled to daily estimate)
Fat_Percentage  → (used for fitness_category derivation)

Derived / engineered:
  bmi_category   → from BMI
  goal           → inferred from Workout_Type + Experience_Level
  diet_preference→ randomly assigned (not in dataset; realistic distribution)
  bmr            → Mifflin-St Jeor
  tdee           → bmr × activity multiplier
  diet_plan      → rule-based from goal + diet_preference
  fitness_category → from BMI + activity + Fat_Percentage

Run:
    python data/kaggle_adapter.py
"""

import pandas as pd
import numpy as np
import os

np.random.seed(42)

RAW   = "data/gym_members_exercise_tracking.csv"   # Kaggle CSV
OUT   = "data/fitness_diet_dataset.csv"             # FitBot unified format

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(RAW)
df.columns = df.columns.str.strip()
print(f"✅ Loaded Kaggle dataset: {df.shape}")

# ── Rename / unit-convert ─────────────────────────────────────────────────────
df = df.rename(columns={
    "Age":                      "age",
    "Gender":                   "gender",
    "Weight (kg)":              "weight_kg",
    "Height (m)":               "height_m",
    "BMI":                      "bmi",
    "Calories_Burned":          "calories_burned_session",
    "Workout_Type":             "workout_type_raw",
    "Fat_Percentage":           "fat_pct",
    "Water_Intake (liters)":    "water_liters",
    "Workout_Frequency (days/week)": "workout_freq",
    "Experience_Level":         "experience_level",
    "Session_Duration (hours)": "session_hours",
    "Max_BPM":                  "max_bpm",
    "Avg_BPM":                  "avg_bpm",
    "Resting_BPM":              "resting_bpm",
})

# height: metres → centimetres
df["height_cm"] = (df["height_m"] * 100).round(1)

# ── BMI Category ─────────────────────────────────────────────────────────────
def bmi_cat(b):
    if b < 18.5: return "Underweight"
    elif b < 25:  return "Normal"
    elif b < 30:  return "Overweight"
    else:         return "Obese"

df["bmi_category"] = df["bmi"].apply(bmi_cat)

# ── Activity Level  (from Experience_Level 1/2/3 + workout_freq) ─────────────
def map_activity(row):
    exp  = row["experience_level"]
    freq = row["workout_freq"]
    if exp == 1:
        return "Sedentary" if freq <= 2 else "Light"
    elif exp == 2:
        return "Moderate" if freq <= 3 else "Active"
    else:
        return "Active" if freq <= 4 else "Very Active"

df["activity_level"] = df.apply(map_activity, axis=1)

# ── Goal  (from workout_type + experience) ───────────────────────────────────
def map_goal(row):
    wt  = row["workout_type_raw"]
    exp = row["experience_level"]
    bmi = row["bmi"]
    if wt == "Cardio":
        return "Improve Stamina" if exp >= 2 else "Weight Loss"
    elif wt == "Strength":
        return "Muscle Gain" if bmi < 27 else "Weight Loss"
    elif wt == "HIIT":
        return "Weight Loss" if bmi >= 25 else "Maintain Fitness"
    elif wt == "Yoga":
        return "Maintain Fitness" if exp >= 2 else "Improve Stamina"
    return "Maintain Fitness"

df["goal"] = df.apply(map_goal, axis=1)

# ── Diet Preference  (realistically distributed; not in Kaggle data) ─────────
df["diet_preference"] = np.random.choice(
    ["Vegetarian", "Non-Vegetarian", "Vegan", "Eggetarian"],
    size=len(df), p=[0.45, 0.35, 0.10, 0.10]
)

# ── BMR  (Mifflin-St Jeor) ───────────────────────────────────────────────────
def calc_bmr(row):
    if row["gender"] == "Male":
        return round(10*row["weight_kg"] + 6.25*row["height_cm"] - 5*row["age"] + 5, 1)
    else:
        return round(10*row["weight_kg"] + 6.25*row["height_cm"] - 5*row["age"] - 161, 1)

df["bmr"] = df.apply(calc_bmr, axis=1)

# ── TDEE ─────────────────────────────────────────────────────────────────────
ACT_MULT = {"Sedentary":1.2, "Light":1.375, "Moderate":1.55, "Active":1.725, "Very Active":1.9}
df["tdee"] = df.apply(lambda r: round(r["bmr"] * ACT_MULT[r["activity_level"]], 1), axis=1)

# ── Calorie Target ───────────────────────────────────────────────────────────
GOAL_ADJ = {"Weight Loss":-400, "Weight Gain":400, "Muscle Gain":300,
            "Maintain Fitness":0, "Improve Stamina":100}
df["calorie_target"] = df.apply(
    lambda r: max(1200, min(4000, round(r["tdee"] + GOAL_ADJ[r["goal"]], 1))), axis=1
)

# ── Diet Plan ────────────────────────────────────────────────────────────────
def diet_plan(row):
    goal, bmi_c, dp = row["goal"], row["bmi_category"], row["diet_preference"]
    if goal == "Weight Loss":
        return "Low Calorie Balanced Diet"
    elif goal in ("Weight Gain", "Muscle Gain"):
        return "High Protein Non-Veg Diet" if dp in ("Non-Vegetarian","Eggetarian") else "High Protein Veg Diet"
    elif goal == "Improve Stamina":
        return "High Carb Performance Diet"
    else:
        return "Low Calorie Balanced Diet" if bmi_c in ("Overweight","Obese") else "Balanced Maintenance Diet"

df["diet_plan"] = df.apply(diet_plan, axis=1)

# ── Workout Plan  (from original Kaggle workout_type + experience) ────────────
def workout_plan(row):
    wt  = row["workout_type_raw"]
    exp = row["experience_level"]
    age = row["age"]
    goal= row["goal"]
    if wt == "Cardio":
        return "Beginner Cardio + Walking" if exp == 1 else "Cardio Endurance Training"
    elif wt == "HIIT":
        return "Beginner Cardio + Walking" if exp == 1 else "Intermediate Cardio + HIIT"
    elif wt == "Strength":
        if exp == 1: return "Beginner Fitness Routine"
        elif age > 45: return "Moderate Strength Training"
        return "Progressive Strength Training" if goal == "Muscle Gain" else "Compound Strength Training"
    elif wt == "Yoga":
        return "Active Lifestyle Routine" if exp >= 2 else "Beginner Fitness Routine"
    return "Beginner Fitness Routine"

df["workout_plan"] = df.apply(workout_plan, axis=1)

# ── Fitness Category  (BMI + activity + fat %) ───────────────────────────────
def fitness_cat(row):
    bmi_c   = row["bmi_category"]
    act     = row["activity_level"]
    fat     = row["fat_pct"]
    age     = row["age"]
    if bmi_c == "Normal" and act in ("Active","Very Active") and fat < 20:
        return "Fit"
    elif bmi_c in ("Overweight","Obese") or act == "Sedentary" or fat > 28:
        return "Needs Improvement"
    else:
        return "Moderately Fit"

df["fitness_category"] = df.apply(fitness_cat, axis=1)

# ── Select & Save ─────────────────────────────────────────────────────────────
FINAL_COLS = [
    "age","gender","height_cm","weight_kg","bmi","bmi_category",
    "activity_level","goal","diet_preference","bmr","tdee",
    "calorie_target","diet_plan","workout_plan","fitness_category",
    # Kaggle-exclusive bonus columns (kept for richer EDA)
    "fat_pct","water_liters","workout_freq","session_hours",
    "max_bpm","avg_bpm","calories_burned_session",
]

df_out = df[FINAL_COLS].copy()
df_out.to_csv(OUT, index=False)

print(f"\n✅ Unified dataset saved → {OUT}")
print(f"   Rows: {len(df_out)}  |  Columns: {len(df_out.columns)}")
print("\nfitness_category:\n", df_out["fitness_category"].value_counts().to_string())
print("\ndiet_plan:\n",        df_out["diet_plan"].value_counts().to_string())
print("\nworkout_plan:\n",     df_out["workout_plan"].value_counts().to_string())
print("\nactivity_level:\n",   df_out["activity_level"].value_counts().to_string())
