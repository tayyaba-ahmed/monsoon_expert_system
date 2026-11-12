# Streamlit interface: takes the patient's input and shows the decision, diagnosis and advice

import pandas as pd
import streamlit as st

from engine import (DISCLAIMER, DECISION_TEXT, ExpertSystem, build_facts,
                    format_report, MAX_CF)
from knowledge import (DISEASES, FACT_LABELS, PRESETS, RULES, SYMPTOM_GROUPS)

st.set_page_config(page_title="MonsoonCare Expert System", page_icon="🌧️", layout="wide")


# creates the engine only once instead of on every click
@st.cache_resource
def get_engine():
    return ExpertSystem()


ES = get_engine()

AGE_OPTIONS = ["Child (under 12)", "Adult (12-59)", "Elderly (60+)"]
AGE_KEY = {AGE_OPTIONS[0]: "child", AGE_OPTIONS[1]: "adult", AGE_OPTIONS[2]: "elderly"}
KIND_NAMES = {
    "derive": "Inference", "diagnose": "Diagnosis", "alert_urgent": "Urgent alert",
    "alert_doctor": "Doctor alert", "advice": "Advice",
}

# keeps the form values when streamlit reruns the script
defaults = {
    "unit": "°F", "temp_f": 98.6, "temp_c": 37.0, "fever_days": 0, "feels": False,
    "age": AGE_OPTIONS[1], "chronic": False, "pregnant": False, "analysed": False,
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)
for group in SYMPTOM_GROUPS.values():
    for key in group:
        st.session_state.setdefault(f"sym_{key}", False)


# fills the form with a demo case
def apply_preset(name):
    p = PRESETS[name]
    st.session_state["unit"] = "°F"
    st.session_state["temp_f"] = float(p["temp_f"])
    st.session_state["fever_days"] = int(p["days"])
    st.session_state["feels"] = False
    st.session_state["age"] = {"child": AGE_OPTIONS[0], "adult": AGE_OPTIONS[1],
                               "elderly": AGE_OPTIONS[2]}[p["age"]]
    st.session_state["chronic"] = False
    st.session_state["pregnant"] = False
    for group in SYMPTOM_GROUPS.values():
        for key in group:
            st.session_state[f"sym_{key}"] = key in p["symptoms"]
    st.session_state["analysed"] = True


# clears the form
def reset_all():
    for k, v in defaults.items():
        st.session_state[k] = v
    for group in SYMPTOM_GROUPS.values():
        for key in group:
            st.session_state[f"sym_{key}"] = False


# sidebar
with st.sidebar:
    st.header("🌧️ MonsoonCare")
    st.write("A rule-based **expert system** for monsoon illnesses. It uses "
             "**inferencing** to reach a **diagnosis**, makes a **decision** on how urgently "
             "to seek care, and works as a **decision support system** by showing its reasons.")
    st.metric("Rules in knowledge base", len(RULES))
    st.metric("Conditions the system can suspect", len(DISEASES))
    st.caption("Forward chaining + certainty factors. "
               f"Certainty is capped at {MAX_CF:.0%}: the system is never 100% sure.")
    st.divider()
    st.warning("Not a medical diagnosis. Always consult a doctor.")

st.title("🌧️ MonsoonCare - Monsoon Illness Diagnosis & Decision Support Expert System")
st.caption("Dengue · Malaria · Chikungunya · Typhoid · Cholera · Gastroenteritis · Hepatitis A · "
           "Leptospirosis · Flu · Cold · Eye flu · Fungal skin infection")

tab_diag, tab_how, tab_kb = st.tabs(["🩺 Diagnosis & Decision", "⚙️ How it works", "📚 Knowledge base"])

# main tab: patient form and results
with tab_diag:
    st.warning(DISCLAIMER)

    with st.expander("Try a demo case", expanded=False):
        choice = st.selectbox("Demo case", list(PRESETS), key="preset_choice")
        st.button("Load and analyse this case", on_click=apply_preset, args=(choice,))

    st.subheader("1. About the patient")
    c1, c2 = st.columns(2)
    with c1:
        st.radio("Age group", AGE_OPTIONS, key="age", horizontal=True)
        st.checkbox("Has a long-term illness (diabetes, heart, kidney, liver, low immunity)", key="chronic")
        st.checkbox("Pregnant", key="pregnant")
    with c2:
        st.radio("Temperature unit", ["°F", "°C"], key="unit", horizontal=True)
        if st.session_state["unit"] == "°F":
            st.slider("Body temperature (°F)", 95.0, 108.0, step=0.1, format="%.1f", key="temp_f")
            temp_f = st.session_state["temp_f"]
        else:
            st.slider("Body temperature (°C)", 35.0, 42.2, step=0.1, format="%.1f", key="temp_c")
            temp_f = st.session_state["temp_c"] * 9 / 5 + 32
        st.checkbox("Temperature not measured, but feels feverish", key="feels")
        st.slider("Days of fever so far", 0, 14, key="fever_days")

    st.subheader("2. Symptoms and exposures")
    st.caption("Tick everything that applies.")
    for i, (group, items) in enumerate(SYMPTOM_GROUPS.items()):
        with st.expander(group, expanded=(i < 2)):
            cols = st.columns(2)
            for j, (key, label) in enumerate(items.items()):
                cols[j % 2].checkbox(label, key=f"sym_{key}")

    b1, b2 = st.columns([3, 1])
    if b1.button("🔍 Diagnose", type="primary", use_container_width=True):
        st.session_state["analysed"] = True
    b2.button("Reset", on_click=reset_all, use_container_width=True)

    # results: form input becomes base facts, then the engine runs
    if st.session_state["analysed"]:
        selected = [k for g in SYMPTOM_GROUPS.values() for k in g
                    if st.session_state.get(f"sym_{k}")]
        facts = build_facts(
            temperature_f=temp_f,
            fever_days=st.session_state["fever_days"],
            feels_feverish=st.session_state["feels"],
            selected=selected,
            age_group=AGE_KEY[st.session_state["age"]],
            chronic=st.session_state["chronic"],
            pregnant=st.session_state["pregnant"],
        )
        result = ES.decision_support(facts)

        st.divider()
        st.subheader("3. Decision")
        st.caption("Decision making: what the system recommends you do.")

        if result.decision == "urgent":
            st.error(f"🚨 **{DECISION_TEXT['urgent']}**")
        elif result.decision == "doctor":
            st.warning(f"🩺 **{DECISION_TEXT['doctor']}**")
        else:
            st.success(f"🏠 **{DECISION_TEXT['monitor']}**")

        if result.alerts:
            st.markdown("**Why this decision?**")
            for level, msg, rid in result.alerts:
                icon = "🚨" if level == "urgent" else "🩺"
                st.markdown(f"- {icon} {msg} `{rid}`")

        st.subheader("4. Diagnosis")
        st.caption("Possible conditions, ranked. Certainty is a rule-based score, not a probability.")
        if not result.diagnoses:
            st.info("No condition matched the information given. This does not mean you are well - "
                    "if you feel unwell, please see a doctor.")
        for d in result.diagnoses[:5]:
            st.progress(float(d.cf), text=f"{d.name} - {d.cf:.0%} ({d.label})")
            with st.expander(f"About {d.name} and why it was suggested"):
                info = DISEASES[d.key]
                st.markdown(f"**What it is:** {info['about']}")
                st.markdown(f"**Tests a doctor may order:** {info['tests']}")
                st.markdown(f"**General care:** {info['care']}")
                st.markdown("**Rules that supported this:**")
                for rid, text, cf in ES.explain(d):
                    st.markdown(f"- `{rid}` (CF {cf:.2f}) {text}")

        st.subheader("5. Decision support")
        st.caption("Advice, the full reasoning, and a report you can show a doctor. "
                   "The final decision stays with you and your doctor.")
        if result.advice:
            st.markdown("#### Advice")
            for a in result.advice:
                st.markdown(f"- {a}")

        with st.expander(f"Inferencing trace - {result.rules_fired} rules fired, in order"):
            st.dataframe(pd.DataFrame(result.trace), use_container_width=True, hide_index=True)

        summary = [
            f"Age group: {st.session_state['age']}",
            f"Temperature: {temp_f:.1f} F, fever days: {st.session_state['fever_days']}",
            "Reported: " + (", ".join(FACT_LABELS[s] for s in selected) or "nothing selected"),
        ]
        st.download_button("⬇️ Download report", format_report(result, summary),
                           file_name="monsooncare_report.txt")

        st.info(DISCLAIMER)

# explains how the system works
with tab_how:
    st.markdown(f"""
### The four parts of this system
| Part | What it means | Where in the code | What you see |
|---|---|---|---|
| **Inferencing** | Drawing new conclusions from known facts by firing IF-THEN rules (forward chaining) | `ExpertSystem.infer()` | Inferencing trace |
| **Diagnosis** | Identifying the likely illness from symptoms and exposures, with a certainty score | `ExpertSystem.diagnose()` + `combine_cf()` | 4. Diagnosis (ranked conditions) |
| **Decision making** | Choosing the action: urgent care now, see a doctor in 24 hours, or home monitoring | `ExpertSystem.make_decision()` | 3. Decision banner |
| **Decision support system** | Giving the decision *with its reasons*, advice and a report, so the patient and doctor make the final call | `ExpertSystem.decision_support()` + `explain()` | Why this decision?, supporting rules, 5. Decision support |

**Flow:** form → `build_facts()` → `decision_support()` → `infer()` → `diagnose()` → `make_decision()` → screen

### Architecture
**Knowledge base** → **Inference engine** → **Explanation facility** → **User interface**

1. **Knowledge base** (`knowledge.py`): {len(RULES)} IF-THEN production rules written by hand from
   public health guidance on monsoon illnesses.
2. **Inference engine** (`engine.py`): *forward chaining*. Rules fire when their conditions are true;
   new facts can trigger more rules until nothing new can be concluded.
3. **Certainty factors**: each diagnosis rule carries a certainty (CF). Evidence for the same
   condition is combined with `CF = CF1 + CF2 × (1 − CF1)` and capped at {MAX_CF:.0%}.
4. **Negation as failure**: rules can say *NOT fact*. A rule is blocked if the fact is present,
   e.g. eye discharge blocks the leptospirosis red-eye rule.
5. **Decision making**: urgent alerts → hospital now; doctor alerts or a strong match → see a doctor within
   about 24 hours; otherwise home care with monitoring. A disclaimer is shown every time.
6. **Explanation (decision support)**: every result shows which rules fired and in what order.

### Rule types
| Type | Purpose | Example |
|---|---|---|
| Inference | Build higher-level facts | dry mouth AND little urine ⇒ *dehydration* |
| Diagnosis | Add evidence for a condition | high fever AND pain behind eyes AND severe body ache ⇒ dengue (CF 0.55) |
| Urgent alert | Emergency warnings | confusion AND fever ⇒ urgent |
| Doctor alert | Needs a doctor soon | fever for 3+ days ⇒ get tested |
| Advice | Prevention and home care | stagnant water ⇒ empty containers weekly |

### Limitations
Rule-based systems only know what their rules say. They cannot examine you, run tests, or notice
what they were not told. They are screening aids, **not** a replacement for a doctor.
""")

# shows all rules in a table
with tab_kb:
    n_cond = sum(r.n_conditions for r in RULES)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Rules", len(RULES))
    m2.metric("Conditions in rules", n_cond)
    m3.metric("Questions asked", sum(len(g) for g in SYMPTOM_GROUPS.values()))
    m4.metric("Conditions suspected", len(DISEASES))

    kind_filter = st.selectbox("Show rule type", ["All"] + list(KIND_NAMES.values()))
    rows = []
    for rule in RULES:
        if kind_filter != "All" and KIND_NAMES[rule.kind] != kind_filter:
            continue
        rows.append({
            "ID": rule.id,
            "Type": KIND_NAMES[rule.kind],
            "Rule": rule.as_text(FACT_LABELS),
            "CF": rule.cf if rule.kind == "diagnose" else None,
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
