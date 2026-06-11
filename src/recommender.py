"""
recommender.py  –  Loads trained models and returns predictions.
Works with the REAL Kaggle dataset feature set.

IMPORTANT FIX: The Kaggle gym dataset had no diet_preference column,
so the ML model cannot learn it. We apply a hard override AFTER prediction
to ensure Vegetarian / Vegan / Eggetarian users NEVER get a Non-Veg diet plan.
"""

import joblib
import pandas as pd
import os

_BASE      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MODEL_DIR = os.path.join(_BASE, "models")

_fitness_model = _diet_model = _workout_model = _encoders = _feature_cols = None


def _load(fn):
    return joblib.load(os.path.join(_MODEL_DIR, fn))


def _init():
    global _fitness_model, _diet_model, _workout_model, _encoders, _feature_cols
    if _encoders is None:
        _encoders       = _load("label_encoders.pkl")
        _fitness_model  = _load("fitness_category_model.pkl")
        _diet_model     = _load("diet_plan_model.pkl")
        _workout_model  = _load("workout_plan_model.pkl")
        _feature_cols   = _load("feature_cols.pkl")


def _enc(col, val):
    le  = _encoders[col]
    val = val if val in le.classes_ else le.classes_[0]
    return int(le.transform([val])[0])


def _fix_diet_plan(ml_plan, diet_pref, bmi, fat_pct, tdee):
    """
    Hard rule: diet_preference always overrides the ML prediction.
    Vegetarian / Vegan / Eggetarian must NEVER receive a Non-Veg plan.
    """
    NON_VEG = "High Protein Non-Veg Diet"

    if diet_pref in ("Vegetarian", "Vegan", "Eggetarian"):
        if ml_plan == NON_VEG:
            # Replace with best veg alternative based on body stats
            if bmi > 27 or fat_pct > 25:
                return "Low Calorie Balanced Diet"
            elif tdee > 2800:
                return "High Carb Performance Diet"
            else:
                return "High Protein Veg Diet"

    # Non-Vegetarian → ML prediction is always fine
    return ml_plan


def predict(
    age, gender, weight_kg, height_m,
    bmi, bmi_category,
    max_bpm, avg_bpm, resting_bpm,
    session_duration_h, calories_burned,
    fat_pct, water_intake_l,
    workout_freq, workout_type, experience_level,
    bmr, tdee,
    diet_preference="Non-Vegetarian",   # ← new param, safe default
):
    _init()

    row = {
        "age":               age,
        "gender_enc":        _enc("gender", gender),
        "weight_kg":         weight_kg,
        "height_m":          height_m,
        "bmi":               bmi,
        "bmi_category_enc":  _enc("bmi_category", bmi_category),
        "max_bpm":           max_bpm,
        "avg_bpm":           avg_bpm,
        "resting_bpm":       resting_bpm,
        "session_duration_h":session_duration_h,
        "calories_burned":   calories_burned,
        "fat_pct":           fat_pct,
        "water_intake_l":    water_intake_l,
        "workout_freq":      workout_freq,
        "workout_type_enc":  _enc("workout_type", workout_type),
        "experience_level":  experience_level,
        "bmr":               bmr,
        "tdee":              tdee,
    }

    X = pd.DataFrame([row])[_feature_cols]

    fc_enc = _fitness_model.predict(X)[0]
    dp_enc = _diet_model.predict(X)[0]
    wp_enc = _workout_model.predict(X)[0]

    ml_diet_plan = _encoders["diet_plan"].inverse_transform([dp_enc])[0]

    # ── Apply hard diet preference override ───────────────────────────────────
    final_diet_plan = _fix_diet_plan(ml_diet_plan, diet_preference, bmi, fat_pct, tdee)

    return {
        "fitness_category": _encoders["fitness_category"].inverse_transform([fc_enc])[0],
        "diet_plan":        final_diet_plan,
        "workout_plan":     _encoders["workout_plan"].inverse_transform([wp_enc])[0],
    }