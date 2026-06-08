"""
app.py  –  FitBot  |  Professional Streamlit App
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

# ── helpers ────────────────────────────────────────────────────────────────────
def md_to_html(text: str) -> str:
    """Render markdown bold + newlines inside custom HTML bubbles."""
    t = html.escape(str(text))
    t = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\*(.*?)\*",     r"<em>\1</em>", t)
    # bullet lines  ─ keep leading •
    lines = t.split("&#10;") if "&#10;" in t else t.split("\n")
    out = []
    for ln in lines:
        ln = ln.strip()
        if not ln:
            out.append("<br>")
        elif ln.startswith("•") or ln.startswith("-") or ln.startswith("*"):
            out.append(f"<div class='bot-bullet'>{ln.lstrip('•- *').strip()}</div>")
        else:
            out.append(f"<span>{ln}</span><br>")
    return "".join(out)

# ── page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FitBot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── background ── */
.stApp { background: #0a0a0f; }
.main .block-container { padding: 2rem 2.5rem 4rem; max-width: 1100px; }

/* ── hide streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── sidebar ── */
section[data-testid="stSidebar"] {
    background: #0d0d14;
    border-right: 1px solid #1c1c2e;
    padding-top: 0;
}
section[data-testid="stSidebar"] > div { padding: 1.5rem 1.2rem; }

/* sidebar brand */
.sb-brand {
    display: flex; align-items: center; gap: 10px;
    padding: 0 0 1.2rem;
    border-bottom: 1px solid #1c1c2e;
    margin-bottom: 1.4rem;
}
.sb-brand-icon {
    width: 36px; height: 36px; border-radius: 10px;
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
}
.sb-brand-name { font-size: 17px; font-weight: 700; color: #f0f0ff; letter-spacing: -0.3px; }
.sb-brand-sub  { font-size: 11px; color: #555570; margin-top: 1px; }

/* sidebar section labels */
.sb-label {
    font-size: 10px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 1.2px; color: #44445a;
    margin: 1.4rem 0 0.6rem;
}

/* generate button */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    color: #fff !important; border: none !important;
    border-radius: 10px !important; font-weight: 600 !important;
    font-size: 14px !important; padding: 0.65rem 1rem !important;
    width: 100% !important; cursor: pointer !important;
    transition: opacity .2s !important;
}
div[data-testid="stButton"] > button:hover { opacity: .85 !important; }

/* ── top nav strip ── */
.topnav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 0 1.6rem;
    border-bottom: 1px solid #1c1c2e;
    margin-bottom: 1.8rem;
}
.topnav-title { font-size: 22px; font-weight: 700; color: #e8e8ff; letter-spacing: -0.5px; }
.topnav-badge {
    font-size: 11px; font-weight: 500; color: #7c3aed;
    background: #1a1040; border: 1px solid #3d2080;
    padding: 4px 10px; border-radius: 20px; letter-spacing: .3px;
}

/* ── tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    gap: 4px !important;
    border-bottom: 1px solid #1c1c2e !important;
    padding-bottom: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #555570 !important;
    font-size: 13px !important; font-weight: 500 !important;
    padding: 8px 18px !important;
    border-radius: 8px 8px 0 0 !important;
    border: none !important;
    transition: color .15s !important;
}
.stTabs [aria-selected="true"] {
    color: #a78bfa !important;
    border-bottom: 2px solid #7c3aed !important;
    background: #110a20 !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.6rem !important; }

/* ── metric cards ── */
.mcard {
    background: #0f0f1a;
    border: 1px solid #1c1c2e;
    border-radius: 14px;
    padding: 18px 16px;
    text-align: center;
}
.mcard-label { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.2px; color: #44445a; margin-bottom: 10px; }
.mcard-value { font-size: 28px; font-weight: 700; color: #a78bfa; font-family: 'JetBrains Mono', monospace; line-height: 1; }
.mcard-sub   { font-size: 11px; color: #555570; margin-top: 6px; }

/* ── badges ── */
.badge        { display:inline-flex; align-items:center; padding: 5px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.badge-green  { background: #0d2018; color: #34d399; border: 1px solid #1a4d30; }
.badge-yellow { background: #1e1a08; color: #fbbf24; border: 1px solid #4d3f0a; }
.badge-red    { background: #200d0d; color: #f87171; border: 1px solid #4d1a1a; }

/* ── stat rows ── */
.stat-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 9px 0; border-bottom: 1px solid #141420;
    font-size: 13px;
}
.stat-row:last-child { border-bottom: none; }
.stat-key   { color: #555570; }
.stat-val   { color: #c8c8e8; font-weight: 500; font-family: 'JetBrains Mono', monospace; font-size: 12px; }
.stat-val-accent { color: #a78bfa; font-weight: 600; font-family: 'JetBrains Mono', monospace; font-size: 12px; }

/* ── section headers ── */
.sec-title {
    font-size: 13px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 1px; color: #44445a;
    padding-bottom: 8px; border-bottom: 1px solid #1c1c2e;
    margin-bottom: 14px;
}

/* ── info cards (meal / workout) ── */
.info-card {
    background: #0f0f1a; border: 1px solid #1c1c2e;
    border-radius: 12px; padding: 18px; margin-bottom: 12px;
}
.info-card-title { font-size: 13px; font-weight: 600; color: #a78bfa; margin-bottom: 12px; }
.info-item {
    font-size: 13px; color: #8888aa; padding: 7px 0;
    border-bottom: 1px solid #141420; line-height: 1.5;
}
.info-item:last-child { border-bottom: none; }
.info-item-num { color: #44445a; font-size: 11px; margin-right: 6px; font-family: 'JetBrains Mono', monospace; }
.info-note { font-size: 12px; color: #44445a; font-style: italic; padding-top: 10px; border-top: 1px solid #141420; margin-top: 10px; }

/* ── chat ── */
.chat-wrap { display: flex; flex-direction: column; gap: 6px; margin-bottom: 8px; }

.chat-user-row { display: flex; justify-content: flex-end; }
.chat-bot-row  { display: flex; justify-content: flex-start; }

.chat-bubble-user {
    background: #1a1040;
    border: 1px solid #2e1d6e;
    border-radius: 18px 18px 4px 18px;
    padding: 11px 16px;
    max-width: 72%;
    font-size: 13.5px; color: #c4b5fd; line-height: 1.6;
}
.chat-bubble-bot {
    background: #0f0f1a;
    border: 1px solid #1c1c2e;
    border-radius: 18px 18px 18px 4px;
    padding: 14px 18px;
    max-width: 82%;
    font-size: 13.5px; color: #d0d0e8; line-height: 1.7;
}
.chat-bubble-bot strong { color: #c4b5fd; font-weight: 600; }
.chat-bubble-bot em     { color: #a78bfa; font-style: normal; }

.bot-bullet {
    position: relative;
    padding-left: 14px;
    margin: 3px 0;
    color: #b0b0cc;
    font-size: 13px;
}
.bot-bullet::before {
    content: "›";
    position: absolute; left: 0;
    color: #7c3aed; font-weight: 700;
}

.chat-name-user { font-size: 10px; color: #44445a; text-align: right; margin-bottom: 3px; margin-right: 4px; }
.chat-name-bot  { font-size: 10px; color: #44445a; margin-bottom: 3px; margin-left: 4px; }

/* chat empty state */
.chat-empty {
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; padding: 60px 20px;
    color: #333348; text-align: center;
}
.chat-empty-icon { font-size: 40px; margin-bottom: 14px; opacity: .5; }
.chat-empty-text { font-size: 14px; color: #44445a; line-height: 1.7; }

/* ── progress log ── */
.log-header {
    display: flex; justify-content: space-between;
    font-size: 10px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 1px; color: #333348;
    padding: 0 0 8px; border-bottom: 1px solid #1c1c2e; margin-bottom: 4px;
}
.log-row {
    display: flex; justify-content: space-between; align-items: center;
    font-size: 12px; color: #666680; padding: 8px 0;
    border-bottom: 1px solid #111120; font-family: 'JetBrains Mono', monospace;
}
.log-row:last-child { border-bottom: none; }

/* ── disclaimer ── */
.disclaimer {
    font-size: 11px; color: #2a2a3a;
    text-align: center; margin-top: 3rem;
    padding-top: 1.2rem; border-top: 1px solid #111120;
}

/* ── input widgets override ── */
.stSelectbox > div > div,
.stNumberInput > div > div > input,
.stSlider { background: #0d0d14 !important; }

div[data-testid="stNumberInput"] input { color: #c8c8e8 !important; background: #0d0d14 !important; border-color: #1c1c2e !important; }
</style>
""", unsafe_allow_html=True)

# ── session state ──────────────────────────────────────────────────────────────
for k, v in {
    "chat_history": [], "profile": None,
    "stats": None, "prediction": None, "progress_log": [],
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class='sb-brand'>
      <div class='sb-brand-icon'>⚡</div>
      <div>
        <div class='sb-brand-name'>FitBot</div>
        <div class='sb-brand-sub'>AI Fitness Advisor</div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div class='sb-label'>Body Metrics</div>", unsafe_allow_html=True)
    age    = st.number_input("Age",          18, 80,  25, label_visibility="visible")
    gender = st.selectbox("Gender",          ["Male", "Female"])
    height = st.number_input("Height (cm)",  140.0, 210.0, 170.0, step=0.5)
    weight = st.number_input("Weight (kg)",   30.0, 150.0,  70.0, step=0.5)
    fat_pct= st.number_input("Body Fat %",    5.0,  50.0,  20.0, step=0.5)

    st.markdown("<div class='sb-label'>Training</div>", unsafe_allow_html=True)
    goal         = st.selectbox("Goal", ["Fat Loss", "Muscle Gain", "Maintain Fitness"])
    diet_pref    = st.selectbox("Diet", ["Vegetarian", "Non-Vegetarian", "Vegan", "Eggetarian"])
    workout_type = st.selectbox("Workout Type", ["Cardio", "Strength", "HIIT", "Yoga"])
    workout_freq = st.slider("Days / Week", 1, 7, 3)
    experience   = st.selectbox("Experience", ["Beginner", "Intermediate", "Expert"])
    exp_num      = {"Beginner": 1, "Intermediate": 2, "Expert": 3}[experience]

    st.markdown("<div class='sb-label'>Heart Rate</div>", unsafe_allow_html=True)
    max_bpm     = st.number_input("Max BPM",     100, 220, 175)
    avg_bpm     = st.number_input("Avg BPM",      80, 200, 140)
    resting_bpm = st.number_input("Resting BPM",  40,  90,  60)

    st.markdown("<div class='sb-label'>Habits</div>", unsafe_allow_html=True)
    water_intake = st.number_input("Water (L/day)", 1.0, 5.0, 2.5, step=0.1)
    session_dur  = st.number_input("Session (hrs)", 0.25, 3.0, 1.0, step=0.25)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⚡  Generate My Plan"):
        act_map    = ["Sedentary","Light","Moderate","Active","Very Active","Very Active","Very Active"]
        act_level  = act_map[workout_freq - 1]
        bmi_val    = calculate_bmi(weight, height)
        bmi_cat_v  = bmi_category(bmi_val)
        bmr_val    = calculate_bmr(weight, height, age, gender)
        tdee_val   = calculate_tdee(bmr_val, act_level)
        cal_burned = round(session_dur * avg_bpm * 0.5, 1)
        h_m        = height / 100

        pred = predict(
            age=age, gender=gender, weight_kg=weight, height_m=h_m,
            bmi=bmi_val, bmi_category=bmi_cat_v,
            max_bpm=max_bpm, avg_bpm=avg_bpm, resting_bpm=resting_bpm,
            session_duration_h=session_dur, calories_burned=cal_burned,
            fat_pct=fat_pct, water_intake_l=water_intake,
            workout_freq=workout_freq, workout_type=workout_type,
            experience_level=exp_num, bmr=bmr_val, tdee=tdee_val,
        )

        st.session_state.profile = dict(
            age=age, gender=gender, height=height, weight=weight,
            goal=goal, diet_pref=diet_pref, activity=act_level,
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
                f"Plan generated ✓\n\n"
                f"**BMI** {bmi_val} · {bmi_cat_v}\n"
                f"**TDEE** {int(tdee_val)} kcal/day\n"
                f"**Category** {pred['fitness_category']}\n"
                f"**Diet Plan** {pred['diet_plan']}\n"
                f"**Workout** {pred['workout_plan']}\n\n"
                f"Ask me anything about your plan."
            )
        }]
        st.rerun()

    # ── progress log ──
    if st.session_state.profile:
        st.markdown("<div class='sb-label' style='margin-top:1.6rem'>Log Today</div>", unsafe_allow_html=True)
        lw  = st.number_input("Weight (kg)", 30.0, 150.0, float(st.session_state.profile["weight"]), key="lw")
        lc  = st.number_input("Calories eaten", 0, 6000, 1800, key="lc")
        lwo = st.selectbox("Workout done?", ["Yes", "No"], key="lwo")
        if st.button("Save Entry"):
            st.session_state.progress_log.append({
                "date": datetime.now().strftime("%d %b"), "weight": lw,
                "calories": lc, "workout": lwo,
            })
            st.success("Saved")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class='topnav'>
  <span class='topnav-title'>FitBot <span style='color:#3a3a5a;font-weight:300'>/ Dashboard</span></span>
  <span class='topnav-badge'>⚡ Groq · LLaMA 3.3 · Random Forest</span>
</div>""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["Chat", "Overview", "Meal Plan", "Workout"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — CHAT
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    if not st.session_state.chat_history:
        st.markdown("""
        <div class='chat-empty'>
          <div class='chat-empty-icon'>⚡</div>
          <div class='chat-empty-text'>
            Fill in your details on the left<br>and click <strong style='color:#7c3aed'>Generate My Plan</strong> to begin.
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("<div class='chat-wrap'>", unsafe_allow_html=True)
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(
                    f"<div class='chat-name-user'>You</div>"
                    f"<div class='chat-user-row'>"
                    f"<div class='chat-bubble-user'>{html.escape(msg['text'])}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div class='chat-name-bot'>FitBot</div>"
                    f"<div class='chat-bot-row'>"
                    f"<div class='chat-bubble-bot'>{md_to_html(msg['text'])}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)

        user_input = st.chat_input("Message FitBot…")
        if user_input:
            st.session_state.chat_history.append({"role": "user", "text": user_input})
            p    = st.session_state.profile
            s    = st.session_state.stats
            r    = st.session_state.prediction
            meal = get_meal_plan(r["diet_plan"])
            wo   = get_workout_plan(r["workout_plan"])

            SYSTEM = f"""You are FitBot — a concise, professional AI fitness and diet advisor.

OUTPUT FORMAT RULES (critical):
- Use **bold** for key terms, meal names, and exercise names.
- Use bullet points (start line with •) for lists of meals or exercises.
- Never use headers like ## or ###.
- Keep answers under 12 lines. Detailed plans max 16 lines.
- Never ask "How does that sound?" or "Feel free to ask."
- Never say "Based on your profile" at the start — just answer directly.
- Never add a Tips/Note/Remember section at the end unless asked.
- Do not repeat any meal or exercise already given in this conversation.
- For regional cuisine requests (North Indian, South Indian, Gujarati etc.) — give entirely new meals.

DIET RESTRICTION (non-negotiable):
- Vegetarian → no egg, chicken, fish, meat.
- Vegan → no milk, paneer, curd, ghee, honey, egg.
- Non-Vegetarian → eggs, chicken, fish allowed.
- Eggetarian → eggs yes, meat/fish/chicken no.
- Beginner → no burpees, mountain climbers, heavy barbells, box jumps.

USER:
Age {p.get("age")} | Gender {p.get("gender")} | Height {p.get("height")} cm | Weight {p.get("weight")} kg
BMI {s.get("bmi")} ({s.get("bmi_category")}) | Fat {p.get("fat_pct")}% | Goal {p.get("goal")}
Diet {p.get("diet_pref")} | Activity {p.get("activity")} | Experience {["","Beginner","Intermediate","Expert"][p.get("experience",1)]}
Workout {p.get("workout_type")} | {p.get("workout_freq")} days/week | Session {p.get("session_dur")} h
BPM Rest/Avg/Max {p.get("resting_bpm")}/{p.get("avg_bpm")}/{p.get("max_bpm")} | Water {p.get("water_intake")} L/day

ML MODEL OUTPUT:
Fitness Category: {r.get("fitness_category")}
Diet Plan: {r.get("diet_plan")}
Workout Plan: {r.get("workout_plan")}

MEAL PLAN ({r.get("diet_plan")}):
Breakfast: {" | ".join(meal.get("breakfast", []))}
Lunch: {" | ".join(meal.get("lunch", []))}
Dinner: {" | ".join(meal.get("dinner", []))}
Snacks: {" | ".join(meal.get("snacks", []))}

WORKOUT ({r.get("workout_plan")}):
{chr(10).join(wo.get("weekly", []))}

CALORIES: BMR {int(s.get("bmr",0))} | TDEE {int(s.get("tdee",0))} kcal"""

            msgs = []
            for m in st.session_state.chat_history[:-1]:
                msgs.append({"role": "user" if m["role"] == "user" else "assistant", "content": m["text"]})
            msgs.append({"role": "user", "content": user_input})

            try:
                from groq import Groq
                key = os.getenv("GROQ_API_KEY")
                if not key:
                    raise ValueError("GROQ_API_KEY not set")
                client   = Groq(api_key=key)
                groq_msgs = [{"role": "system", "content": SYSTEM}] + msgs
                resp  = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=groq_msgs,
                    temperature=0.45,
                    max_tokens=500,
                )
                reply = resp.choices[0].message.content

            except ImportError:
                reply = "⚠️ Run `pip install groq` then restart the app."
            except Exception as e:
                err = str(e).lower()
                if any(k in err for k in ["api_key","auth","invalid","missing","gsk"]):
                    reply = "🔑 Groq API key missing.\n\nSet it in PowerShell:\n`$env:GROQ_API_KEY=\"gsk_...\"`\n\nGet key at **console.groq.com/keys**"
                elif any(k in err for k in ["rate","limit","quota"]):
                    reply = "⏳ Rate limit hit — wait 30 seconds and try again."
                elif any(k in err for k in ["connection","reset","timeout"]):
                    reply = "🌐 Connection error — switch to mobile hotspot and retry."
                else:
                    reply = f"⚠️ {str(e)[:200]}"

            st.session_state.chat_history.append({"role": "bot", "text": reply})
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    if not st.session_state.stats:
        st.markdown("<div class='chat-empty'><div class='chat-empty-icon'>📊</div><div class='chat-empty-text'>Generate your plan to see the overview.</div></div>", unsafe_allow_html=True)
    else:
        s = st.session_state.stats
        p = st.session_state.profile
        r = st.session_state.prediction

        badge_map = {
            "Fit":               ("badge-green",  "● Fit"),
            "Moderately Fit":    ("badge-yellow", "● Moderately Fit"),
            "Needs Improvement": ("badge-red",    "● Needs Improvement"),
        }
        bcls, blbl = badge_map.get(r["fitness_category"], ("badge-yellow", r["fitness_category"]))
        st.markdown(f"<div style='margin-bottom:1.6rem'><span class='badge {bcls}'>{blbl}</span></div>", unsafe_allow_html=True)

        # metric row
        c1, c2, c3, c4 = st.columns(4)
        for col, lbl, val, sub in [
            (c1, "BMI",          s["bmi"],           s["bmi_category"]),
            (c2, "BMR",          f"{int(s['bmr'])}",  "kcal · at rest"),
            (c3, "TDEE",         f"{int(s['tdee'])}", "kcal · daily burn"),
            (c4, "Session Burn", f"{int(s['cal_burned'])}", "kcal · per session"),
        ]:
            with col:
                st.markdown(f"""<div class='mcard'>
                  <div class='mcard-label'>{lbl}</div>
                  <div class='mcard-value'>{val}</div>
                  <div class='mcard-sub'>{sub}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown("<div class='sec-title'>Profile</div>", unsafe_allow_html=True)
            profile_rows = [
                ("Age / Gender",   f"{p['age']} yrs · {p['gender']}"),
                ("Height / Weight",f"{p['height']} cm · {p['weight']} kg"),
                ("Body Fat",       f"{p['fat_pct']} %"),
                ("Goal",           p.get("goal","—")),
                ("Diet",           p.get("diet_pref","—")),
                ("Activity",       p.get("activity","—")),
                ("Workout Type",   p.get("workout_type","—")),
                ("Frequency",      f"{p['workout_freq']} days/week"),
                ("Experience",     ["","Beginner","Intermediate","Expert"][p["experience"]]),
                ("Session",        f"{p['session_dur']} h"),
                ("Water",          f"{p['water_intake']} L/day"),
                ("BPM (R/A/M)",    f"{p['resting_bpm']} / {p['avg_bpm']} / {p['max_bpm']}"),
            ]
            for k, v in profile_rows:
                st.markdown(f"<div class='stat-row'><span class='stat-key'>{k}</span><span class='stat-val'>{v}</span></div>", unsafe_allow_html=True)

        with col_r:
            st.markdown("<div class='sec-title'>ML Recommendations</div>", unsafe_allow_html=True)
            for k, v in [
                ("Fitness Category", r["fitness_category"]),
                ("Diet Plan",        r["diet_plan"]),
                ("Workout Plan",     r["workout_plan"]),
            ]:
                st.markdown(f"<div class='stat-row'><span class='stat-key'>{k}</span><span class='stat-val-accent'>{v}</span></div>", unsafe_allow_html=True)

            st.markdown("<div class='sec-title' style='margin-top:1.4rem'>Dataset</div>", unsafe_allow_html=True)
            for k, v in [
                ("Source",    "Gym Members Exercise · Kaggle"),
                ("Samples",   "973 real gym members"),
                ("Features",  "15 + 8 engineered"),
                ("Model",     "Random Forest"),
                ("Accuracy",  "94.87 %"),
            ]:
                st.markdown(f"<div class='stat-row'><span class='stat-key'>{k}</span><span class='stat-val'>{v}</span></div>", unsafe_allow_html=True)

        # progress log
        if st.session_state.progress_log:
            st.markdown("<br><div class='sec-title'>Progress Log</div>", unsafe_allow_html=True)
            st.markdown("<div class='log-header'><span>Date</span><span>Weight</span><span>Calories</span><span>Workout</span></div>", unsafe_allow_html=True)
            for e in reversed(st.session_state.progress_log[-10:]):
                wo_icon = "✓" if e["workout"] == "Yes" else "✗"
                st.markdown(f"<div class='log-row'><span>{e['date']}</span><span>{e['weight']} kg</span><span>{e['calories']} kcal</span><span>{wo_icon}</span></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — MEAL PLAN
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    if not st.session_state.prediction:
        st.markdown("<div class='chat-empty'><div class='chat-empty-icon'>🍽️</div><div class='chat-empty-text'>Generate your plan first.</div></div>", unsafe_allow_html=True)
    else:
        r    = st.session_state.prediction
        meal = get_meal_plan(r["diet_plan"])

        st.markdown(f"<div class='sec-title'>{r['diet_plan']}</div>", unsafe_allow_html=True)

        for section_title, items in [
            ("Breakfast", meal["breakfast"]),
            ("Lunch",     meal["lunch"]),
            ("Dinner",    meal["dinner"]),
            ("Snacks",    meal["snacks"]),
        ]:
            st.markdown(f"<div class='info-card'><div class='info-card-title'>{section_title}</div>", unsafe_allow_html=True)
            for i, item in enumerate(items, 1):
                st.markdown(f"<div class='info-item'><span class='info-item-num'>0{i}</span>{item}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"<div class='info-card'><div class='info-card-title'>Nutrition Note</div>"
                    f"<div class='info-note'>{meal['notes']}</div></div>", unsafe_allow_html=True)
        st.markdown("<div class='disclaimer'>General wellness guidance only — not a substitute for professional nutrition advice.</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — WORKOUT
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    if not st.session_state.prediction:
        st.markdown("<div class='chat-empty'><div class='chat-empty-icon'>💪</div><div class='chat-empty-text'>Generate your plan first.</div></div>", unsafe_allow_html=True)
    else:
        r  = st.session_state.prediction
        wo = get_workout_plan(r["workout_plan"])

        st.markdown(f"<div class='sec-title'>{r['workout_plan']}</div>", unsafe_allow_html=True)

        st.markdown("<div class='info-card'><div class='info-card-title'>Weekly Schedule</div>", unsafe_allow_html=True)
        for day in wo["weekly"]:
            parts = day.split("–", 1)
            if len(parts) == 2:
                st.markdown(f"<div class='info-item'><span class='info-item-num'>{parts[0].strip()}</span>{parts[1].strip()}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='info-item'>{day}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"<div class='info-card'><div class='info-card-title'>Coach Note</div>"
                    f"<div class='info-note'>{wo['notes']}</div></div>", unsafe_allow_html=True)
        st.markdown("<div class='disclaimer'>General fitness guidelines only — consult a certified trainer before starting new programs.</div>", unsafe_allow_html=True)
