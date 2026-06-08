"""
planner.py – Indian-style meal plans and workout plans keyed by recommendation labels.
"""

MEAL_PLANS = {
    "Low Calorie Balanced Diet": {
        "breakfast": [
            "Oats porridge with banana and chia seeds (no sugar)",
            "Moong dal chilla (2 pieces) with mint chutney",
            "Vegetable upma with green tea",
        ],
        "lunch": [
            "2 roti + dal + sabzi (bhindi/lauki/gobi) + cucumber raita",
            "Brown rice + rajma + salad",
            "Multigrain roti + palak paneer (low oil) + buttermilk",
        ],
        "dinner": [
            "1 roti + vegetable soup + mixed salad",
            "Moong dal khichdi (light) + papad",
            "Oats dosa + sambar + coconut chutney",
        ],
        "snacks": [
            "Handful of roasted chana",
            "1 fruit (apple/pear/guava)",
            "Buttermilk (plain, no salt)",
        ],
        "notes": "Avoid fried snacks, sugar, maida, and late-night eating. Drink 3L water daily.",
    },

    "High Protein Non-Veg Diet": {
        "breakfast": [
            "4 egg whites + 1 whole egg scrambled with veggies + 2 whole wheat toast",
            "Chicken keema paratha (1 piece) + low-fat curd",
            "Omelette (3 eggs) + banana milkshake (no sugar)",
        ],
        "lunch": [
            "2 roti + grilled chicken breast + dal + salad",
            "Brown rice + fish curry (mustard-based) + salad",
            "Chicken biryani (home-made, low oil) + raita",
        ],
        "dinner": [
            "2 eggs + paneer bhurji + 1 roti",
            "Grilled fish + brown rice + stir-fried veggies",
            "Boiled chicken salad + roti",
        ],
        "snacks": [
            "Boiled eggs (2)",
            "Roasted chana + peanuts (handful)",
            "Whey protein shake (if available)",
        ],
        "notes": "Focus on lean protein. Avoid deep frying. Grill, boil, or bake whenever possible.",
    },

    "High Protein Veg Diet": {
        "breakfast": [
            "Paneer bhurji (100g) + 2 multigrain roti",
            "Sprouts salad + soy milk + banana",
            "Greek yogurt + nuts + flaxseeds",
        ],
        "lunch": [
            "2 roti + rajma + palak paneer + salad",
            "Brown rice + chana masala + buttermilk",
            "Tofu stir-fry with veggies + brown rice",
        ],
        "dinner": [
            "2 roti + dal makhani (low cream) + sabzi",
            "Soya chunks curry + 2 roti + salad",
            "Paneer tikka + multigrain roti + soup",
        ],
        "snacks": [
            "Roasted peanuts / chana (50g)",
            "Soy protein shake",
            "Peanut butter on whole wheat bread",
        ],
        "notes": "Include soy, paneer, lentils, and legumes daily. Avoid empty-carb snacks.",
    },

    "Balanced Maintenance Diet": {
        "breakfast": [
            "Idli (3) + sambar + coconut chutney",
            "Poha with peanuts and green peas",
            "Whole wheat paratha + curd + pickle",
        ],
        "lunch": [
            "2 roti + mixed dal + sabzi + salad",
            "Rice + sambhar + papad + buttermilk",
            "Khichdi + ghee + papad + raita",
        ],
        "dinner": [
            "2 roti + sabzi + dal soup",
            "Vegetable pulao + raita",
            "Dosa + sambar",
        ],
        "snacks": [
            "Fruit chaat",
            "Dhokla (2 pieces)",
            "Makhana (roasted)",
        ],
        "notes": "Eat at regular times. Include all food groups. Limit sugar and processed food.",
    },

    "High Carb Performance Diet": {
        "breakfast": [
            "Banana + oats + honey smoothie + boiled eggs",
            "Poha + banana + green tea",
            "Whole wheat toast + peanut butter + fruit juice",
        ],
        "lunch": [
            "White rice + dal + sabzi + papad",
            "Pasta (whole wheat) + tomato sauce + paneer",
            "Roti + potato sabzi + lassi",
        ],
        "dinner": [
            "Rice + dal fry + salad",
            "2 roti + sabzi + soup",
            "Ragi roti + vegetable curry",
        ],
        "snacks": [
            "Banana + peanut butter",
            "Sweet potato chaat",
            "Energy bar (oats/dates based)",
        ],
        "notes": "Carbs fuel your performance. Time meals around workouts. Stay well-hydrated.",
    },
}

WORKOUT_PLANS = {
    "Beginner Cardio + Walking": {
        "weekly": [
            "Monday   – 30 min brisk walk + 10 min stretching",
            "Tuesday  – 20 min walk + bodyweight squats (3×10)",
            "Wednesday – Rest or 15 min gentle yoga",
            "Thursday  – 30 min brisk walk + wall push-ups (3×10)",
            "Friday    – 20 min walk + planks (3×20 sec)",
            "Saturday  – 30 min light cycling / Zumba",
            "Sunday    – Full rest",
        ],
        "notes": "Start slow. Focus on consistency over intensity. Increase walk time by 5 min each week.",
    },
    "Intermediate Cardio + HIIT": {
        "weekly": [
            "Monday   – 20 min HIIT (jumping jacks, high knees, burpees) + 10 min cooldown",
            "Tuesday  – 35 min jogging + core (planks, crunches)",
            "Wednesday – Active recovery: yoga / stretching",
            "Thursday  – 25 min HIIT + 15 min walk",
            "Friday    – 40 min cycling or skipping + abs",
            "Saturday  – Full body circuit (4 exercises × 4 rounds)",
            "Sunday    – Rest",
        ],
        "notes": "Keep rest intervals short (20-30 sec). Monitor heart rate. Hydrate before and after.",
    },
    "Beginner Fitness Routine": {
        "weekly": [
            "Monday   – Full body: squats, push-ups, lunges (3×10 each)",
            "Tuesday  – 30 min walk + stretching",
            "Wednesday – Rest",
            "Thursday  – Repeat Monday's routine",
            "Friday    – 30 min light activity (yoga / cycling)",
            "Saturday  – Core: plank, crunches, leg raises",
            "Sunday    – Full rest",
        ],
        "notes": "Master form before increasing reps. Rest is as important as training.",
    },
    "Active Lifestyle Routine": {
        "weekly": [
            "Monday   – Upper body: push-ups, rows, shoulder press (3×12)",
            "Tuesday  – 40 min cardio (run / cycle)",
            "Wednesday – Yoga + flexibility",
            "Thursday  – Lower body: squats, lunges, calf raises",
            "Friday    – HIIT or sports (badminton / cricket)",
            "Saturday  – Full body functional training",
            "Sunday    – Rest or light walk",
        ],
        "notes": "Vary your activities to stay motivated. Include outdoor sports when possible.",
    },
    "Progressive Strength Training": {
        "weekly": [
            "Monday   – Chest & Triceps: bench press, push-ups, tricep dips",
            "Tuesday  – Back & Biceps: rows, pull-ups / lat pulldown, curls",
            "Wednesday – Rest / light cardio",
            "Thursday  – Legs: squats, deadlifts, lunges, calf raises",
            "Friday    – Shoulders & Core: overhead press, lateral raises, planks",
            "Saturday  – Full body compound (deadlift + squat + bench)",
            "Sunday    – Rest",
        ],
        "notes": "Increase weight by ~2.5 kg each week (progressive overload). Log every session.",
    },
    "Compound Strength Training": {
        "weekly": [
            "Monday   – Squat + Bench + Bent-over Row (5×5)",
            "Tuesday  – Rest",
            "Wednesday – Deadlift + Overhead Press + Pull-ups (5×5)",
            "Thursday  – Rest",
            "Friday    – Squat + Bench + Bent-over Row (5×5)",
            "Saturday  – Accessory: arms, core, calves",
            "Sunday    – Rest",
        ],
        "notes": "Eat in a calorie surplus. Sleep 8 hours. Track body weight weekly.",
    },
    "Moderate Strength Training": {
        "weekly": [
            "Monday   – Full body: machines preferred (leg press, chest press, lat pulldown)",
            "Wednesday – Cardio 30 min + core exercises",
            "Friday    – Full body repeat + stretching",
            "Other days – Rest or gentle walk",
        ],
        "notes": "Prioritize safety. Avoid heavy free weights alone. A trainer is recommended.",
    },
    "Cardio Endurance Training": {
        "weekly": [
            "Monday   – 5 km run (easy pace)",
            "Tuesday  – Intervals: 8×400m runs",
            "Wednesday – Rest / yoga",
            "Thursday  – 6 km tempo run",
            "Friday    – Cycling 45 min",
            "Saturday  – Long run 8–10 km (easy)",
            "Sunday    – Rest",
        ],
        "notes": "Build mileage gradually (10% rule). Include 1–2 rest days. Stay hydrated.",
    },
}


def get_meal_plan(diet_plan_label: str) -> dict:
    return MEAL_PLANS.get(diet_plan_label, MEAL_PLANS["Balanced Maintenance Diet"])


def get_workout_plan(workout_plan_label: str) -> dict:
    return WORKOUT_PLANS.get(workout_plan_label, WORKOUT_PLANS["Beginner Fitness Routine"])
