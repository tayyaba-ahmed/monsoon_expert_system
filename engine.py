# Inference engine of MonsoonCare: inferencing, diagnosis, decision making and decision support

from dataclasses import dataclass

from knowledge import RULES, DISEASES, FACT_LABELS

MAX_CF = 0.95


# converts the form input into base facts
# numbers become facts too, like 102 F or more becomes high_fever
def build_facts(temperature_f=None, fever_days=0, feels_feverish=False,
                selected=(), age_group="adult", chronic=False, pregnant=False):
    facts = set(selected)

    if temperature_f is not None:
        if temperature_f >= 99.5:
            facts.add("fever")
        if temperature_f >= 102.0:
            facts.update({"fever", "high_fever"})
        if temperature_f >= 104.0:
            facts.update({"fever", "high_fever", "very_high_fever"})
    if feels_feverish:
        facts.add("fever")

    if "fever" in facts:
        if fever_days >= 3:
            facts.add("fever_3plus")
        if fever_days >= 7:
            facts.update({"fever_3plus", "fever_7plus"})

    if age_group == "child":
        facts.add("child")
    elif age_group == "elderly":
        facts.add("elderly")
    if chronic:
        facts.add("chronic_condition")
    if pregnant:
        facts.add("pregnant")
    return facts


# combines old and new certainty using the MYCIN formula old + new * (1 - old)
# capped at 0.95 because the system is never 100% sure
def combine_cf(old, new):
    return min(MAX_CF, old + new * (1.0 - old))


# turns the certainty number into words
def confidence_label(cf):
    if cf >= 0.70:
        return "Strong match"
    if cf >= 0.45:
        return "Moderate match"
    return "Possible match"


# one suspected disease with its certainty and the rules that supported it
@dataclass
class Diagnosis:
    key: str
    name: str
    cf: float
    rule_ids: list

    @property
    def label(self):
        return confidence_label(self.cf)


# full result of one run, app.py reads everything from this
@dataclass
class DecisionSupportResult:
    facts: dict
    diagnoses: list
    decision: str
    alerts: list
    advice: list
    trace: list
    rules_fired: int = 0

    # best diagnosis, or None if nothing matched
    @property
    def top(self):
        return self.diagnoses[0] if self.diagnoses else None


class ExpertSystem:
    def __init__(self, rules=RULES):
        self.rules = list(rules)

    # checks if one condition is true in the working memory
    @staticmethod
    def _holds(cond, facts):
        if ">=" in cond:
            name, thr = cond.split(">=")
            return facts.get(name, 0.0) >= float(thr)
        return facts.get(cond, 0.0) > 0.0

    # checks a whole rule: all_of must all be true, any_of needs one, none_of must all be false
    def _matches(self, rule, facts):
        if not all(self._holds(c, facts) for c in rule.all_of):
            return False
        if rule.any_of and not any(self._holds(c, facts) for c in rule.any_of):
            return False
        if any(self._holds(c, facts) for c in rule.none_of):
            return False
        return True

    # forward chaining: keeps firing matching rules until no new rule can fire
    # derived facts, disease scores, alerts and advice are collected on the way
    def infer(self, base_facts):
        facts = {f: 1.0 for f in base_facts}  # working memory
        fired = set()
        trace, alerts, advice = [], [], []

        progress = True
        while progress:
            progress = False
            for rule in self.rules:
                if rule.id in fired or not self._matches(rule, facts):
                    continue
                fired.add(rule.id)  # so the same rule never fires twice
                progress = True
                entry = {"step": len(trace) + 1, "rule": rule.id, "kind": rule.kind}

                # what happens depends on the kind of rule
                if rule.kind == "derive":
                    facts[rule.then] = 1.0
                    entry["result"] = f"inferred: {FACT_LABELS.get(rule.then, rule.then)}"
                elif rule.kind == "diagnose":
                    before = facts.get(rule.then, 0.0)
                    after = combine_cf(before, rule.cf)
                    facts[rule.then] = after
                    entry["result"] = (f"{DISEASES[rule.then]['name']}: "
                                       f"{before:.2f} -> {after:.2f}")
                elif rule.kind in ("alert_urgent", "alert_doctor"):
                    level = "urgent" if rule.kind == "alert_urgent" else "doctor"
                    alerts.append((level, rule.text, rule.id))
                    entry["result"] = f"{level} alert: {rule.text}"
                else:
                    if rule.text not in advice:
                        advice.append(rule.text)
                    entry["result"] = "advice added"
                trace.append(entry)

        return facts, trace, alerts, advice

    # makes a list of suspected diseases sorted by certainty, highest first
    def diagnose(self, facts, trace):
        return sorted(
            (Diagnosis(k, DISEASES[k]["name"], facts[k],
                       [t["rule"] for t in trace if t["kind"] == "diagnose"
                        and self._rule(t["rule"]).then == k])
             for k in DISEASES if facts.get(k, 0.0) > 0.0),
            key=lambda d: d.cf, reverse=True)

    # decides what the patient should do: urgent, doctor or monitor
    @staticmethod
    def make_decision(alerts, diagnoses):
        if any(a[0] == "urgent" for a in alerts):
            return "urgent"
        if any(a[0] == "doctor" for a in alerts) or (diagnoses and diagnoses[0].cf >= 0.5):
            return "doctor"
        return "monitor"

    # main function called by app.py, runs inference, diagnosis and decision in order
    def decision_support(self, base_facts):
        facts, trace, alerts, advice = self.infer(base_facts)
        diagnoses = self.diagnose(facts, trace)
        decision = self.make_decision(alerts, diagnoses)
        return DecisionSupportResult(facts, diagnoses, decision, alerts, advice, trace, len(trace))

    # finds a rule by its id
    def _rule(self, rule_id):
        return next(r for r in self.rules if r.id == rule_id)

    # returns the rules that supported a diagnosis, used to show why it was suggested
    def explain(self, diagnosis):
        out = []
        for rid in diagnosis.rule_ids:
            rule = self._rule(rid)
            out.append((rid, rule.as_text(FACT_LABELS), rule.cf))
        return out


DISCLAIMER = ("This tool is an educational expert system based on a limited set of rules. "
              "It is NOT a medical diagnosis and can be wrong. It can miss serious illness "
              "or suggest conditions you do not have. Always consult a qualified doctor, "
              "and seek emergency care immediately if you feel seriously unwell.")

DECISION_TEXT = {
    "urgent": "Seek urgent medical care now (hospital / emergency).",
    "doctor": "See a doctor within about 24 hours.",
    "monitor": "Home care and monitoring may be enough for now, but see a doctor if symptoms continue beyond 2 days or get worse.",
}


# makes the text report for the download button
def format_report(result, summary_lines):
    c = result
    lines = ["MONSOONCARE - DIAGNOSIS AND DECISION SUPPORT REPORT", "=" * 51, ""]
    lines += summary_lines + [""]
    lines += [f"Decision: {DECISION_TEXT[c.decision]}", ""]
    if c.alerts:
        lines.append("Reasons for the decision (alerts):")
        lines += [f"  - [{lvl.upper()}] {msg} ({rid})" for lvl, msg, rid in c.alerts]
        lines.append("")
    lines.append("Diagnosis - possible conditions (certainty is not probability):")
    if c.diagnoses:
        for d in c.diagnoses[:5]:
            lines.append(f"  - {d.name}: {d.cf:.0%} ({d.label})")
    else:
        lines.append("  - No condition matched the information given.")
    lines.append("")
    if c.advice:
        lines.append("Advice:")
        lines += [f"  - {a}" for a in c.advice]
        lines.append("")
    lines += ["DISCLAIMER", DISCLAIMER]
    return "\n".join(lines)
