"""Health report check for the Safe-to-Train page.

A PDF report is read only inside this app (nothing is sent to any AI service and nothing is saved).
Six gym-relevant values are looked for, the visitor confirms or corrects them, and each value is
compared with published adult ranges. The result can only be "see a doctor before training" or
"these values do not flag anything" - never "you are fit". Arnold is given topic words only.

Sources of the ranges:
- Blood pressure: 2017 ACC/AHA Guideline for High Blood Pressure in Adults (Whelton et al., 2018).
- Fasting glucose and HbA1c: American Diabetes Association, Standards of Care in Diabetes,
  "Diagnosis and Classification of Diabetes".
- Total and LDL cholesterol: NCEP Adult Treatment Panel III (ATP III), 2002.
- Haemoglobin: WHO, Haemoglobin concentrations for the diagnosis of anaemia (WHO/NMH/NHD/MNM/11.1, 2011).
"""
import re

SOURCES = {
    "bp": "ACC/AHA 2017 blood pressure guideline",
    "sugar": "American Diabetes Association Standards of Care",
    "hba1c": "American Diabetes Association Standards of Care",
    "chol": "NCEP ATP III (2002)",
    "ldl": "NCEP ATP III (2002)",
    "hb": "WHO anaemia thresholds (2011)",
}

LABELS = {
    "bp": "Blood pressure", "sugar": "Fasting blood sugar", "hba1c": "HbA1c",
    "chol": "Total cholesterol", "ldl": "LDL cholesterol", "hb": "Haemoglobin",
}
UNITS = {"bp": "mmHg", "sugar": "mg/dL", "hba1c": "%", "chol": "mg/dL", "ldl": "mg/dL", "hb": "g/dL"}


# ---------------------------------------------------------------- reading a PDF
def pdf_text(data, max_pages=10):
    """Text of a PDF report (first pages only). Returns "" if the file has no readable text."""
    import pymupdf
    try:
        with pymupdf.open(stream=data, filetype="pdf") as doc:
            return "\n".join(page.get_text() for page in list(doc)[:max_pages])
    except Exception:
        return ""


_NUM = r"(\d{1,3}(?:\.\d{1,2})?)"


def _find(text, names, lo, hi):
    """First number after one of the names that falls within a sensible range."""
    for name in names:
        for m in re.finditer(name + r"[^0-9\n]{0,40}?" + _NUM, text, flags=re.IGNORECASE):
            value = float(m.group(1))
            if lo <= value <= hi:
                return value
    return None


def find_values(text):
    """Look for the six values in report text. Missing values are None."""
    values = {}
    bp = re.search(r"(?:blood\s*pressure|\bB\.?P\.?\b)[^0-9\n]{0,30}?(\d{2,3})\s*/\s*(\d{2,3})", text, flags=re.IGNORECASE)
    if bp and 70 <= int(bp.group(1)) <= 260 and 40 <= int(bp.group(2)) <= 160:
        values["sys"], values["dia"] = float(bp.group(1)), float(bp.group(2))
    values["sugar"] = _find(text, [r"fasting\s*(?:blood|plasma)?\s*(?:sugar|glucose)", r"\bFBS\b", r"\bFPG\b"], 30, 600)
    values["hba1c"] = _find(text, [r"HbA1c", r"glycated\s*ha?emoglobin", r"A1C"], 3, 20)
    values["chol"] = _find(text, [r"total\s*cholesterol", r"cholesterol,?\s*total", r"serum\s*cholesterol"], 70, 500)
    values["ldl"] = _find(text, [r"\bLDL\b(?:\s*cholesterol)?", r"low\s*density\s*lipoprotein"], 20, 400)
    values["hb"] = _find(text, [r"ha?emoglobin(?!\s*a1c)(?!\s*A1C)", r"\bHb\b(?!A1c)", r"\bHGB\b"], 3, 25)
    return values


# ---------------------------------------------------------------- comparing with the ranges
def _finding(key, value_text, category, flag, topic, questions):
    return {"key": key, "label": LABELS[key], "value": value_text, "category": category, "flag": flag,
            "topic": topic, "questions": questions, "source": SOURCES[key]}


def assess(values, gender="Male"):
    """Compare entered values with the ranges. Returns (findings, urgent).

    urgent is True for a blood pressure above 180/120, which needs medical care now, not gym advice.
    """
    findings, urgent = [], False
    sys_, dia = values.get("sys"), values.get("dia")
    if sys_ and dia:
        text = f"{sys_:.0f}/{dia:.0f} mmHg"
        if sys_ > 180 or dia > 120:
            urgent = True
            findings.append(_finding("bp", text, "Very high (hypertensive crisis range)", True, "very high blood pressure",
                                     ["Please get medical help today. Do not exercise until a doctor has seen you."]))
        elif sys_ >= 140 or dia >= 90:
            findings.append(_finding("bp", text, "High, stage 2", True, "high blood pressure (stage 2)",
                                     ["Is it safe for me to lift weights with this blood pressure?",
                                      "What blood pressure should I have before I start, and what heart rate limit should I keep?"]))
        elif sys_ >= 130 or dia >= 80:
            findings.append(_finding("bp", text, "High, stage 1", True, "high blood pressure (stage 1)",
                                     ["Can I start with light cardio and moderate weights?",
                                      "Should I check my blood pressure before and after training?"]))
        elif sys_ >= 120:
            findings.append(_finding("bp", text, "Elevated", False, "", []))
        else:
            findings.append(_finding("bp", text, "Normal", False, "", []))

    s = values.get("sugar")
    if s:
        if s < 70:
            f = _finding("sugar", f"{s:.0f} mg/dL", "Low", True, "low blood sugar",
                         ["Why is my sugar low, and what should I eat before training?"])
        elif s >= 126:
            f = _finding("sugar", f"{s:.0f} mg/dL", "In the diabetes range", True, "high fasting blood sugar",
                         ["How should I time food and any medicine around my workouts?",
                          "Should I check my sugar before and after exercise?"])
        elif s >= 100:
            f = _finding("sugar", f"{s:.0f} mg/dL", "In the prediabetes range", True, "prediabetes",
                         ["How much exercise each week would help my sugar level?"])
        else:
            f = _finding("sugar", f"{s:.0f} mg/dL", "Normal", False, "", [])
        findings.append(f)

    a = values.get("hba1c")
    if a:
        if a >= 6.5:
            f = _finding("hba1c", f"{a:.1f} %", "In the diabetes range", True, "high HbA1c (diabetes range)",
                         ["Is my diabetes controlled enough to start training, and what should I watch for?"])
        elif a >= 5.7:
            f = _finding("hba1c", f"{a:.1f} %", "In the prediabetes range", True, "HbA1c in the prediabetes range",
                         ["How much exercise each week would help my HbA1c?"])
        else:
            f = _finding("hba1c", f"{a:.1f} %", "Normal", False, "", [])
        findings.append(f)

    c = values.get("chol")
    if c:
        if c >= 240:
            f = _finding("chol", f"{c:.0f} mg/dL", "High", True, "high total cholesterol",
                         ["Do I need a heart check (such as an ECG or stress test) before hard exercise?"])
        elif c >= 200:
            f = _finding("chol", f"{c:.0f} mg/dL", "Borderline high", True, "borderline high cholesterol",
                         ["Which type of exercise and diet will help my cholesterol most?"])
        else:
            f = _finding("chol", f"{c:.0f} mg/dL", "Desirable", False, "", [])
        findings.append(f)

    l = values.get("ldl")
    if l:
        if l >= 160:
            f = _finding("ldl", f"{l:.0f} mg/dL", "High" if l < 190 else "Very high", True, "high LDL cholesterol",
                         ["Is my heart risk high enough that I need a check before intense training?"])
        elif l >= 130:
            f = _finding("ldl", f"{l:.0f} mg/dL", "Borderline high", True, "borderline high LDL cholesterol",
                         ["How much cardio each week would help lower my LDL?"])
        else:
            f = _finding("ldl", f"{l:.0f} mg/dL", "Optimal or near optimal", False, "", [])
        findings.append(f)

    h = values.get("hb")
    if h:
        limit = 13.0 if gender == "Male" else 12.0
        if h < limit:
            f = _finding("hb", f"{h:.1f} g/dL", f"Low (below {limit:g} g/dL)", True, "low haemoglobin (possible anaemia)",
                         ["Could low haemoglobin make me dizzy or tired during workouts, and how should I build up?"])
        else:
            f = _finding("hb", f"{h:.1f} g/dL", "Normal", False, "", [])
        findings.append(f)
    return findings, urgent


def arnold_question(findings):
    """Question for Arnold made of topic words only: no numbers, no names, no report."""
    topics = [f["topic"] for f in findings if f["flag"] and f["topic"]]
    if not topics:
        return None
    return ("My health report shows: " + "; ".join(topics) + ". How do these affect gym training and heart attack risk, "
            "what kind of exercise is usually safer, and what should I ask my doctor before I start?")
