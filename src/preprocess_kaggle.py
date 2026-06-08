"""
preprocess_kaggle.py
Loads the real Kaggle "Gym Members Exercise Dataset", engineers new target
columns (fitness_category, diet_plan, workout_plan) from the existing rich
features, then saves a clean model-ready CSV.

Run: python src/preprocess_kaggle.py
"""

import pandas as pd
import numpy as np
import os

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv("data/gym_members_exercise_tracking.csv")
print(f"Loaded: {df.shape[0]} rows × {df.shape[1]} cols")
print("Columns:", list(df.columns))

# ── Rename for cleaner access ─────────────────────────────────────────────────
df.rename(columns={
    "Weight (kg)":              "weight_kg",
    "Height (m)":               "height_m",
    "Session_Duration (hours)": "session_duration_h",
    "Calories_Burned":          "calories_burned",
    "Fat_Percentage":           "fat_pct",
    "Water_Intake (liters)":    "water_intake_l",
    "Workout_Frequency (days/week)": "workout_freq",
    "Max_BPM":                  "max_bpm",
    "Avg_BPM":                  "avg_bpm",
    "Resting_BPM":              "resting_bpm",
    "Workout_Type":             "workout_type",
    "Experience_Level":         "experience_level",
}, inplace=True)

df.columns = df.columns.str.lower()

# ── Derived columns ───────────────────────────────────────────────────────────
df["height_cm"]   = (df["height_m"] * 100).round(1)
df["bmi_recalc"]  = (df["weight_kg"] / df["height_m"]**2).round(2)

# BMI Category
def bmi_cat(b):
    if b < 18.5: return "Underweight"
    elif b < 25:  return "Normal"
    elif b < 30:  return "Overweight"
    else:         return "Obese"
df["bmi_category"] = df["bmi"].apply(bmi_cat)

# BMR (Mifflin-St Jeor)
def calc_bmr(row):
    if row["gender"] == "Male":
        return round(10*row["weight_kg"] + 6.25*row["height_cm"] - 5*row["age"] + 5, 1)
    else:
        return round(10*row["weight_kg"] + 6.25*row["height_cm"] - 5*row["age"] - 161, 1)
df["bmr"] = df.apply(calc_bmr, axis=1)

# TDEE from workout frequency & experience
freq_mult = {1: 1.2, 2: 1.375, 3: 1.55, 4: 1.725, 5: 1.9, 6: 1.9}
df["tdee"] = df.apply(lambda r: round(r["bmr"] * freq_mult.get(r["workout_freq"], 1.55), 1), axis=1)

# ── Engineered TARGET labels ──────────────────────────────────────────────────

# 1. Fitness Category  (real signals: fat_pct, bmi, experience_level, workout_freq)
def fitness_category(row):
    score = 0
    if row["fat_pct"] < 20: score += 2
    elif row["fat_pct"] < 28: score += 1
    if row["bmi"] < 25: score += 2
    elif row["bmi"] < 30: score += 1
    if row["experience_level"] == 3: score += 2
    elif row["experience_level"] == 2: score += 1
    if row["workout_freq"] >= 4: score += 1
    if score >= 5: return "Fit"
    elif score >= 3: return "Moderately Fit"
    else: return "Needs Improvement"
df["fitness_category"] = df.apply(fitness_category, axis=1)

# 2. Diet Plan  (from workout_type + bmi_category)
def diet_plan(row):
    wt  = row["workout_type"]
    bmi = row["bmi_category"]
    if wt == "Cardio" and bmi in ("Overweight","Obese"):
        return "Low Calorie Balanced Diet"
    elif wt in ("Strength","HIIT") and row["gender"] == "Male":
        return "High Protein Non-Veg Diet"
    elif wt in ("Strength","HIIT") and row["gender"] == "Female":
        return "High Protein Veg Diet"
    elif wt == "Yoga":
        return "Balanced Maintenance Diet"
    elif wt == "Cardio" and bmi in ("Normal","Underweight"):
        return "High Carb Performance Diet"
    else:
        return "Balanced Maintenance Diet"
df["diet_plan"] = df.apply(diet_plan, axis=1)

# 3. Workout Plan  (from experience_level + workout_type + calories_burned)
def workout_plan(row):
    lvl = row["experience_level"]
    wt  = row["workout_type"]
    if lvl == 1:
        if wt == "Cardio":   return "Beginner Cardio + Walking"
        elif wt == "HIIT":   return "Intermediate Cardio + HIIT"
        elif wt == "Strength": return "Beginner Fitness Routine"
        else:                return "Active Lifestyle Routine"
    elif lvl == 2:
        if wt in ("Strength","HIIT"): return "Progressive Strength Training"
        elif wt == "Cardio":          return "Cardio Endurance Training"
        else:                         return "Active Lifestyle Routine"
    else:  # expert
        if wt == "Strength":          return "Compound Strength Training"
        elif wt == "HIIT":            return "Intermediate Cardio + HIIT"
        elif wt == "Cardio":          return "Cardio Endurance Training"
        else:                         return "Active Lifestyle Routine"
df["workout_plan"] = df.apply(workout_plan, axis=1)

# ── Goal inference (for profile display) ────────────────────────────────────
def infer_goal(row):
    if row["bmi_category"] in ("Overweight","Obese"):
        return "Weight Loss"
    elif row["bmi_category"] == "Underweight":
        return "Weight Gain"
    elif row["workout_type"] == "Strength":
        return "Muscle Gain"
    elif row["workout_type"] == "Cardio":
        return "Improve Stamina"
    else:
        return "Maintain Fitness"
df["inferred_goal"] = df.apply(infer_goal, axis=1)

# ── Save ──────────────────────────────────────────────────────────────────────
keep_cols = [
    "age","gender","weight_kg","height_m","height_cm",
    "bmi","bmi_category","max_bpm","avg_bpm","resting_bpm",
    "session_duration_h","calories_burned","fat_pct",
    "water_intake_l","workout_freq","workout_type","experience_level",
    "bmr","tdee","inferred_goal",
    # targets
    "fitness_category","diet_plan","workout_plan"
]
df = df[keep_cols]
df.to_csv("data/kaggle_fitness_clean.csv", index=False)

print("\n✅ Clean dataset saved → data/kaggle_fitness_clean.csv")
print(f"   Rows: {len(df)}  |  Cols: {len(df.columns)}")
print("\nTarget distributions:")
for col in ["fitness_category","diet_plan","workout_plan"]:
    print(f"\n{col}:\n{df[col].value_counts().to_string()}")
