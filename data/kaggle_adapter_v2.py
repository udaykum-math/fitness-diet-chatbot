"""
kaggle_adapter_v2.py
====================
Merges TWO Kaggle datasets into one unified FitBot dataset.

Dataset 1 (REQUIRED):
  gym_members_exercise_tracking.csv
  → kaggle.com/datasets/valakhorasani/gym-members-exercise-dataset

Dataset 2 (OPTIONAL - adds diet plan data):
  meal_plan_exercise_schedule.csv
  → kaggle.com/datasets/kavindavimukthi/meal-plan-and-exercise-schedule-gender-goal-bmi

Place both CSVs inside:   data/raw/
Output saved to:          data/fitness_diet_dataset.csv

Run:
    python data/kaggle_adapter_v2.py
"""

import pandas as pd
import numpy as np
import os, glob

np.random.seed(42)

# ─────────────────────────────────────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────────────────────────────────────
RAW_DIR  = os.path.join(os.path.dirname(__file__), "raw")
OUT_FILE = os.path.join(os.path.dirname(__file__), "fitness_diet_dataset.csv")

os.makedirs(RAW_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# HELPER – find a CSV file by partial name inside data/raw/
# ─────────────────────────────────────────────────────────────────────────────
def find_csv(keyword):
    """Return the first CSV in data/raw/ whose filename contains keyword."""
    pattern = os.path.join(RAW_DIR, f"*{keyword}*.csv")
    matches = glob.glob(pattern, recursive=False)
    if matches:
        return matches[0]
    # also try in data/ itself (in case user placed it there)
    pattern2 = os.path.join(os.path.dirname(__file__), f"*{keyword}*.csv")
    matches2 = glob.glob(pattern2, recursive=False)
    return matches2[0] if matches2 else None

# ─────────────────────────────────────────────────────────────────────────────
# LOCATE DATASET FILES
# ─────────────────────────────────────────────────────────────────────────────
GYM_CSV  = find_csv("gym") or find_csv("exercise_tracking") or find_csv("gym_members")
MEAL_CSV = find_csv("meal") or find_csv("meal_plan") or find_csv("exercise_schedule")

print("=" * 60)
print("🏋️  FITBOT — KAGGLE DATASET ADAPTER v2")
print("=" * 60)
print(f"\n📂 Looking in: {RAW_DIR}")
print(f"   Dataset 1 (Gym):  {'✅ ' + os.path.basename(GYM_CSV) if GYM_CSV else '❌ NOT FOUND'}")
print(f"   Dataset 2 (Meal): {'✅ ' + os.path.basename(MEAL_CSV) if MEAL_CSV else '⚠️  NOT FOUND (will use rules instead)'}")

if not GYM_CSV:
    print("\n❌ ERROR: Dataset 1 not found!")
    print("   Please download from:")
    print("   https://www.kaggle.com/datasets/valakhorasani/gym-members-exercise-dataset")
    print(f"   and place the CSV inside: {RAW_DIR}")
    exit(1)

# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATASET 1 — GYM MEMBERS
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{'─'*40}")
print("📊 Loading Dataset 1 — Gym Members...")
gym = pd.read_csv(GYM_CSV)
gym.columns = gym.columns.str.strip()
print(f"   Shape: {gym.shape}")
print(f"   Columns: {list(gym.columns)}")

# Rename to standard names
gym = gym.rename(columns={
    "Age":                          "age",
    "Gender":                       "gender",
    "Weight (kg)":                  "weight_kg",
    "Height (m)":                   "height_m",
    "BMI":                          "bmi",
    "Calories_Burned":              "calories_burned_session",
    "Workout_Type":                 "workout_type_raw",
    "Fat_Percentage":               "fat_pct",
    "Water_Intake (liters)":        "water_liters",
    "Workout_Frequency (days/week)":"workout_freq",
    "Experience_Level":             "experience_level",
    "Session_Duration (hours)":     "session_hours",
    "Max_BPM":                      "max_bpm",
    "Avg_BPM":                      "avg_bpm",
    "Resting_BPM":                  "resting_bpm",
})

# height m → cm
gym["height_cm"] = (gym["height_m"] * 100).round(1)

# ── BMI Category ──────────────────────────────────────────────────────────────
def bmi_cat(b):
    if b < 18.5: return "Underweight"
    elif b < 25: return "Normal"
    elif b < 30: return "Overweight"
    else:        return "Obese"

gym["bmi_category"] = gym["bmi"].apply(bmi_cat)

# ── Activity Level ────────────────────────────────────────────────────────────
def map_activity(row):
    exp  = row["experience_level"]
    freq = row["workout_freq"]
    if exp == 1:
        return "Sedentary" if freq <= 2 else "Light"
    elif exp == 2:
        return "Moderate" if freq <= 3 else "Active"
    else:
        return "Active" if freq <= 4 else "Very Active"

gym["activity_level"] = gym.apply(map_activity, axis=1)

# ── Goal ──────────────────────────────────────────────────────────────────────
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

gym["goal"] = gym.apply(map_goal, axis=1)

# ── Diet Preference ───────────────────────────────────────────────────────────
gym["diet_preference"] = np.random.choice(
    ["Vegetarian", "Non-Vegetarian", "Vegan", "Eggetarian"],
    size=len(gym), p=[0.45, 0.35, 0.10, 0.10]
)

# ── BMR ───────────────────────────────────────────────────────────────────────
def calc_bmr(row):
    if row["gender"] == "Male":
        return round(10*row["weight_kg"] + 6.25*row["height_cm"] - 5*row["age"] + 5, 1)
    else:
        return round(10*row["weight_kg"] + 6.25*row["height_cm"] - 5*row["age"] - 161, 1)

gym["bmr"] = gym.apply(calc_bmr, axis=1)

# ── TDEE ──────────────────────────────────────────────────────────────────────
ACT_MULT = {"Sedentary":1.2,"Light":1.375,"Moderate":1.55,"Active":1.725,"Very Active":1.9}
gym["tdee"] = gym.apply(lambda r: round(r["bmr"] * ACT_MULT[r["activity_level"]], 1), axis=1)

# ── Calorie Target ────────────────────────────────────────────────────────────
GOAL_ADJ = {"Weight Loss":-400,"Weight Gain":400,"Muscle Gain":300,
            "Maintain Fitness":0,"Improve Stamina":100}
gym["calorie_target"] = gym.apply(
    lambda r: max(1200, min(4000, round(r["tdee"] + GOAL_ADJ[r["goal"]], 1))), axis=1
)

# ── Workout Plan ──────────────────────────────────────────────────────────────
def map_workout_plan(row):
    wt  = row["workout_type_raw"]
    exp = row["experience_level"]
    age = row["age"]
    goal= row["goal"]
    if wt == "Cardio":
        return "Beginner Cardio + Walking" if exp == 1 else "Cardio Endurance Training"
    elif wt == "HIIT":
        return "Beginner Cardio + Walking" if exp == 1 else "Intermediate Cardio + HIIT"
    elif wt == "Strength":
        if exp == 1:    return "Beginner Fitness Routine"
        elif age > 45:  return "Moderate Strength Training"
        return "Progressive Strength Training" if goal == "Muscle Gain" else "Compound Strength Training"
    elif wt == "Yoga":
        return "Active Lifestyle Routine" if exp >= 2 else "Beginner Fitness Routine"
    return "Beginner Fitness Routine"

gym["workout_plan"] = gym.apply(map_workout_plan, axis=1)

# ── Fitness Category ──────────────────────────────────────────────────────────
def fitness_cat(row):
    bmi_c = row["bmi_category"]
    act   = row["activity_level"]
    fat   = row["fat_pct"]
    if bmi_c == "Normal" and act in ("Active","Very Active") and fat < 20:
        return "Fit"
    elif bmi_c in ("Overweight","Obese") or act == "Sedentary" or fat > 28:
        return "Needs Improvement"
    else:
        return "Moderately Fit"

gym["fitness_category"] = gym.apply(fitness_cat, axis=1)

print(f"   ✅ Dataset 1 processed: {len(gym)} rows")

# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATASET 2 — MEAL PLAN (if available)
# ─────────────────────────────────────────────────────────────────────────────
diet_plan_map = {}   # will hold bmi_cat+goal → diet_plan if Dataset 2 exists

if MEAL_CSV:
    print(f"\n{'─'*40}")
    print("🍽️  Loading Dataset 2 — Meal Plan & Exercise Schedule...")
    meal = pd.read_csv(MEAL_CSV)
    meal.columns = meal.columns.str.strip()
    print(f"   Shape: {meal.shape}")
    print(f"   Columns: {list(meal.columns)}")

    # Try to find diet/meal plan column (name varies by Kaggle version)
    diet_col    = next((c for c in meal.columns if "diet"   in c.lower() or "meal"   in c.lower() or "food"   in c.lower()), None)
    goal_col    = next((c for c in meal.columns if "goal"   in c.lower() or "target" in c.lower()), None)
    bmi_col     = next((c for c in meal.columns if "bmi"    in c.lower()), None)
    gender_col  = next((c for c in meal.columns if "gender" in c.lower()), None)

    print(f"   Diet column found : {diet_col}")
    print(f"   Goal column found : {goal_col}")
    print(f"   BMI column found  : {bmi_col}")

    if diet_col and goal_col:
        # Build lookup: goal → most common diet plan label
        meal_clean = meal[[goal_col, diet_col]].dropna()
        meal_clean.columns = ["goal_raw", "diet_plan_raw"]

        # Normalize goal names to match FitBot goals
        goal_norm = {
            "weight loss":      "Weight Loss",
            "weightloss":       "Weight Loss",
            "lose weight":      "Weight Loss",
            "weight gain":      "Weight Gain",
            "muscle gain":      "Muscle Gain",
            "muscle":           "Muscle Gain",
            "maintain":         "Maintain Fitness",
            "maintenance":      "Maintain Fitness",
            "stamina":          "Improve Stamina",
            "endurance":        "Improve Stamina",
        }
        meal_clean["goal_norm"] = meal_clean["goal_raw"].str.lower().str.strip().map(
            lambda x: next((v for k,v in goal_norm.items() if k in x), None)
        )
        meal_clean = meal_clean.dropna(subset=["goal_norm"])

        # Build goal → diet_plan lookup (most frequent)
        for goal_val, grp in meal_clean.groupby("goal_norm"):
            top_diet = grp["diet_plan_raw"].value_counts().index[0]
            diet_plan_map[goal_val] = str(top_diet)

        print(f"   ✅ Diet plan lookup built: {diet_plan_map}")
    else:
        print("   ⚠️  Could not find diet/goal columns — using rule-based diet plans")
else:
    print("\n⚠️  Dataset 2 not found — using rule-based diet plans (still valid!)")

# ─────────────────────────────────────────────────────────────────────────────
# ASSIGN DIET PLAN
# Either from Dataset 2 lookup OR rule-based (both are valid for ML training)
# ─────────────────────────────────────────────────────────────────────────────
RULE_DIET = {
    "Weight Loss":      "Low Calorie Balanced Diet",
    "Weight Gain":      "High Protein Veg Diet",
    "Muscle Gain":      "High Protein Non-Veg Diet",
    "Maintain Fitness": "Balanced Maintenance Diet",
    "Improve Stamina":  "High Carb Performance Diet",
}

def assign_diet_plan(row):
    goal = row["goal"]
    dp   = row["diet_preference"]
    # Use Dataset 2 lookup if available
    if goal in diet_plan_map:
        return diet_plan_map[goal]
    # Otherwise rule-based
    if goal in ("Weight Gain", "Muscle Gain"):
        return "High Protein Non-Veg Diet" if dp in ("Non-Vegetarian","Eggetarian") else "High Protein Veg Diet"
    return RULE_DIET.get(goal, "Balanced Maintenance Diet")

gym["diet_plan"] = gym.apply(assign_diet_plan, axis=1)

# ─────────────────────────────────────────────────────────────────────────────
# FINAL COLUMN SELECTION & SAVE
# ─────────────────────────────────────────────────────────────────────────────
FINAL_COLS = [
    "age", "gender", "height_cm", "weight_kg", "bmi", "bmi_category",
    "activity_level", "goal", "diet_preference", "bmr", "tdee",
    "calorie_target", "diet_plan", "workout_plan", "fitness_category",
    # Kaggle bonus columns (enrich ML features)
    "fat_pct", "water_liters", "workout_freq",
    "session_hours", "max_bpm", "avg_bpm", "calories_burned_session",
]

df_out = gym[FINAL_COLS].copy()
df_out = df_out.dropna().reset_index(drop=True)
df_out.to_csv(OUT_FILE, index=False)

# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"✅ UNIFIED DATASET SAVED → {OUT_FILE}")
print(f"   Rows: {len(df_out)}  |  Columns: {len(df_out.columns)}")
print(f"\nfitness_category:\n{df_out['fitness_category'].value_counts().to_string()}")
print(f"\ndiet_plan:\n{df_out['diet_plan'].value_counts().to_string()}")
print(f"\nworkout_plan:\n{df_out['workout_plan'].value_counts().to_string()}")
print(f"\nactivity_level:\n{df_out['activity_level'].value_counts().to_string()}")
print(f"\n{'='*60}")
print("✅ Now run:  python src/train_model.py")
print("✅ Then run: streamlit run app.py")
print(f"{'='*60}")
