# Rule structure used by the knowledge base

from dataclasses import dataclass


# one IF-THEN rule, frozen so it cannot be changed after it is made
@dataclass(frozen=True)
class Rule:
    id: str            # like "DX-01"
    kind: str          # derive, diagnose, alert_urgent, alert_doctor or advice
    then: str          # what the rule concludes
    all_of: tuple = ()
    any_of: tuple = ()
    none_of: tuple = ()
    cf: float = 1.0    # certainty, only used by diagnose rules
    text: str = ""     # message for alert and advice rules

    # total number of conditions in this rule
    @property
    def n_conditions(self) -> int:
        return len(self.all_of) + len(self.any_of) + len(self.none_of)

    # writes the rule as readable IF THEN text for the app
    def as_text(self, labels: dict) -> str:
        def lab(c):
            if ">=" in c:
                name, thr = c.split(">=")
                return f"{labels.get(name, name)} (certainty >= {float(thr):.0%})"
            return labels.get(c, c)

        parts = [" AND ".join(lab(c) for c in self.all_of)] if self.all_of else []
        if self.any_of:
            parts.append("(" + " OR ".join(lab(c) for c in self.any_of) + ")")
        for c in self.none_of:
            parts.append("NOT " + lab(c))
        cond = " AND ".join(p for p in parts if p)

        if self.kind == "derive":
            then = f"infer '{labels.get(self.then, self.then)}'"
        elif self.kind == "diagnose":
            then = f"suspect {labels.get(self.then, self.then)} (CF {self.cf:.2f})"
        elif self.kind == "alert_urgent":
            then = "raise URGENT alert"
        elif self.kind == "alert_doctor":
            then = "raise SEE-A-DOCTOR alert"
        else:
            then = "give advice"
        return f"IF {cond} THEN {then}"
