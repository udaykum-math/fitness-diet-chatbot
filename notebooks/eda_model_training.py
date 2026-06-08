"""
eda_model_training.py – Exploratory Data Analysis + full ML training pipeline.
This mirrors what would be in a Jupyter notebook (for your CV / GitHub).
Run: python notebooks/eda_model_training.py
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    classification_report, accuracy_score, confusion_matrix, ConfusionMatrixDisplay
)

os.makedirs("static", exist_ok=True)

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv("data/fitness_diet_dataset.csv")
print(f"Dataset Shape: {df.shape}")
print(df.dtypes)
print(df.describe())
print("\nMissing Values:\n", df.isnull().sum())

# ── EDA Plots ─────────────────────────────────────────────────────────────────
sns.set_theme(style="darkgrid", palette="muted")
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle("Fitness Dataset – EDA Overview", fontsize=16, fontweight="bold")

# BMI Distribution
axes[0][0].hist(df["bmi"], bins=30, color="#e040fb", edgecolor="black", alpha=0.8)
axes[0][0].set_title("BMI Distribution")
axes[0][0].set_xlabel("BMI")

# Age Distribution
axes[0][1].hist(df["age"], bins=20, color="#7c4dff", edgecolor="black", alpha=0.8)
axes[0][1].set_title("Age Distribution")

# Fitness Category counts
df["fitness_category"].value_counts().plot(kind="bar", ax=axes[0][2], color=["#e040fb","#7c4dff","#40c4ff"])
axes[0][2].set_title("Fitness Category Counts")
axes[0][2].tick_params(axis="x", rotation=15)

# Goal distribution
df["goal"].value_counts().plot(kind="barh", ax=axes[1][0], color="#e040fb")
axes[1][0].set_title("Fitness Goals")

# Activity Level
df["activity_level"].value_counts().plot(kind="pie", ax=axes[1][1], autopct="%1.1f%%")
axes[1][1].set_title("Activity Levels")

# BMI vs Calorie Target scatter
axes[1][2].scatter(df["bmi"], df["calorie_target"], alpha=0.3, c=df["bmi"], cmap="plasma")
axes[1][2].set_title("BMI vs Calorie Target")
axes[1][2].set_xlabel("BMI")
axes[1][2].set_ylabel("Calorie Target")

plt.tight_layout()
plt.savefig("static/eda_overview.png", dpi=120, bbox_inches="tight")
plt.close()
print("✅ EDA plot saved → static/eda_overview.png")

# ── ML Encoding ──────────────────────────────────────────────────────────────
cat_cols = ["gender", "activity_level", "goal", "diet_preference",
            "bmi_category", "fitness_category"]
encoders = {}
df_enc = df.copy()
for col in cat_cols:
    le = LabelEncoder()
    df_enc[col + "_enc"] = le.fit_transform(df[col])
    encoders[col] = le

feature_cols = ["age","gender_enc","height_cm","weight_kg","bmi",
                "activity_level_enc","goal_enc","diet_preference_enc",
                "bmr","tdee","calorie_target"]
X = df_enc[feature_cols]
y = df_enc["fitness_category_enc"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# ── Model Comparison ──────────────────────────────────────────────────────────
models = {
    "Random Forest":      RandomForestClassifier(n_estimators=100, random_state=42),
    "Decision Tree":      DecisionTreeClassifier(max_depth=8, random_state=42),
    "Logistic Regression":LogisticRegression(max_iter=500, random_state=42),
}

results = {}
for name, clf in models.items():
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    cv  = cross_val_score(clf, X, y, cv=5).mean()
    results[name] = {"accuracy": acc, "cv_score": cv, "model": clf, "preds": y_pred}
    print(f"\n{name}  →  Accuracy: {acc:.4f}  |  5-Fold CV: {cv:.4f}")
    print(classification_report(y_test, y_pred, target_names=encoders["fitness_category"].classes_))

# ── Comparison Plot ───────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("ML Model Comparison – Fitness Category", fontsize=14, fontweight="bold")

names   = list(results.keys())
accs    = [results[n]["accuracy"] for n in names]
cv_scores = [results[n]["cv_score"] for n in names]
colors  = ["#e040fb", "#7c4dff", "#40c4ff"]

axes[0].bar(names, accs, color=colors)
axes[0].set_ylim(0.6, 1.05)
axes[0].set_title("Test Accuracy")
axes[0].tick_params(axis="x", rotation=10)
for i, v in enumerate(accs):
    axes[0].text(i, v + 0.005, f"{v:.4f}", ha="center", fontsize=10)

axes[1].bar(names, cv_scores, color=colors)
axes[1].set_ylim(0.6, 1.05)
axes[1].set_title("5-Fold CV Score")
axes[1].tick_params(axis="x", rotation=10)
for i, v in enumerate(cv_scores):
    axes[1].text(i, v + 0.005, f"{v:.4f}", ha="center", fontsize=10)

best_clf = results["Random Forest"]["model"]
cm = confusion_matrix(y_test, best_clf.predict(X_test))
disp = ConfusionMatrixDisplay(cm, display_labels=encoders["fitness_category"].classes_)
disp.plot(ax=axes[2], colorbar=False, cmap="Purples")
axes[2].set_title("Random Forest – Confusion Matrix")

plt.tight_layout()
plt.savefig("static/model_comparison.png", dpi=120, bbox_inches="tight")
plt.close()
print("\n✅ Model comparison plot saved → static/model_comparison.png")

# Feature importance
fi = pd.DataFrame({"feature": feature_cols, "importance": best_clf.feature_importances_})
fi = fi.sort_values("importance", ascending=True)
fig, ax = plt.subplots(figsize=(8, 6))
ax.barh(fi["feature"], fi["importance"], color="#e040fb")
ax.set_title("Feature Importance – Random Forest")
plt.tight_layout()
plt.savefig("static/feature_importance.png", dpi=120, bbox_inches="tight")
plt.close()
print("✅ Feature importance plot saved → static/feature_importance.png")
print("\n✅ All EDA + ML analysis complete.")
