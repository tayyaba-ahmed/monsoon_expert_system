# Knowledge base: questions, diseases, rules and demo cases

from models import Rule


# short helper to write rules
def r(id, kind, then, *, all_of=(), any_of=(), none_of=(), cf=1.0, text=""):
    return Rule(id, kind, then, tuple(all_of), tuple(any_of), tuple(none_of), cf, text)


# questions asked from the user (base facts)
SYMPTOM_GROUPS = {
    "Fever pattern": {
        "chills_rigors": "Shaking chills / rigors",
        "fever_cycles": "Fever that comes and goes in cycles (every 1-3 days)",
        "stepladder_fever": "Fever rising a little higher every day",
        "drenching_sweats": "Drenching sweats when the fever breaks",
    },
    "Head, body and joints": {
        "headache": "Headache",
        "retro_orbital_pain": "Pain behind the eyes",
        "body_ache": "General body ache",
        "severe_body_ache": "Severe 'bone-breaking' body ache",
        "severe_joint_pain": "Severe joint pain",
        "swollen_joints": "Swollen joints",
        "calf_pain": "Calf muscle pain / tenderness",
        "leg_cramps": "Painful muscle cramps in legs",
        "fatigue": "Marked tiredness / weakness",
        "dizziness": "Dizziness on standing",
    },
    "Stomach and digestion": {
        "nausea": "Nausea",
        "vomiting": "Vomiting",
        "persistent_vomiting": "Repeated vomiting, cannot keep fluids down",
        "loose_stools": "Loose stools / diarrhoea",
        "rice_water_stools": "Very watery, pale 'rice-water' stools",
        "blood_in_stool": "Blood in stool",
        "abdominal_pain": "Stomach pain",
        "severe_abdominal_pain": "Severe, continuous stomach pain",
        "constipation": "Constipation",
        "loss_appetite": "Loss of appetite",
        "jaundice": "Yellow eyes or skin",
        "dark_urine": "Dark (tea-coloured) urine",
    },
    "Dehydration signs": {
        "dry_mouth": "Very dry mouth / extreme thirst",
        "sunken_eyes": "Sunken eyes",
        "reduced_urine": "Passing much less urine than usual",
    },
    "Throat, nose and chest": {
        "sore_throat": "Sore throat",
        "runny_nose": "Runny nose",
        "sneezing": "Sneezing",
        "cough": "Cough",
        "breathlessness": "Difficulty breathing / breathlessness",
    },
    "Eyes and skin": {
        "red_eyes": "Red eyes",
        "eye_discharge": "Sticky eye discharge",
        "itchy_eyes": "Itchy / watery eyes",
        "rash": "Skin rash (red spots / flushing)",
        "bleeding": "Bleeding gums / nose or easy bruising",
        "itchy_skin": "Itchy skin",
        "ring_rash": "Ring-shaped, scaly skin patches",
        "foot_skin_cracks": "Cracked / whitish, itchy skin between toes or on soles",
    },
    "Mind and nerves": {
        "confusion": "Confusion or unusual drowsiness",
        "stiff_neck": "Stiff neck",
    },
    "Exposures (last 2 weeks)": {
        "stagnant_water": "Stagnant water around home / workplace",
        "mosquito_bites": "Many mosquito bites",
        "untreated_water": "Drank untreated / unboiled water",
        "street_food": "Ate street food or uncooked / cut food",
        "floodwater_contact": "Walked or waded in rain / flood water",
        "rodent_contact": "Contact with rodents, their urine, or dirty water",
        "sick_contact": "Close contact with someone who is ill",
        "rain_drenched": "Clothes or shoes stayed wet for long",
    },
}

# names for facts that rules infer
DERIVED_LABELS = {
    "fever": "Fever (>= 99.5 F / 37.5 C)",
    "high_fever": "High fever (>= 102 F / 38.9 C)",
    "very_high_fever": "Very high fever (>= 104 F / 40 C)",
    "fever_3plus": "Fever lasting 3 or more days",
    "fever_7plus": "Fever lasting 7 or more days",
    "child": "Child (under 12)",
    "elderly": "Elderly (60+)",
    "chronic_condition": "Has a chronic condition",
    "pregnant": "Pregnant",
    "dehydration": "Signs of dehydration",
    "mosquito_exposure": "Mosquito exposure",
    "fecal_oral_exposure": "Contaminated food / water exposure",
    "flood_exposure": "Flood / contaminated-water exposure",
    "vulnerable": "High-risk patient (child / elderly / chronic / pregnant)",
    "respiratory_symptoms": "Respiratory symptoms",
    "gi_symptoms": "Stomach / bowel symptoms",
    "dengue_warning_signs": "Dengue warning signs",
    "neuro_danger": "Neurological danger signs",
    "joint_involvement": "Joint involvement",
}

# diseases the system can suspect, with info shown to the user
DISEASES = {
    "dx_dengue": {
        "name": "Dengue fever",
        "about": "Mosquito-borne viral fever; breeds in clean stagnant water. Typical: high fever, pain behind eyes, severe body ache, rash.",
        "tests": "NS1 antigen (early), dengue IgM/IgG, CBC with platelet count.",
        "care": "Rest and plenty of fluids. Avoid aspirin/ibuprofen. Watch closely on days 3-7 as the fever falls.",
    },
    "dx_malaria": {
        "name": "Malaria",
        "about": "Parasite spread by Anopheles mosquitoes. Typical: chills, fever in cycles, heavy sweating.",
        "tests": "Malaria rapid test (ICT) and blood smear.",
        "care": "Needs a confirmed test and prescribed anti-malarial treatment. Do not self-medicate.",
    },
    "dx_chikungunya": {
        "name": "Chikungunya",
        "about": "Mosquito-borne viral illness. Typical: sudden fever with severe, often swollen joint pain and rash.",
        "tests": "Chikungunya IgM / PCR; doctors also rule out dengue.",
        "care": "Rest, fluids, doctor-advised pain relief. Joint pain can last weeks.",
    },
    "dx_typhoid": {
        "name": "Typhoid (enteric) fever",
        "about": "Bacterial infection from contaminated food or water. Typical: fever rising day by day, stomach pain, loss of appetite.",
        "tests": "Blood culture, Widal / Typhidot as advised.",
        "care": "Needs antibiotics prescribed by a doctor; fluids and soft food meanwhile.",
    },
    "dx_cholera": {
        "name": "Cholera / severe watery diarrhoea",
        "about": "Severe watery diarrhoea from contaminated water that can dehydrate within hours.",
        "tests": "Stool test; clinical assessment of dehydration.",
        "care": "Start ORS immediately and go to a clinic - drips may be needed.",
    },
    "dx_gastroenteritis": {
        "name": "Gastroenteritis (food / water infection)",
        "about": "Stomach infection causing vomiting, loose stools and cramps after unsafe food or water.",
        "tests": "Usually clinical; stool test if severe or prolonged.",
        "care": "ORS, small frequent sips, light food. See a doctor if it lasts beyond 2 days or blood appears.",
    },
    "dx_hepatitis_a": {
        "name": "Hepatitis A (jaundice)",
        "about": "Liver infection from contaminated food or water. Typical: yellow eyes, dark urine, tiredness, nausea.",
        "tests": "Liver function tests, Hepatitis A IgM.",
        "care": "Rest, light non-oily food, no alcohol, avoid self-medication; doctor must monitor.",
    },
    "dx_leptospirosis": {
        "name": "Leptospirosis",
        "about": "Bacterial infection from water contaminated with animal (rodent) urine - common after flooding.",
        "tests": "Leptospira IgM / PCR, kidney and liver tests.",
        "care": "Needs prompt antibiotics from a doctor - tell them about flood-water contact.",
    },
    "dx_influenza": {
        "name": "Influenza / viral fever",
        "about": "Viral illness with fever, cough, sore throat and body ache; spreads between people.",
        "tests": "Usually clinical; flu test if severe.",
        "care": "Rest, warm fluids, doctor-advised fever medicine. Stay away from others.",
    },
    "dx_common_cold": {
        "name": "Common cold",
        "about": "Mild viral infection of the nose and throat, common when wet or chilled.",
        "tests": "None usually needed.",
        "care": "Rest, warm fluids, steam. See a doctor if fever develops or it lasts over a week.",
    },
    "dx_conjunctivitis": {
        "name": "Conjunctivitis ('eye flu')",
        "about": "Eye infection that spreads fast in monsoon. Typical: red, watery or sticky eyes.",
        "tests": "Eye examination.",
        "care": "Do not rub eyes, wash hands often, do not share towels. Eye doctor may prescribe drops.",
    },
    "dx_fungal_skin": {
        "name": "Fungal skin infection (ringworm / foot rot)",
        "about": "Fungus grows on skin kept damp. Typical: ring-shaped itchy patches or cracked skin between toes.",
        "tests": "Skin examination, scraping if unclear.",
        "care": "Keep skin dry, change wet clothes and socks, do not share towels; doctor may prescribe antifungal cream.",
    },
}

FACT_LABELS = {}
for _g in SYMPTOM_GROUPS.values():
    FACT_LABELS.update(_g)
FACT_LABELS.update(DERIVED_LABELS)
FACT_LABELS.update({k: v["name"] for k, v in DISEASES.items()})

# facts that come directly from the user
BASE_FACTS = set(FACT_LABELS) - set(DISEASES) - {
    "dehydration", "mosquito_exposure", "fecal_oral_exposure", "flood_exposure",
    "vulnerable", "respiratory_symptoms", "gi_symptoms", "dengue_warning_signs",
    "neuro_danger", "joint_involvement",
}

# rule base
RULES = [
    # inference rules: make new facts from the input
    r("D-01", "derive", "dehydration", all_of=["dry_mouth", "reduced_urine"]),
    r("D-02", "derive", "dehydration", all_of=["dry_mouth", "sunken_eyes"]),
    r("D-03", "derive", "dehydration", all_of=["sunken_eyes", "reduced_urine"]),
    r("D-04", "derive", "dehydration", all_of=["dizziness", "reduced_urine"], any_of=["vomiting", "loose_stools"]),
    r("D-05", "derive", "mosquito_exposure", any_of=["stagnant_water", "mosquito_bites"]),
    r("D-06", "derive", "fecal_oral_exposure", any_of=["untreated_water", "street_food"]),
    r("D-07", "derive", "flood_exposure", any_of=["floodwater_contact", "rodent_contact"]),
    r("D-08", "derive", "vulnerable", any_of=["child", "elderly", "chronic_condition", "pregnant"]),
    r("D-09", "derive", "respiratory_symptoms", any_of=["cough", "sore_throat", "runny_nose", "sneezing"]),
    r("D-10", "derive", "gi_symptoms", any_of=["vomiting", "loose_stools", "abdominal_pain", "nausea"]),
    r("D-11", "derive", "dengue_warning_signs", any_of=["severe_abdominal_pain", "persistent_vomiting", "bleeding"]),
    r("D-12", "derive", "neuro_danger", any_of=["confusion", "stiff_neck"]),
    r("D-13", "derive", "joint_involvement", any_of=["severe_joint_pain", "swollen_joints"]),

    # diagnosis rules, each adds certainty to a disease
    # Dengue
    r("DX-01", "diagnose", "dx_dengue", all_of=["high_fever", "retro_orbital_pain", "severe_body_ache"], cf=0.55),
    r("DX-02", "diagnose", "dx_dengue", all_of=["fever", "rash", "mosquito_exposure", "headache"], cf=0.40),
    r("DX-03", "diagnose", "dx_dengue", all_of=["high_fever", "mosquito_exposure", "severe_body_ache"], cf=0.40),
    r("DX-04", "diagnose", "dx_dengue", all_of=["fever", "bleeding", "mosquito_exposure"], cf=0.50),
    r("DX-05", "diagnose", "dx_dengue", all_of=["fever", "nausea", "headache", "mosquito_exposure", "fatigue"], cf=0.30),
    r("DX-06", "diagnose", "dx_dengue", all_of=["high_fever", "retro_orbital_pain", "rash"], cf=0.50),
    # Malaria
    r("DX-07", "diagnose", "dx_malaria", all_of=["chills_rigors", "fever", "mosquito_exposure"], cf=0.40),
    r("DX-08", "diagnose", "dx_malaria", all_of=["fever_cycles", "chills_rigors"], cf=0.55),
    r("DX-09", "diagnose", "dx_malaria", all_of=["fever", "drenching_sweats", "headache", "mosquito_exposure"], cf=0.40),
    r("DX-10", "diagnose", "dx_malaria", all_of=["fever_cycles", "mosquito_exposure", "fatigue"], cf=0.40),
    r("DX-11", "diagnose", "dx_malaria", all_of=["chills_rigors", "vomiting", "headache", "high_fever"], cf=0.30),
    # Chikungunya
    r("DX-12", "diagnose", "dx_chikungunya", all_of=["fever", "severe_joint_pain", "mosquito_exposure"], cf=0.55),
    r("DX-13", "diagnose", "dx_chikungunya", all_of=["joint_involvement", "rash", "fever"], cf=0.50),
    r("DX-14", "diagnose", "dx_chikungunya", all_of=["high_fever", "severe_joint_pain", "rash"], cf=0.50),
    # Typhoid
    r("DX-15", "diagnose", "dx_typhoid", all_of=["fever_3plus", "abdominal_pain", "fecal_oral_exposure"], cf=0.50),
    r("DX-16", "diagnose", "dx_typhoid", all_of=["fever_3plus", "headache", "loss_appetite", "fecal_oral_exposure"], cf=0.45),
    r("DX-17", "diagnose", "dx_typhoid", all_of=["fever_3plus", "constipation", "abdominal_pain"], cf=0.45),
    r("DX-18", "diagnose", "dx_typhoid", all_of=["fever_7plus", "fatigue", "fecal_oral_exposure"], cf=0.40),
    r("DX-19", "diagnose", "dx_typhoid", all_of=["stepladder_fever", "fever_3plus"], cf=0.50),
    # Cholera
    r("DX-20", "diagnose", "dx_cholera", all_of=["rice_water_stools", "dehydration"], cf=0.70),
    r("DX-21", "diagnose", "dx_cholera", all_of=["loose_stools", "vomiting", "fecal_oral_exposure", "dehydration"], cf=0.50),
    r("DX-22", "diagnose", "dx_cholera", all_of=["rice_water_stools", "fecal_oral_exposure"], cf=0.55),
    r("DX-23", "diagnose", "dx_cholera", all_of=["loose_stools", "leg_cramps", "dehydration"], none_of=["high_fever"], cf=0.45),
    # Gastroenteritis
    r("DX-24", "diagnose", "dx_gastroenteritis", all_of=["vomiting", "loose_stools", "fecal_oral_exposure"], cf=0.55),
    r("DX-25", "diagnose", "dx_gastroenteritis", all_of=["abdominal_pain", "loose_stools", "nausea"], cf=0.40),
    r("DX-26", "diagnose", "dx_gastroenteritis", all_of=["vomiting", "loose_stools", "sick_contact"], cf=0.35),
    r("DX-27", "diagnose", "dx_gastroenteritis", all_of=["nausea", "vomiting", "abdominal_pain", "street_food"], none_of=["jaundice"], cf=0.40),
    # Hepatitis A
    r("DX-28", "diagnose", "dx_hepatitis_a", all_of=["jaundice", "dark_urine"], cf=0.60),
    r("DX-29", "diagnose", "dx_hepatitis_a", all_of=["jaundice", "fecal_oral_exposure", "fatigue"], cf=0.55),
    r("DX-30", "diagnose", "dx_hepatitis_a", all_of=["loss_appetite", "nausea", "dark_urine", "fecal_oral_exposure"], cf=0.50),
    r("DX-31", "diagnose", "dx_hepatitis_a", all_of=["fatigue", "loss_appetite", "nausea", "fecal_oral_exposure"], none_of=["loose_stools"], cf=0.30),
    # Leptospirosis
    r("DX-32", "diagnose", "dx_leptospirosis", all_of=["flood_exposure", "high_fever", "calf_pain"], cf=0.65),
    r("DX-33", "diagnose", "dx_leptospirosis", all_of=["flood_exposure", "fever", "red_eyes"], none_of=["eye_discharge"], cf=0.50),
    r("DX-34", "diagnose", "dx_leptospirosis", all_of=["flood_exposure", "fever", "jaundice"], cf=0.60),
    r("DX-35", "diagnose", "dx_leptospirosis", all_of=["flood_exposure", "fever", "severe_body_ache", "chills_rigors"], cf=0.40),
    r("DX-36", "diagnose", "dx_leptospirosis", all_of=["rodent_contact", "fever", "headache"], cf=0.45),
    # Influenza
    r("DX-37", "diagnose", "dx_influenza", all_of=["fever", "cough", "body_ache", "sore_throat"], cf=0.55),
    r("DX-38", "diagnose", "dx_influenza", all_of=["fever", "runny_nose", "sneezing", "headache"], cf=0.40),
    r("DX-39", "diagnose", "dx_influenza", all_of=["high_fever", "cough", "fatigue", "sick_contact"], cf=0.50),
    r("DX-40", "diagnose", "dx_influenza", all_of=["respiratory_symptoms", "fever", "sick_contact"], cf=0.35),
    r("DX-41", "diagnose", "dx_influenza", all_of=["respiratory_symptoms", "body_ache", "fatigue"], cf=0.30),
    # Common cold
    r("DX-42", "diagnose", "dx_common_cold", all_of=["runny_nose", "sneezing"], none_of=["high_fever"], cf=0.55),
    r("DX-43", "diagnose", "dx_common_cold", all_of=["sore_throat", "runny_nose"], none_of=["fever"], cf=0.45),
    r("DX-44", "diagnose", "dx_common_cold", all_of=["cough", "runny_nose", "rain_drenched"], none_of=["high_fever"], cf=0.35),
    # Conjunctivitis
    r("DX-45", "diagnose", "dx_conjunctivitis", all_of=["red_eyes", "eye_discharge"], cf=0.65),
    r("DX-46", "diagnose", "dx_conjunctivitis", all_of=["red_eyes", "itchy_eyes", "sick_contact"], cf=0.50),
    r("DX-47", "diagnose", "dx_conjunctivitis", all_of=["red_eyes", "eye_discharge", "sick_contact"], cf=0.75),
    # Fungal skin infection
    r("DX-48", "diagnose", "dx_fungal_skin", all_of=["ring_rash", "itchy_skin"], cf=0.70),
    r("DX-49", "diagnose", "dx_fungal_skin", all_of=["itchy_skin", "rain_drenched"], none_of=["fever"], cf=0.35),
    r("DX-50", "diagnose", "dx_fungal_skin", all_of=["foot_skin_cracks", "rain_drenched"], cf=0.50),
    r("DX-51", "diagnose", "dx_fungal_skin", all_of=["foot_skin_cracks", "floodwater_contact"], cf=0.55),
    r("DX-52", "diagnose", "dx_fungal_skin", all_of=["ring_rash", "rain_drenched"], cf=0.50),

    # urgent alerts
    r("AU-01", "alert_urgent", "alert_urgent", all_of=["dengue_warning_signs", "fever"],
      text="Severe belly pain, repeated vomiting or bleeding with fever are dengue warning signs."),
    r("AU-02", "alert_urgent", "alert_urgent", all_of=["neuro_danger", "fever"],
      text="Confusion, drowsiness or stiff neck with fever can mean the brain or its lining is involved."),
    r("AU-03", "alert_urgent", "alert_urgent", all_of=["breathlessness", "fever"],
      text="Difficulty breathing with fever needs urgent assessment."),
    r("AU-04", "alert_urgent", "alert_urgent", all_of=["dehydration", "vulnerable"],
      text="Dehydration is dangerous in children, the elderly, pregnancy and chronic illness."),
    r("AU-05", "alert_urgent", "alert_urgent", all_of=["bleeding", "fever"],
      text="Bleeding together with fever may indicate severe dengue."),
    r("AU-06", "alert_urgent", "alert_urgent", all_of=["persistent_vomiting", "dehydration"],
      text="Cannot keep fluids down and already dehydrated - drips are likely needed."),
    r("AU-07", "alert_urgent", "alert_urgent", all_of=["very_high_fever"],
      text="Temperature of 104 F (40 C) or more is a medical emergency."),
    r("AU-08", "alert_urgent", "alert_urgent", all_of=["blood_in_stool", "fever"],
      text="Blood in stool with fever suggests a serious bowel infection."),
    r("AU-09", "alert_urgent", "alert_urgent", all_of=["jaundice", "confusion"],
      text="Yellow skin with confusion can mean liver failure."),
    r("AU-10", "alert_urgent", "alert_urgent", all_of=["flood_exposure", "jaundice", "reduced_urine"],
      text="Flood-water exposure with jaundice and low urine may be severe leptospirosis affecting liver and kidneys."),
    r("AU-11", "alert_urgent", "alert_urgent", all_of=["dx_cholera>=0.5"],
      text="Cholera-like diarrhoea can cause dangerous dehydration within hours."),
    r("AU-12", "alert_urgent", "alert_urgent", all_of=["persistent_vomiting", "vulnerable"],
      text="A child, elderly or high-risk person who cannot keep fluids down needs urgent care."),
    r("AU-13", "alert_urgent", "alert_urgent", all_of=["breathlessness", "flood_exposure"],
      text="Breathlessness after flood-water exposure can be a lung complication of leptospirosis."),

    # see a doctor alerts
    r("AD-01", "alert_doctor", "alert_doctor", all_of=["fever_3plus"],
      text="Fever for 3 or more days in monsoon should be tested (dengue, malaria, typhoid)."),
    r("AD-02", "alert_doctor", "alert_doctor", all_of=["fever", "vulnerable"],
      text="Fever in a child, elderly person, pregnancy or chronic illness should be seen by a doctor."),
    r("AD-03", "alert_doctor", "alert_doctor", all_of=["dehydration"],
      text="Signs of dehydration need medical review."),
    r("AD-04", "alert_doctor", "alert_doctor", all_of=["jaundice"],
      text="Yellow eyes or skin need liver tests."),
    r("AD-05", "alert_doctor", "alert_doctor", all_of=["fever", "rash", "mosquito_exposure"],
      text="Fever with rash after mosquito exposure should be tested for dengue / chikungunya."),
    r("AD-06", "alert_doctor", "alert_doctor", all_of=["chills_rigors", "mosquito_exposure", "fever"],
      text="Chills with fever after mosquito exposure needs a malaria test."),
    r("AD-07", "alert_doctor", "alert_doctor", all_of=["blood_in_stool"],
      text="Blood in stool should be examined by a doctor."),
    r("AD-08", "alert_doctor", "alert_doctor", all_of=["vomiting", "loose_stools", "vulnerable"],
      text="Vomiting and diarrhoea in a high-risk person can dehydrate quickly."),
    r("AD-09", "alert_doctor", "alert_doctor", all_of=["severe_abdominal_pain"],
      text="Severe stomach pain should be examined."),
    r("AD-10", "alert_doctor", "alert_doctor", all_of=["dx_dengue>=0.5"],
      text="Dengue is suspected: needs NS1/IgM test and platelet monitoring."),
    r("AD-11", "alert_doctor", "alert_doctor", all_of=["dx_leptospirosis>=0.5"],
      text="Leptospirosis is suspected: early antibiotics matter. Mention flood-water contact to the doctor."),
    r("AD-12", "alert_doctor", "alert_doctor", all_of=["dx_malaria>=0.5"],
      text="Malaria is suspected: needs a confirmed blood test before treatment."),
    r("AD-13", "alert_doctor", "alert_doctor", all_of=["dx_typhoid>=0.5"],
      text="Typhoid is suspected: needs blood tests and prescribed antibiotics."),
    r("AD-14", "alert_doctor", "alert_doctor", all_of=["dx_hepatitis_a>=0.5"],
      text="Hepatitis A is suspected: liver tests and medical monitoring needed."),
    r("AD-15", "alert_doctor", "alert_doctor", all_of=["dx_chikungunya>=0.5"],
      text="Chikungunya is suspected: a doctor should rule out dengue."),
    r("AD-16", "alert_doctor", "alert_doctor", all_of=["red_eyes", "fever"],
      text="Red eyes together with fever can be a sign of infection beyond the eye."),

    # advice rules
    r("AV-01", "advice", "advice", all_of=["mosquito_exposure"],
      text="Prevent mosquito bites: use nets or repellent, wear full sleeves, and empty coolers, tyres and flower-pot trays every week."),
    r("AV-02", "advice", "advice", all_of=["fecal_oral_exposure"],
      text="Drink only boiled or filtered water and avoid street food and cut fruit until you recover."),
    r("AV-03", "advice", "advice", all_of=["flood_exposure"],
      text="Avoid wading in flood water, cover any cuts, wash with soap and clean water afterwards, and tell your doctor about the exposure."),
    r("AV-04", "advice", "advice", all_of=["rain_drenched"],
      text="Change out of wet clothes and shoes quickly and keep feet and skin folds dry."),
    r("AV-05", "advice", "advice", any_of=["dehydration", "loose_stools"],
      text="Drink ORS (oral rehydration solution) in small, frequent sips."),
    r("AV-06", "advice", "advice", all_of=["fever"],
      text="Rest and drink plenty of fluids. Use fever medicine only as per label or doctor's advice, and avoid aspirin and ibuprofen until dengue is ruled out."),
    r("AV-07", "advice", "advice", all_of=["sick_contact"],
      text="Wash hands often, use a mask and keep your distance from others while you are unwell."),
    r("AV-08", "advice", "advice", any_of=["red_eyes", "eye_discharge"],
      text="Do not rub your eyes, wash hands often and do not share towels or pillows."),
    r("AV-09", "advice", "advice", all_of=["respiratory_symptoms"],
      text="Warm fluids, steam inhalation and rest help with throat and nose symptoms."),
    r("AV-10", "advice", "advice", all_of=["dx_dengue>=0.4"],
      text="If dengue is possible, watch for warning signs (severe belly pain, repeated vomiting, bleeding, extreme weakness) as the fever falls on days 3-7."),
]

# demo cases
PRESETS = {
    "Dengue-like case": dict(temp_f=103.5, days=4, age="adult",
        symptoms=["retro_orbital_pain", "severe_body_ache", "rash", "headache", "mosquito_bites", "stagnant_water"]),
    "Malaria-like case": dict(temp_f=103.0, days=3, age="adult",
        symptoms=["chills_rigors", "fever_cycles", "drenching_sweats", "headache", "mosquito_bites"]),
    "Typhoid-like case": dict(temp_f=102.5, days=8, age="adult",
        symptoms=["stepladder_fever", "abdominal_pain", "constipation", "loss_appetite", "headache", "untreated_water"]),
    "Cholera-like case": dict(temp_f=98.6, days=0, age="adult",
        symptoms=["rice_water_stools", "loose_stools", "vomiting", "dry_mouth", "reduced_urine", "leg_cramps", "untreated_water"]),
    "Leptospirosis-like case": dict(temp_f=103.0, days=3, age="adult",
        symptoms=["calf_pain", "red_eyes", "headache", "severe_body_ache", "chills_rigors", "floodwater_contact"]),
    "Flu-like case": dict(temp_f=100.8, days=2, age="adult",
        symptoms=["cough", "sore_throat", "body_ache", "sick_contact"]),
    "Eye flu case": dict(temp_f=98.6, days=0, age="child",
        symptoms=["red_eyes", "eye_discharge", "sick_contact"]),
    "Danger-sign case": dict(temp_f=104.6, days=3, age="adult",
        symptoms=["confusion", "headache", "mosquito_bites"]),
}
