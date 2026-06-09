"""
app.py  –  FitBot Streamlit App  (Kaggle dataset version)
Run:  streamlit run app.py
"""

import sys, os, re, html
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import streamlit as st
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from utils import calculate_bmi, bmi_category, calculate_bmr, calculate_tdee
from recommender import predict
from planner import get_meal_plan, get_workout_plan


def format_bot_text(text: str) -> str:
    """Convert simple markdown-style bot text to safe HTML for custom chat bubbles."""
    text = html.escape(str(text))
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    text = text.replace("\n", "<br>")
    return text


def format_user_text(text: str) -> str:
    """Escape user text before putting it inside unsafe_allow_html markup."""
    return html.escape(str(text)).replace("\n", "<br>")


# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FitBot – AI Fitness & Diet Chatbot",
    page_icon="🏋️", layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=DM+Mono:ital,wght@0,400;0,500;1,400&display=swap');

html,body,[class*="css"]{ font-family:'Space Grotesk',sans-serif; }
.stApp{ background:linear-gradient(135deg,#0b0b12 0%,#0f0f1e 100%); }

.hero{ text-align:center; padding:28px 0 6px; }
.hero h1{ font-size:44px; font-weight:700;
  background:linear-gradient(90deg,#e040fb,#7c4dff,#40c4ff);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.hero p{ color:#7070a0; font-size:15px; margin-top:4px; }

.metric-card{
  background:linear-gradient(135deg,#141428,#111130);
  border:1px solid #252550; border-radius:16px;
  padding:20px 16px; text-align:center; margin:6px 0;
}
.metric-title{ color:#6868a0; font-size:11px; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:8px; }
.metric-value{ color:#e040fb; font-size:30px; font-weight:700; font-family:'DM Mono',monospace; }
.metric-sub{ color:#9090c0; font-size:12px; margin-top:4px; }

.chat-user{
  background:linear-gradient(135deg,#1a3060,#162540);
  border:1px solid #2a4a80; border-radius:16px 16px 4px 16px;
  padding:12px 16px; margin:8px 0 8px auto; max-width:76%;
  color:#c0d0f0; font-size:14px; line-height:1.6;
}
.chat-bot{
  background:linear-gradient(135deg,#141428,#111130);
  border:1px solid #252550; border-radius:16px 16px 16px 4px;
  padding:12px 16px; margin:8px auto 8px 0; max-width:86%;
  color:#d0d0f0; font-size:14px; line-height:1.6;
}
.chat-lbl-u{ color:#5070a0; font-size:11px; text-align:right; margin-bottom:2px; }
.chat-lbl-b{ color:#5050a0; font-size:11px; margin-bottom:2px; }

.plan-card{
  background:linear-gradient(135deg,#111128,#0f0f25);
  border:1px solid #222248; border-radius:14px;
  padding:18px; margin:10px 0;
}
.plan-header{ color:#e040fb; font-size:15px; font-weight:600; margin-bottom:10px; }
.plan-item{ color:#a0a0c8; font-size:13px; padding:5px 0; border-bottom:1px solid #1a1a38; }
.plan-note{ color:#7070a0; font-size:12px; font-style:italic; margin-top:10px; }

.sec-hdr{ color:#e040fb; font-size:21px; font-weight:700;
  margin:20px 0 10px; padding-bottom:8px; border-bottom:2px solid #222248; }

.badge-fit      { background:#183028; color:#30d090; border:1px solid #28b070;
  padding:5px 14px; border-radius:20px; font-size:13px; font-weight:600; display:inline-block; }
.badge-moderate { background:#282818; color:#d0b030; border:1px solid #b09028;
  padding:5px 14px; border-radius:20px; font-size:13px; font-weight:600; display:inline-block; }
.badge-needs    { background:#301818; color:#d04040; border:1px solid #b02828;
  padding:5px 14px; border-radius:20px; font-size:13px; font-weight:600; display:inline-block; }

.log-row{
  display:flex; justify-content:space-between; align-items:center;
  padding:6px 0; border-bottom:1px solid #1a1a38;
  color:#9090b8; font-size:13px; font-family:'DM Mono',monospace;
}

section[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#0a0a18 0%,#0d0d20 100%);
  border-right:1px solid #1e1e40;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
for k, v in {
    "chat_history": [], "profile": None, "stats": None,
    "prediction": None, "progress_log": [],
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar: profile form ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏋️ FitBot")
    st.markdown("##### Kaggle-Powered AI Fitness Advisor")
    st.markdown("---")
    st.markdown("### 📋 Your Profile")

    age     = st.number_input("Age",         18, 80,  25)
    gender  = st.selectbox("Gender",         ["Male", "Female"])
    height  = st.number_input("Height (cm)", 140.0, 210.0, 170.0, step=0.5)
    weight  = st.number_input("Weight (kg)",  30.0, 150.0,  70.0, step=0.5)

    st.markdown("#### 🎯 Goal & Diet Preference")
    goal = st.selectbox("Fitness Goal", ["Fat Loss", "Muscle Gain", "Maintain Fitness"])
    diet_pref = st.selectbox("Diet Preference", ["Vegetarian", "Non-Vegetarian", "Vegan", "Eggetarian"])

    st.markdown("#### 🏃 Activity Profile")
    workout_type  = st.selectbox("Workout Type", ["Cardio", "Strength", "HIIT", "Yoga"])
    workout_freq  = st.slider("Workout Days/Week", 1, 7, 3)
    experience    = st.selectbox("Experience Level", ["Beginner (1)", "Intermediate (2)", "Expert (3)"])
    exp_num       = int(experience.split("(")[1].replace(")", ""))

    st.markdown("#### 💓 Heart Rate (optional)")
    max_bpm     = st.number_input("Max BPM",     100, 220, 175)
    avg_bpm     = st.number_input("Avg BPM",      80, 200, 140)
    resting_bpm = st.number_input("Resting BPM",  40,  90,  60)

    st.markdown("#### 💧 Daily Habits")
    water_intake   = st.number_input("Water Intake (L)",    1.0, 5.0, 2.5, step=0.1)
    session_dur    = st.number_input("Session Duration (h)", 0.25, 3.0, 1.0, step=0.25)
    fat_pct        = st.number_input("Body Fat % (approx)", 5.0, 50.0, 20.0, step=0.5)

    if st.button("🚀 Generate My Plan", use_container_width=True):
        h_m        = height / 100
        bmi_val    = calculate_bmi(weight, height)
        bmi_cat_v  = bmi_category(bmi_val)
        bmr_val    = calculate_bmr(weight, height, age, gender)
        activity_level = ["Sedentary", "Light", "Moderate", "Active", "Very Active", "Very Active", "Very Active"][workout_freq - 1]
        tdee_val   = calculate_tdee(bmr_val, activity_level)
        cal_burned = round(session_dur * avg_bpm * 0.5, 1)   # simple estimate

        pred = predict(
            age=age, gender=gender, weight_kg=weight, height_m=h_m,
            bmi=bmi_val, bmi_category=bmi_cat_v,
            max_bpm=max_bpm, avg_bpm=avg_bpm, resting_bpm=resting_bpm,
            session_duration_h=session_dur, calories_burned=cal_burned,
            fat_pct=fat_pct, water_intake_l=water_intake,
            workout_freq=workout_freq, workout_type=workout_type,
            experience_level=exp_num,
            bmr=bmr_val, tdee=tdee_val,
        )

        st.session_state.profile = dict(
            age=age, gender=gender, height=height, weight=weight,
            goal=goal, diet_pref=diet_pref, activity=activity_level,
            workout_type=workout_type, workout_freq=workout_freq,
            experience=exp_num, max_bpm=max_bpm, avg_bpm=avg_bpm,
            resting_bpm=resting_bpm, water_intake=water_intake,
            session_dur=session_dur, fat_pct=fat_pct,
        )
        st.session_state.stats = dict(
            bmi=bmi_val, bmi_category=bmi_cat_v,
            bmr=bmr_val, tdee=tdee_val, cal_burned=cal_burned,
        )
        st.session_state.prediction = pred
        st.session_state.chat_history = [{
            "role": "bot",
            "text": (
                f"👋 Hey! I've analysed your data. Here's your snapshot:\n\n"
                f"**BMI:** {bmi_val} ({bmi_cat_v})\n"
                f"**TDEE:** {int(tdee_val)} kcal/day\n"
                f"**Goal:** {goal}\n"
                f"**Diet Preference:** {diet_pref}\n"
                f"**Fitness Category:** {pred['fitness_category']}\n"
                f"**Diet Plan:** {pred['diet_plan']}\n"
                f"**Workout Plan:** {pred['workout_plan']}\n\n"
                f"Explore the tabs below 👇 or ask me anything!"
            )
        }]

    st.markdown("---")
    st.markdown("### 📈 Log Today")
    lw = st.number_input(
        "Weight (kg)", 30.0, 150.0,
        st.session_state.profile["weight"] if st.session_state.profile else 70.0,
        key="lw"
    )
    lc  = st.number_input("Calories eaten", 0, 6000, 1800, key="lc")
    lwo = st.selectbox("Workout done?", ["Yes", "No"], key="lwo")
    if st.button("📝 Log Entry", use_container_width=True):
        st.session_state.progress_log.append({
            "date": datetime.now().strftime("%d %b %Y"),
            "weight": lw, "calories": lc, "workout": lwo
        })
        st.success("Logged ✅")

# ── Main content ───────────────────────────────────────────────────────────────
st.markdown("""<div class='hero'>
  <h1>🏋️ FitBot</h1>
  <p>AI-Powered Fitness & Diet Advisor — trained on real Kaggle gym data</p>
</div>""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["💬 Chatbot", "📊 Dashboard", "🍽️ Meal Plan", "💪 Workout Plan"])

# ── TAB 1 : CHATBOT ────────────────────────────────────────────────────────────
with tab1:
    if not st.session_state.chat_history:
        st.markdown("""<div class='plan-card' style='text-align:center;padding:40px;'>
          <div style='font-size:48px'>🤖</div>
          <div style='color:#6060a0;font-size:15px;margin-top:12px'>
            Fill your profile in the sidebar and click
            <strong style='color:#e040fb'>Generate My Plan</strong><br>
            Then chat with your AI fitness advisor here!
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(
                    f"<div class='chat-lbl-u'>You</div>"
                    f"<div class='chat-user'>{format_user_text(msg['text'])}</div>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"<div class='chat-lbl-b'>🤖 FitBot</div>"
                    f"<div class='chat-bot'>{format_bot_text(msg['text'])}</div>",
                    unsafe_allow_html=True
                )

        user_input = st.chat_input("Ask FitBot anything — food preferences, workout tips, regional cuisine…")
        if user_input:
            st.session_state.chat_history.append({"role": "user", "text": user_input})

            p    = st.session_state.profile
            s    = st.session_state.stats
            r    = st.session_state.prediction
            meal = get_meal_plan(r["diet_plan"])
            wo   = get_workout_plan(r["workout_plan"])

            system_prompt = f"""
You are FitBot, an AI fitness and diet recommendation assistant inside a Streamlit ML project.

Your job:
Give personalized fitness and diet suggestions using the user's profile, BMI, BMR, TDEE, ML-predicted fitness category, diet plan, and workout plan.

Response rules:
1. Always use the user's data when answering.
2. Keep answers practical, specific, and Indian-user friendly.
3. Use simple language.
4. Do not give medical diagnosis.
5. Do not suggest extreme dieting, crash diets, fat burners, or unsafe workouts.
6. If the user is vegetarian, do NOT suggest egg, chicken, fish, or meat.
7. If the user is vegan, do NOT suggest milk, paneer, curd, ghee, egg, or honey.
8. For beginner workouts, avoid burpees, mountain climbers, heavy weights, or high-impact exercises unless the user asks.
9. Do not repeat the same meal plan again and again.
10. Do not end every answer with “How does that sound?”.
11. Keep the answer around 6-10 lines unless the user asks for a detailed plan.
12. Do not give exact protein grams unless portion size is clearly mentioned. Use approximate words like "good protein source" or "high-protein option".
13. Avoid suggesting very heavy foods like dal makhani or biryani for breakfast unless the user specifically asks for heavy meals.
14. For snacks, suggest light options like sprouts chaat, roasted chana, curd, buttermilk, or fruit salad instead of heavy options like samosas or pakoras.
15. Use practical Indian foods like dal, roti, paneer, curd, milk, sprouts, besan chilla, poha, upma, daliya, roasted chana, rajma, chole, soybean, tofu, rice, and sabzi.
16. For non-vegetarian Indian users, include eggs, chicken, fish, and lean meats as good protein sources.
17. Include a short safety note only when needed.

USER PROFILE:
- Age: {p.get("age")}
- Gender: {p.get("gender")}
- Height: {p.get("height")} cm
- Weight: {p.get("weight")} kg
- Goal: {p.get("goal")}
- Diet Preference: {p.get("diet_pref")}
- Activity Level: {p.get("activity")}
- BMI: {s.get("bmi")} ({s.get("bmi_category")})
- Body Fat: {p.get("fat_pct", "N/A")}%
- Workout Type: {p.get("workout_type")}
- Workout Frequency: {p.get("workout_freq", "N/A")} days/week
- Experience Level: {p.get("experience")}
- Resting BPM: {p.get("resting_bpm", "N/A")}
- Avg BPM: {p.get("avg_bpm", "N/A")}
- Max BPM: {p.get("max_bpm", "N/A")}
- Water Intake: {p.get("water_intake", "N/A")} L/day

ML RECOMMENDATIONS:
- Fitness Category: {r.get("fitness_category")}
- Diet Plan: {r.get("diet_plan")}
- Workout Plan: {r.get("workout_plan")}

CURRENT MEAL PLAN:
- Breakfast: {" | ".join(meal.get("breakfast", []))}
- Lunch: {" | ".join(meal.get("lunch", []))}
- Dinner: {" | ".join(meal.get("dinner", []))}
- Snacks: {" | ".join(meal.get("snacks", []))}
- Notes: {meal.get("notes", "")}

CURRENT WORKOUT:
{" | ".join(wo.get("weekly", []))}
Coach notes: {wo.get("notes", "")}

CALORIE STATS:
- BMR: {int(s.get("bmr", 0))} kcal/day
- TDEE: {int(s.get("tdee", 0))} kcal/day

Answer format:
Start with: "Based on your profile..."
Then give clear bullet points.
"""

            messages = []
            for old_msg in st.session_state.chat_history[:-1]:
                role = "user" if old_msg["role"] == "user" else "assistant"
                messages.append({"role": role, "content": old_msg["text"]})
            messages.append({"role": "user", "content": user_input})

            try:
                from groq import Groq

                groq_api_key = os.getenv("GROQ_API_KEY")
                if not groq_api_key:
                    raise ValueError("GROQ_API_KEY is missing. Set it in terminal or in a .env file.")

                client = Groq(api_key=groq_api_key)

                groq_messages = [{"role": "system", "content": system_prompt}]
                groq_messages.extend(messages)

                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=groq_messages,
                    temperature=0.4,
                    max_tokens=650,
                )

                reply = response.choices[0].message.content

            except ImportError:
                reply = ("⚠️ groq package not installed.\n\n"
                         "Run: `pip install groq`\n"
                         "then restart the app.")
            except Exception as e:
                err = str(e)
                if any(k in err.lower() for k in ["api_key", "authentication", "auth", "invalid api key", "gsk", "missing"]):
                    reply = ("🔑 **Groq API key missing or invalid.**\n\n"
                             "**Steps to fix:**\n"
                             "1. Get your key from **https://console.groq.com/keys**\n"
                             "2. In PowerShell terminal run: `$env:GROQ_API_KEY=\"gsk_your_new_key_here\"`\n"
                             "3. Restart app: `streamlit run app.py`")
                else:
                    reply = f"⚠️ Error: {err[:200]}"

            st.session_state.chat_history.append({"role": "bot", "text": reply})
            st.rerun()

# ── TAB 2 : DASHBOARD ──────────────────────────────────────────────────────────
with tab2:
    if not st.session_state.stats:
        st.info("Fill your profile and click **Generate My Plan** to see your dashboard.")
    else:
        s = st.session_state.stats
        p = st.session_state.profile
        r = st.session_state.prediction

        badge_cls = {"Fit": "badge-fit", "Moderately Fit": "badge-moderate",
                     "Needs Improvement": "badge-needs"}.get(r["fitness_category"], "badge-moderate")
        st.markdown(f"""<div style='display:flex;align-items:center;gap:14px;margin-bottom:22px;'>
          <span style='font-size:26px;font-weight:700;color:#e0e0f8'>Fitness Status:</span>
          <span class='{badge_cls}'>{r['fitness_category']}</span>
        </div>""", unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        metrics = [
            (c1, "BMI",          s["bmi"],          s["bmi_category"]),
            (c2, "BMR",          int(s["bmr"]),      "kcal/day at rest"),
            (c3, "TDEE",         int(s["tdee"]),     "kcal/day total burn"),
            (c4, "Session Burn", int(s["cal_burned"]), "kcal per session"),
        ]
        for col, title, val, sub in metrics:
            with col:
                st.markdown(f"""<div class='metric-card'>
                  <div class='metric-title'>{title}</div>
                  <div class='metric-value'>{val}</div>
                  <div class='metric-sub'>{sub}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("---")
        lc, rc = st.columns(2)

        with lc:
            st.markdown("<div class='sec-hdr'>🧍 Your Stats</div>", unsafe_allow_html=True)
            rows = [
                ("Age / Gender",    f"{p['age']} yrs / {p['gender']}"),
                ("Height / Weight", f"{p['height']} cm / {p['weight']} kg"),
                ("Goal",            p.get("goal", "N/A")),
                ("Diet Preference", p.get("diet_pref", "N/A")),
                ("Activity Level",  p.get("activity", "N/A")),
                ("Body Fat",        f"{p['fat_pct']} %"),
                ("Heart Rate",      f"Rest:{p['resting_bpm']}  Avg:{p['avg_bpm']}  Max:{p['max_bpm']}"),
                ("Workout Type",    p["workout_type"]),
                ("Frequency",       f"{p['workout_freq']} days/week"),
                ("Experience",      ["", "Beginner", "Intermediate", "Expert"][p["experience"]]),
                ("Session Length",  f"{p['session_dur']} h"),
                ("Water Intake",    f"{p['water_intake']} L/day"),
            ]
            for lbl, val in rows:
                st.markdown(f"<div class='log-row'><span>{lbl}</span>"
                            f"<span style='color:#c0c0e8'>{val}</span></div>",
                            unsafe_allow_html=True)

        with rc:
            st.markdown("<div class='sec-hdr'>🎯 ML Recommendations</div>", unsafe_allow_html=True)
            for lbl, val in [
                ("Fitness Category", r["fitness_category"]),
                ("Diet Plan",        r["diet_plan"]),
                ("Workout Plan",     r["workout_plan"]),
            ]:
                st.markdown(f"<div class='log-row'><span>{lbl}</span>"
                            f"<span style='color:#e040fb'>{val}</span></div>",
                            unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<div class='sec-hdr'>📊 Kaggle Dataset Stats</div>", unsafe_allow_html=True)
            for lbl, val in [
                ("Source", "Gym Members Exercise Dataset"),
                ("Rows", "973 real gym members"),
                ("Features", "15 original + engineered features"),
                ("Model", "Random Forest"),
                ("Interface", "Streamlit + Groq LLM Chatbot"),
            ]:
                st.markdown(f"<div class='log-row'><span>{lbl}</span>"
                            f"<span style='color:#7070c0'>{val}</span></div>",
                            unsafe_allow_html=True)

        if st.session_state.progress_log:
            st.markdown("---")
            st.markdown("<div class='sec-hdr'>📈 Progress Log</div>", unsafe_allow_html=True)
            st.markdown("<div class='log-row'><b>Date</b><b>Weight</b><b>Calories</b><b>Workout</b></div>",
                        unsafe_allow_html=True)
            for e in reversed(st.session_state.progress_log[-10:]):
                st.markdown(f"<div class='log-row'>"
                            f"<span>{e['date']}</span><span>{e['weight']} kg</span>"
                            f"<span>{e['calories']} kcal</span>"
                            f"<span>{'✅' if e['workout'] == 'Yes' else '❌'}</span></div>",
                            unsafe_allow_html=True)

# ── TAB 3 : MEAL PLAN ──────────────────────────────────────────────────────────
with tab3:
    if not st.session_state.prediction:
        st.info("Generate your plan first.")
    else:
        r = st.session_state.prediction
        meal = get_meal_plan(r["diet_plan"])
        st.markdown(f"<div class='sec-hdr'>🍽️ {r['diet_plan']}</div>", unsafe_allow_html=True)
        for title, items in [
            ("🌅 Breakfast Options", meal["breakfast"]),
            ("☀️ Lunch Options",     meal["lunch"]),
            ("🌙 Dinner Options",    meal["dinner"]),
            ("🍎 Healthy Snacks",    meal["snacks"]),
        ]:
            st.markdown(f"<div class='plan-card'><div class='plan-header'>{title}</div>", unsafe_allow_html=True)
            for i, item in enumerate(items, 1):
                st.markdown(f"<div class='plan-item'>Option {i}: {item}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='plan-card'><div class='plan-header'>💡 Nutrition Tips</div>"
                    f"<div class='plan-note'>{meal['notes']}</div></div>", unsafe_allow_html=True)
        st.caption("⚠️ General wellness only — not a substitute for professional nutrition advice.")

# ── TAB 4 : WORKOUT PLAN ───────────────────────────────────────────────────────
with tab4:
    if not st.session_state.prediction:
        st.info("Generate your plan first.")
    else:
        r = st.session_state.prediction
        wo = get_workout_plan(r["workout_plan"])
        st.markdown(f"<div class='sec-hdr'>💪 {r['workout_plan']}</div>", unsafe_allow_html=True)
        st.markdown("<div class='plan-card'><div class='plan-header'>📅 Weekly Schedule</div>", unsafe_allow_html=True)
        for day in wo["weekly"]:
            st.markdown(f"<div class='plan-item'>• {day}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='plan-card'><div class='plan-header'>💡 Coach Tips</div>"
                    f"<div class='plan-note'>{wo['notes']}</div></div>", unsafe_allow_html=True)
        st.caption("⚠️ General fitness guidelines — consult a certified trainer before starting new programs.")

st.markdown("""
<div style='text-align:center;color:#303060;font-size:12px;margin-top:40px;
  padding:20px;border-top:1px solid #181838;'>
  FitBot — Built with Python · Scikit-learn · Streamlit · Groq LLM API<br>
  <span>Dataset: Gym Members Exercise Dataset (Kaggle) | For general wellness only.</span>
</div>""", unsafe_allow_html=True)
