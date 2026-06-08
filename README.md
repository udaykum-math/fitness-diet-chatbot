# 🏋️ FitBot – AI-Powered Fitness & Diet Recommendation Chatbot

> **A complete ML + NLP end-to-end project for CV, internship preparation, and real-world deployment.**

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red) ![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.3+-orange) ![License](https://img.shields.io/badge/License-MIT-green)

---

## 📌 Project Overview

FitBot is a personalized fitness and diet recommendation system that:
- Collects user profile (age, gender, height, weight, activity level, goal, diet preference)
- Calculates BMI, BMR, TDEE, and daily calorie targets
- Uses trained ML models to recommend diet plans, workout plans, and fitness categories
- Provides an interactive chatbot with intent-based NLP responses
- Generates Indian-style meal plans and beginner-friendly workout schedules
- Tracks user progress with a weekly log

---

## 🗂️ Project Structure

```
fitness-diet-chatbot/
├── data/
│   ├── generate_dataset.py        # Dataset generator (2000 samples)
│   └── fitness_diet_dataset.csv   # Generated dataset
├── notebooks/
│   └── eda_model_training.py      # EDA + model training + evaluation
├── src/
│   ├── utils.py                   # BMI, BMR, TDEE calculators
│   ├── recommender.py             # ML model loader + predictor
│   └── planner.py                 # Indian meal + workout plans
├── models/
│   ├── fitness_category_model.pkl
│   ├── diet_plan_model.pkl
│   ├── workout_plan_model.pkl
│   ├── label_encoders.pkl
│   └── feature_importance.csv
├── static/
│   ├── eda_overview.png
│   ├── model_comparison.png
│   └── feature_importance.png
├── app.py                         # Main Streamlit application
├── requirements.txt
├── .streamlit/config.toml         # Streamlit theme config
└── README.md
```

---

## ⚙️ Setup & Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/fitness-diet-chatbot.git
cd fitness-diet-chatbot

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Generate dataset
python data/generate_dataset.py

# 5. Train ML models
python src/train_model.py

# 6. (Optional) Run EDA analysis
python notebooks/eda_model_training.py

# 7. Launch the app
streamlit run app.py
```

---

## 🤖 ML Models

| Target Variable     | Best Model    | Accuracy |
|---------------------|---------------|----------|
| Fitness Category    | Decision Tree | 100%     |
| Diet Plan           | Decision Tree | 100%     |
| Workout Plan        | Random Forest | 100%     |

**Features used:** Age, Gender, Height, Weight, BMI, Activity Level, Goal, Diet Preference, BMR, TDEE, Calorie Target

**Algorithms compared:** Random Forest, Decision Tree, Logistic Regression

---

## 🍽️ Diet Plans Covered

| Plan | For |
|------|-----|
| Low Calorie Balanced Diet | Weight Loss |
| High Protein Non-Veg Diet | Muscle Gain (non-veg) |
| High Protein Veg Diet | Muscle Gain (veg/vegan) |
| Balanced Maintenance Diet | Maintain Fitness |
| High Carb Performance Diet | Improve Stamina |

---

## 💪 Workout Plans Covered

- Beginner Cardio + Walking
- Intermediate Cardio + HIIT
- Progressive Strength Training
- Compound Strength Training
- Cardio Endurance Training
- Active Lifestyle Routine
- Moderate Strength Training
- Beginner Fitness Routine

---

## 🚀 Deploy to Streamlit Community Cloud (Free)

1. Push your code to a **public GitHub repo**
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New App** → select your repo → set main file as `app.py`
4. Click **Deploy** — your app is live in minutes!

> **Important:** Make sure `data/fitness_diet_dataset.csv` and all `models/*.pkl` files are committed to GitHub before deploying.

---

## 📄 CV / Resume Section

**Project Title:** AI-Powered Fitness and Diet Recommendation Chatbot using Machine Learning and NLP

**Description:**
> Built an end-to-end ML-based wellness recommendation system that generates personalized diet and workout plans based on BMI, BMR, activity level, and fitness goals. Integrated a conversational chatbot with intent-based NLP to collect user inputs and answer fitness queries. Trained and compared Logistic Regression, Decision Tree, and Random Forest models. Deployed using Streamlit with a production-grade dark-theme UI.

**Bullet Points:**
- Developed an AI-powered fitness chatbot using Python, Scikit-learn, and Streamlit with a fully responsive dark-theme UI
- Engineered features from user inputs (BMI, BMR, TDEE) and trained ML models achieving 100% accuracy on 2000-sample dataset
- Implemented intent-based NLP chatbot covering 10+ fitness query categories including diet, workout, hydration, and sleep
- Built Indian-style meal planner with 5 diet categories and 8 workout plan types tailored to user goals
- Deployed to Streamlit Community Cloud with complete GitHub documentation, EDA plots, and confusion matrix analysis

---

## ⚠️ Disclaimer

This application is for **general wellness and educational purposes only**. It is not a substitute for professional medical, nutritional, or fitness advice. Always consult a qualified professional before starting any new diet or exercise program.

---

## 📜 License

MIT License – free to use, modify, and distribute with attribution.
