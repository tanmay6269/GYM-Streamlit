"""Rule-based gym helper for the public pages.

No outside service is called and no member data is used: answers come from the plan
prices below and from short, general safety notes. It never diagnoses anything.
"""

PLANS = [("1 Month", 1, 1000), ("3 Months", 3, 2400), ("6 Months", 6, 4200), ("12 Months", 12, 7000)]
MONTHLY_PRICE = PLANS[0][2]

DISCLAIMER = ("General information only, not medical advice. If you have a health condition, "
              "an injury or any doubt, talk to a doctor before you start or change your exercise.")

# Questions of the Physical Activity Readiness Questionnaire (PAR-Q), Canadian Society for
# Exercise Physiology, shortened.
PARQ = [
    "Has a doctor ever said you have a heart condition and should do only doctor-recommended activity?",
    "Do you feel pain in your chest when you do physical activity?",
    "In the past month, have you had chest pain when you were not doing physical activity?",
    "Do you lose your balance because of dizziness, or ever lose consciousness?",
    "Do you have a bone or joint problem that could get worse with more physical activity?",
    "Is a doctor currently prescribing medicine for your blood pressure or a heart condition?",
    "Do you know of any other reason why you should not do physical activity?",
]


def plan_rows():
    """Plan name, months, price, saving against paying monthly, and cost per month."""
    return [{"name": n, "months": m, "price": p, "saving": MONTHLY_PRICE * m - p, "per_month": round(p / m)}
            for n, m, p in PLANS]


def parq_result(answers):
    """answers: list of 7 booleans (True = yes). Returns (needs_doctor, message)."""
    if any(answers):
        return True, ("One or more of your answers is a YES. Please talk to a doctor before you start "
                      "or increase your exercise, and tell the gym team what the doctor advises.")
    return False, ("You answered NO to every question, so these answers do not show a reason to stop. "
                   "Start slowly, warm up, learn the correct form and stop if you feel pain, dizziness "
                   "or chest discomfort. This is not a medical check.")


def recommend_plan(goal, stay):
    """goal: text label, stay: how long the person expects to train. Returns a plan row and a reason."""
    rows = {r["months"]: r for r in plan_rows()}
    if stay == "Not sure yet":
        months, why = 1, "Start with one month to see if the gym suits you."
    elif stay == "About 3 months":
        months, why = 3, "Three months is enough to build a routine and costs less per month."
    elif stay == "About 6 months":
        months, why = 6, "Six months gives time to see steady progress at a lower monthly cost."
    else:
        months, why = 12, "A full year gives the lowest cost per month."
    if goal == "Just trying the gym" and months > 3:
        months, why = 3, "For a first try, three months is a safer choice than a long plan."
    return rows[months], why


def _plans_text():
    lines = [f"{r['name']}: Rs. {r['price']:,}" + (f" (saves Rs. {r['saving']:,})" if r["saving"] else "")
             for r in plan_rows()]
    return "Our plans:\n\n" + "\n\n".join("- " + l for l in lines)


def _value_text():
    best = plan_rows()[-1]
    return (f"The 12 Months plan is the best value: Rs. {best['price']:,} saves Rs. {best['saving']:,} "
            f"compared with paying monthly, about Rs. {best['per_month']} a month. "
            "If you are new, a 1 or 3 Months plan lets you try before you commit.")


# (keywords, answer). The entry with the most keyword matches wins.
_TOPICS = [
    (("plan", "price", "cost", "fee", "membership", "rate", "month"), _plans_text),
    (("best", "value", "cheap", "save", "offer", "discount", "which plan"), _value_text),
    (("beginner", "new to", "start", "first time", "first day"),
     "If you are new: train 2 to 3 days a week, warm up for 5 to 10 minutes, learn the correct form "
     "with a trainer before adding weight, and rest between sessions. Progress slowly."),
    (("sore", "soreness", "doms", "muscle ache"),
     "Muscle soreness one or two days after a new workout is common and usually eases in a few days. "
     "Light movement, enough sleep and water help. See a doctor if the pain is sharp, there is swelling, "
     "or it does not improve."),
    (("injury", "sprain", "strain", "pulled", "hurt"),
     "Stop the exercise if something hurts sharply. Rest the area and do not push through pain. "
     "See a doctor if there is swelling, bruising, or you cannot put weight on it."),
    (("back pain", "backache", "spine", "slip disc"),
     "Back strain often comes from poor form or lifting too heavy. Keep your back neutral and lift lighter. "
     "See a doctor first if you already have back problems, or if there is numbness or pain going down a leg."),
    (("blood pressure", "bp", "hypertension", "heart", "chest"),
     "With a heart condition or high blood pressure, get a doctor's clearance first. During exercise, "
     "breathe steadily instead of holding your breath, and stop and seek help for chest pain, severe "
     "breathlessness or dizziness."),
    (("diabetes", "sugar", "insulin"),
     "If you have diabetes, ask your doctor how exercise may affect your sugar levels and medicine, and "
     "follow that advice. Tell the trainer so they know."),
    (("asthma", "breathless", "wheez"),
     "If you have asthma, ask your doctor for advice, keep your prescribed inhaler with you, warm up "
     "longer, and stop if you wheeze or feel breathless."),
    (("water", "dehydrat", "thirst", "sweat"),
     "Drink water before, during and after training. Dizziness, a very dry mouth or dark urine can be "
     "signs you need more fluid."),
    (("protein", "supplement", "creatine", "whey", "bcaa"),
     "Supplements are optional and do not replace a balanced diet. Check with a doctor or dietitian, "
     "especially if you have a health condition. Our Store page lists gym products."),
    (("weight loss", "lose weight", "fat", "slim"),
     "Weight loss comes from regular training, a balanced diet and enough sleep over months, not quick "
     "fixes. A trainer or dietitian can set a plan that suits you."),
    (("muscle", "gain", "bulk", "strength"),
     "Building muscle needs steady strength training, enough food and protein from your diet, and rest. "
     "It takes months, so pick a plan you can keep."),
    (("routine", "beginner routine", "workout plan", "split", "schedule", "exercise plan", "what exercises"),
     "A simple beginner week is 3 days of full-body training (a squat or leg press, a push, a pull and a core move), "
     "about 45 minutes each, with a rest day between. The Plan finder tool can build a starter week for you."),
    (("eat", "food", "diet", "meal", "pre-workout", "post-workout", "before a workout", "after a workout", "before workout"),
     "Before training, a light meal with carbohydrates and some protein 1 to 3 hours earlier works for most people. "
     "After training, have protein with carbohydrates, for example eggs, dal, curd, paneer, chicken, rice or roti, and "
     "drink water. A dietitian can tailor this to you."),
    (("bmi", "body mass", "calorie", "calories"),
     "Use the Health checker tool: it works out your BMI, daily calories, water and protein from your age, height, "
     "weight and activity."),
    (("quiz", "fitness quiz"),
     "Members can take the fitness quiz after logging in. A high score earns a discount of up to 10%."),
    (("login", "log in", "sign in", "account", "password"),
     "Use the Login button at the top right and choose Admin, Team or Member. Your gym team gives you "
     "your user ID."),
    (("time", "timing", "open", "contact", "address", "location"),
     "Opening hours and contact details are set by the gym owner. Please ask at the front desk."),
]

_HEALTH_WORDS = ("chest", "dizz", "faint", "heart", "pregnan", "surgery", "injur", "pain", "diabet",
                 "pressure", "asthma", "disease", "sick", "medicine", "fit to", "unfit")

FALLBACK = ("I can help with our plans and prices, getting started, common aches, and general gym "
            "safety. Try: \"Which plan is best value?\" or \"I am a beginner, where do I start?\"")


def answer(question):
    """Return a plain-text answer. Health words always add the safety note."""
    text = (question or "").lower().strip()
    if not text:
        return "Please type a question."
    best, best_score = None, 0
    for keys, reply in _TOPICS:
        score = sum(1 for k in keys if k in text)
        if score > best_score:
            best, best_score = reply, score
    reply = best() if callable(best) else best
    if reply is None:
        reply = FALLBACK
    if any(w in text for w in _HEALTH_WORDS):
        reply += ("\n\nI cannot tell whether a person is fit or unfit for the gym. For that, please see a "
                  "doctor. You can also use the Safe-to-Train Check on this page.")
    return reply


# ---------------------------------------------------------------- health checker
# BMI categories: WHO. Calories: Mifflin-St Jeor equation. Water and protein are common
# rule-of-thumb ranges (35 ml per kg; 1.4 to 2.0 g per kg for people who train, ISSN position stand).
ACTIVITY = {
    "Little or no exercise": 1.2,
    "Light (1 to 3 days a week)": 1.375,
    "Moderate (3 to 5 days a week)": 1.55,
    "Heavy (6 to 7 days a week)": 1.725,
}
GOALS = ["Lose weight", "Build muscle", "Stay fit and healthy", "Just trying the gym"]


def bmi_value(weight_kg, height_cm):
    return weight_kg / ((height_cm / 100) ** 2)


def bmi_category(bmi):
    """WHO adult categories. Returns (label, colour)."""
    if bmi < 18.5:
        return "Underweight", "#0ea5e9"
    if bmi < 25:
        return "Normal weight", "#16a34a"
    if bmi < 30:
        return "Overweight", "#f59e0b"
    return "Obese", "#dc2626"


def healthy_weight_range(height_cm):
    """Weight range (kg) that gives a BMI of 18.5 to 24.9 at this height."""
    m2 = (height_cm / 100) ** 2
    return round(18.5 * m2, 1), round(24.9 * m2, 1)


def health_check(age, gender, height_cm, weight_kg, activity, goal):
    """All numbers for the health checker. Adults only (18 and over)."""
    bmi = bmi_value(weight_kg, height_cm)
    label, colour = bmi_category(bmi)
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + (5 if gender == "Male" else -161)
    maintain = round(bmr * ACTIVITY[activity])
    if goal == "Lose weight":
        target, target_note = maintain - 400, "about 400 kcal below maintenance for steady loss"
    elif goal == "Build muscle":
        target, target_note = maintain + 300, "about 300 kcal above maintenance for lean gain"
    else:
        target, target_note = maintain, "maintenance"
    target = max(target, 1200 if gender == "Female" else 1500)  # never suggest a crash diet
    low, high = healthy_weight_range(height_cm)
    return {
        "bmi": round(bmi, 1), "category": label, "colour": colour,
        "healthy_low": low, "healthy_high": high,
        "bmr": round(bmr), "maintain": maintain, "target": target, "target_note": target_note,
        "water_l": round(weight_kg * 0.035, 1),
        "protein_low": round(weight_kg * 1.4), "protein_high": round(weight_kg * 2.0),
        "to_healthy": (0 if low <= weight_kg <= high else round(weight_kg - (high if weight_kg > high else low), 1)),
    }


def bmi_marker_percent(bmi):
    """Position (0 to 100) of the marker on a bar that spans BMI 15 to 40."""
    return max(0, min(100, (bmi - 15) / 25 * 100))


def health_advice(result):
    """Short, general advice lines. Never a diagnosis."""
    c = result["category"]
    lines = []
    if c == "Underweight":
        lines.append("Your BMI is below the usual range. Eat regular, balanced meals with enough protein and build strength gradually.")
    elif c == "Normal weight":
        lines.append("Your BMI is in the usual range. Focus on consistent training, sleep and a balanced diet.")
    elif c == "Overweight":
        lines.append("Your BMI is above the usual range. Regular exercise and a modest calorie deficit work better than quick fixes.")
    else:
        lines.append("Your BMI is well above the usual range. Start with low-impact exercise and consider talking to a doctor or dietitian first.")
    lines.append("BMI does not measure muscle or body fat. People with a lot of muscle can show a high BMI while being healthy, "
                 "and South Asians can carry higher health risk at a lower BMI.")
    return lines


EXPERIENCE = ["Beginner (new to the gym)", "Intermediate (6 months or more)", "Advanced (2 years or more)"]

_SPLITS = {
    2: ["Full body", "Full body"],
    3: ["Full body", "Full body", "Full body"],
    4: ["Upper body", "Lower body", "Upper body", "Lower body"],
    5: ["Push", "Pull", "Legs", "Upper body", "Lower body"],
    6: ["Push", "Pull", "Legs", "Push", "Pull", "Legs"],
}


def weekly_plan(experience, days, goal):
    """A simple starter week: list of (day, focus). General guidance, not a prescription."""
    days = max(2, min(6, days))
    if experience.startswith("Beginner"):
        days = min(days, 3)
    focus = list(_SPLITS[days])
    if goal == "Lose weight":
        extra = "plus 15 to 20 minutes of brisk walking or cycling"
    elif goal == "Build muscle":
        extra = "plus progressive overload (add a little weight or a rep each week)"
    else:
        extra = "plus 10 minutes of stretching"
    slots = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    step = {2: [0, 3], 3: [0, 2, 4], 4: [0, 1, 3, 4], 5: [0, 1, 2, 3, 4], 6: [0, 1, 2, 3, 4, 5]}[days]
    return [(slots[i], f"{f}, {extra}") for i, f in zip(step, focus)]


def plan_for(goal, months_commit):
    """Recommend a plan for a goal and a commitment (3, 6, 12 months, or 0 for not sure)."""
    return recommend_plan("Just trying the gym" if goal == "Just trying the gym" else goal,
                          {0: "Not sure yet", 3: "About 3 months", 6: "About 6 months", 12: "A year or more"}[months_commit])


# ---------------------------------------------------------------- readiness check: next steps
# Fixed, general guidance for each PAR-Q question answered Yes. Nothing here is sent to any outside service.
# topic: short label used when the visitor asks Arnold about the result (worded so it is not an emergency phrase).
PARQ_GUIDE = [
    {"topic": "a heart condition",
     "why": "A doctor has already said your activity should be supervised or recommended by them. Your heart may need monitoring, "
            "so a gym programme should be agreed with your doctor first.",
     "ask": ["Which activities and how hard can I exercise?", "Do I need a heart test (such as an ECG or a stress test) before I start?",
             "What heart rate or effort limit should I stay under?"],
     "avoid": "Heavy lifting, sprints and hard cardio"},
    {"topic": "chest discomfort during exercise",
     "why": "Pain or tightness in the chest during effort can mean the heart is not getting enough blood. It needs a medical check "
            "before you exercise.",
     "ask": ["What is causing the chest discomfort when I exercise?", "Which tests do I need before I start?"],
     "avoid": "Any hard exercise until you have been checked"},
    {"topic": "chest discomfort at rest",
     "why": "Chest pain when you are not exercising should always be checked by a doctor, because it can have serious causes.",
     "ask": ["What could be causing the chest discomfort I have at rest?", "Is it safe for me to exercise while this is being checked?"],
     "avoid": "Exercise of any kind that brings the discomfort back"},
    {"topic": "dizziness or loss of balance",
     "why": "Dizziness or losing consciousness can have many causes, some of them serious, and it can make falls with weights dangerous.",
     "ask": ["What is causing my dizziness or loss of balance?", "Is it safe for me to lift weights or use machines?"],
     "avoid": "Training alone, overhead lifts and sudden changes of position"},
    {"topic": "a bone or joint problem",
     "why": "Some bone and joint problems get worse with more activity, and the wrong movements can cause more damage.",
     "ask": ["Which movements and exercises should I avoid?", "Should I see a physiotherapist before I start training?"],
     "avoid": "High-impact moves and heavy loads on the affected joint"},
    {"topic": "medication for blood pressure or a heart condition",
     "why": "Some medicines change how your heart rate and blood pressure react to exercise, so your limits may be different from "
            "other people's.",
     "ask": ["How does my medicine affect exercise?", "What blood pressure and heart rate limits should I keep to?"],
     "avoid": "Sudden hard effort and holding your breath while lifting"},
    {"topic": "another medical reason",
     "why": "You know of another reason why exercise may not be safe for you. Your doctor should hear about it before you start.",
     "ask": ["Is it safe for me to exercise with this condition?", "Is there anything I should avoid?"],
     "avoid": "Anything beyond gentle walking until you have your doctor's advice"},
]

RED_FLAGS = ["Pain, pressure or tightness in the chest", "Pain spreading to the arm, jaw or back", "Severe breathlessness",
             "Fainting or feeling about to faint", "A racing or irregular heartbeat", "A cold sweat with any of the above"]

STARTER_STEPS = ["Warm up for 5 to 10 minutes before every session.", "Start with light weights and learn the correct form first.",
                 "Train 2 to 3 days a week and rest in between.", "Drink water and stop if you feel pain, dizziness or chest discomfort.",
                 "Ask a trainer to check your form in the first week."]


def parq_report(answers):
    """answers: list of 7 booleans (True = yes). Returns everything the results page shows."""
    flagged = [i for i, a in enumerate(answers) if a]
    if not flagged:
        return {"needs_doctor": False, "flagged": [], "steps": STARTER_STEPS}
    seen, questions = set(), []
    for i in flagged:
        for q in PARQ_GUIDE[i]["ask"]:
            if q not in seen:
                seen.add(q)
                questions.append(q)
    topics = [PARQ_GUIDE[i]["topic"] for i in flagged]
    return {
        "needs_doctor": True,
        "flagged": [{"question": PARQ[i], "why": PARQ_GUIDE[i]["why"], "topic": PARQ_GUIDE[i]["topic"]} for i in flagged],
        "doctor_questions": questions,
        "do": ["Gentle walking on flat ground, only if your doctor says it is fine", "Light stretching while seated or lying down",
               "Tell the gym team that you are waiting for a doctor's advice"],
        "avoid": [PARQ_GUIDE[i]["avoid"] for i in flagged],
        "red_flags": RED_FLAGS,
        "arnold_question": ("I am getting ready to start gym training. A safe-to-train check showed I may have: " + "; ".join(topics) +
                            ". What should I ask my doctor, and what can I safely do until I have seen them?"),
    }


def parq_text(answers, today=None):
    """Plain-text copy of the readiness result, for the visitor to download and take to a doctor."""
    from datetime import date
    r = parq_report(answers)
    out = ["TA Fitness - Safe-to-Train Check (based on the PAR-Q)", f"Date: {(today or date.today()):%d %B %Y}", "", "Your answers:"]
    out += [f"  [{'YES' if a else 'no '}] {q}" for q, a in zip(PARQ, answers)]
    out.append("")
    if not r["needs_doctor"]:
        out += ["Result: no warning signs in your answers. This is not a medical check.", "", "Your starter plan:"]
        out += [f"  {i}. {s}" for i, s in enumerate(r["steps"], 1)]
    else:
        out += ["Result: please see a doctor before you start exercising.", "", "Why this matters:"]
        for f in r["flagged"]:
            out += [f"  - {f['question']}", f"    {f['why']}"]
        out += ["", "Questions to ask your doctor:"] + [f"  {i}. {q}" for i, q in enumerate(r["doctor_questions"], 1)]
        out += ["", "Until you see your doctor, usually fine:"] + [f"  - {t}" for t in r["do"]]
        out += ["", "Avoid for now:"] + [f"  - {t}" for t in dict.fromkeys(r["avoid"])]
        out += ["", "Stop and get help now (call 112) if you have:"] + [f"  - {t}" for t in r["red_flags"]]
    out += ["", DISCLAIMER]
    return "\n".join(out) + "\n"
