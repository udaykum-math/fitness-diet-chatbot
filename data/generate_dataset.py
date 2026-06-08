"""
Dataset generator for Fitness & Diet Recommendation Chatbot.
Generates a realistic synthetic dataset based on BMI, activity, and fitness goals.
Run: python data/generate_dataset.py
"""

import pandas as pd
import numpy as np
import random

np.random.seed(42)
random.seed(42)

N = 2000

genders = np.random.choice(["Male", "Female"], size=N, p=[0.5, 0.5])
ages = np.random.randint(18, 60, size=N)

heights, weights = [], []
for g in genders:
    if g == "Male":
        h = round(random.gauss(174, 8), 1)
        w = round(random.gauss(74, 12), 1)
    else:
        h = round(random.gauss(162, 7), 1)
        w = round(random.gauss(62, 10), 1)
    heights.append(max(140, min(210, h)))
    weights.append(max(40, min(140, w)))

heights = np.array(heights)
weights = np.array(weights)
bmi = np.round(weights / (heights / 100) ** 2, 2)

activity_levels = np.random.choice(
    ["Sedentary", "Light", "Moderate", "Active", "Very Active"],
    size=N, p=[0.2, 0.25, 0.25, 0.2, 0.1]
)

goals = np.random.choice(
    ["Weight Loss", "Weight Gain", "Muscle Gain", "Maintain Fitness", "Improve Stamina"],
    size=N, p=[0.3, 0.15, 0.25, 0.2, 0.1]
)

diet_prefs = np.random.choice(
    ["Vegetarian", "Non-Vegetarian", "Vegan", "Eggetarian"],
    size=N, p=[0.45, 0.35, 0.1, 0.1]
)

# BMR using Mifflin-St Jeor
bmr = []
for i in range(N):
    if genders[i] == "Male":
        b = 10 * weights[i] + 6.25 * heights[i] - 5 * ages[i] + 5
    else:
        b = 10 * weights[i] + 6.25 * heights[i] - 5 * ages[i] - 161
    bmr.append(round(b, 1))

activity_multipliers = {
    "Sedentary": 1.2, "Light": 1.375,
    "Moderate": 1.55, "Active": 1.725, "Very Active": 1.9
}

tdee = [round(bmr[i] * activity_multipliers[activity_levels[i]], 1) for i in range(N)]

goal_calorie_adjustments = {
    "Weight Loss": -400, "Weight Gain": 400,
    "Muscle Gain": 300, "Maintain Fitness": 0, "Improve Stamina": 100
}

calorie_targets = [
    max(1200, min(4000, tdee[i] + goal_calorie_adjustments[goals[i]])) for i in range(N)
]

# BMI Categories
def bmi_category(b):
    if b < 18.5: return "Underweight"
    elif b < 25: return "Normal"
    elif b < 30: return "Overweight"
    else: return "Obese"

bmi_cats = [bmi_category(b) for b in bmi]

# Diet Plan Category
def diet_plan(goal, bmi_cat, diet_pref):
    if goal == "Weight Loss":
        return "Low Calorie Balanced Diet"
    elif goal == "Weight Gain" or goal == "Muscle Gain":
        if diet_pref in ["Non-Vegetarian", "Eggetarian"]:
            return "High Protein Non-Veg Diet"
        else:
            return "High Protein Veg Diet"
    elif goal == "Improve Stamina":
        return "High Carb Performance Diet"
    else:
        if bmi_cat in ["Overweight", "Obese"]:
            return "Low Calorie Balanced Diet"
        return "Balanced Maintenance Diet"

diet_plans = [diet_plan(goals[i], bmi_cats[i], diet_prefs[i]) for i in range(N)]

# Workout Plan Category
def workout_plan(goal, activity, age):
    if goal == "Weight Loss":
        if activity in ["Sedentary", "Light"]:
            return "Beginner Cardio + Walking"
        return "Intermediate Cardio + HIIT"
    elif goal == "Muscle Gain":
        if age > 45:
            return "Moderate Strength Training"
        return "Progressive Strength Training"
    elif goal == "Weight Gain":
        return "Compound Strength Training"
    elif goal == "Improve Stamina":
        return "Cardio Endurance Training"
    else:
        if activity in ["Sedentary", "Light"]:
            return "Beginner Fitness Routine"
        return "Active Lifestyle Routine"

workout_plans = [workout_plan(goals[i], activity_levels[i], ages[i]) for i in range(N)]

# Fitness Category (label for ML)
def fitness_category(bmi_cat, activity, age):
    if bmi_cat == "Normal" and activity in ["Active", "Very Active"] and age < 45:
        return "Fit"
    elif bmi_cat in ["Overweight", "Obese"] or activity == "Sedentary":
        return "Needs Improvement"
    else:
        return "Moderately Fit"

fitness_cats = [fitness_category(bmi_cats[i], activity_levels[i], ages[i]) for i in range(N)]

df = pd.DataFrame({
    "age": ages, "gender": genders,
    "height_cm": heights, "weight_kg": weights,
    "bmi": bmi, "bmi_category": bmi_cats,
    "activity_level": activity_levels,
    "goal": goals, "diet_preference": diet_prefs,
    "bmr": bmr, "tdee": tdee,
    "calorie_target": calorie_targets,
    "diet_plan": diet_plans,
    "workout_plan": workout_plans,
    "fitness_category": fitness_cats
})

df.to_csv("data/fitness_diet_dataset.csv", index=False)
print(f"✅ Dataset saved: {len(df)} rows, {len(df.columns)} columns")
print(df["fitness_category"].value_counts())
print(df["diet_plan"].value_counts())
