"""
utils.py – BMI, BMR, TDEE, and calorie target calculations.
"""

ACTIVITY_MULTIPLIERS = {
    "Sedentary":   1.2,
    "Light":       1.375,
    "Moderate":    1.55,
    "Active":      1.725,
    "Very Active": 1.9,
}

GOAL_ADJUSTMENTS = {
    "Weight Loss":      -400,
    "Weight Gain":       400,
    "Muscle Gain":       300,
    "Maintain Fitness":    0,
    "Improve Stamina":   100,
}


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    h_m = height_cm / 100
    return round(weight_kg / (h_m ** 2), 2)


def bmi_category(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25.0:
        return "Normal"
    elif bmi < 30.0:
        return "Overweight"
    else:
        return "Obese"


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """Mifflin-St Jeor equation."""
    if gender == "Male":
        return round(10 * weight_kg + 6.25 * height_cm - 5 * age + 5, 1)
    else:
        return round(10 * weight_kg + 6.25 * height_cm - 5 * age - 161, 1)


def calculate_tdee(bmr: float, activity_level: str) -> float:
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
    return round(bmr * multiplier, 1)


def calculate_calorie_target(tdee: float, goal: str) -> float:
    adjustment = GOAL_ADJUSTMENTS.get(goal, 0)
    return max(1200, min(4000, round(tdee + adjustment, 1)))


def full_calculation(age, gender, height_cm, weight_kg, activity_level, goal):
    bmi  = calculate_bmi(weight_kg, height_cm)
    cat  = bmi_category(bmi)
    bmr  = calculate_bmr(weight_kg, height_cm, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    cal  = calculate_calorie_target(tdee, goal)
    return {
        "bmi": bmi,
        "bmi_category": cat,
        "bmr": bmr,
        "tdee": tdee,
        "calorie_target": cal,
    }
