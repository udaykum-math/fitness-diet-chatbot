"""
train_model.py  –  ML training on REAL Kaggle dataset.
Trains Random Forest, Decision Tree, Logistic Regression for:
  - fitness_category
  - diet_plan
  - workout_plan
Run:  python src/train_model.py
"""

import pandas as pd
import numpy as np
import joblib, os, sys
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, accuracy_score

os.makedirs("models", exist_ok=True)

print("=" * 62)
print("🏋️  FITBOT  –  ML TRAINING ON REAL KAGGLE DATASET")
print("=" * 62)

df = pd.read_csv("data/kaggle_fitness_clean.csv")
print(f"\n✅ Kaggle dataset loaded: {df.shape[0]} rows × {df.shape[1]} cols\n")

# ── Encode categoricals ───────────────────────────────────────────────────────
cat_cols = [
    "gender", "bmi_category", "workout_type",
    "fitness_category", "diet_plan", "workout_plan", "inferred_goal"
]
encoders = {}
for col in cat_cols:
    le = LabelEncoder()
    df[col + "_enc"] = le.fit_transform(df[col])
    encoders[col] = le

joblib.dump(encoders, "models/label_encoders.pkl")
print("✅ Label encoders saved → models/label_encoders.pkl")

# ── Feature set (uses REAL Kaggle columns) ─────────────────────────────────────
FEATURE_COLS = [
    "age", "gender_enc", "weight_kg", "height_m",
    "bmi", "bmi_category_enc",
    "max_bpm", "avg_bpm", "resting_bpm",
    "session_duration_h", "calories_burned",
    "fat_pct", "water_intake_l",
    "workout_freq", "workout_type_enc", "experience_level",
    "bmr", "tdee",
]

X = df[FEATURE_COLS]

TARGETS = {
    "fitness_category": "fitness_category_enc",
    "diet_plan":        "diet_plan_enc",
    "workout_plan":     "workout_plan_enc",
}

summary = {}
for target_name, target_col in TARGETS.items():
    print(f"\n{'─'*45}")
    print(f"  🎯  Target: {target_name.upper()}")
    print(f"{'─'*45}")

    y = df[target_col]
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    candidates = {
        "Random Forest":       RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1),
        "Decision Tree":       DecisionTreeClassifier(max_depth=10, random_state=42),
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    }

    best_model, best_acc, best_name = None, 0, ""
    for name, clf in candidates.items():
        clf.fit(X_tr, y_tr)
        acc = accuracy_score(y_te, clf.predict(X_te))
        cv  = cross_val_score(clf, X, y, cv=5).mean()
        print(f"  {name:<25}  Test Acc: {acc:.4f}   CV: {cv:.4f}")
        if acc > best_acc:
            best_acc, best_model, best_name = acc, clf, name

    print(f"\n  ✅ Best: {best_name}  ({best_acc:.4f})")
    print(classification_report(
        y_te, best_model.predict(X_te),
        target_names=encoders[target_name].classes_
    ))

    save_path = f"models/{target_name}_model.pkl"
    joblib.dump(best_model, save_path)
    summary[target_name] = (best_name, best_acc)
    print(f"  💾 Saved → {save_path}")

# ── Feature Importance ────────────────────────────────────────────────────────
best_rf = joblib.load("models/fitness_category_model.pkl")
if hasattr(best_rf, "feature_importances_"):
    fi = pd.DataFrame({"feature": FEATURE_COLS, "importance": best_rf.feature_importances_})
    fi = fi.sort_values("importance", ascending=False).head(10)
    fi.to_csv("models/feature_importance.csv", index=False)
    print("\n📊 Top-10 Feature Importances (Fitness Category):")
    print(fi.to_string(index=False))

# Save the feature column list (needed by recommender)
joblib.dump(FEATURE_COLS, "models/feature_cols.pkl")

print("\n" + "=" * 62)
print("✅  ALL MODELS TRAINED AND SAVED")
for t, (m, a) in summary.items():
    print(f"   {t:<25}  {m:<25}  Acc={a:.4f}")
print("=" * 62)
