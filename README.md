# MonsoonCare

Expert system for monsoon illnesses, made with Python and Streamlit.

It covers dengue, malaria, chikungunya, typhoid, cholera, gastroenteritis, hepatitis A,
leptospirosis, flu, common cold, eye flu and fungal skin infection. The user enters symptoms,
and the system gives a diagnosis, a decision on how urgently to see a doctor, and advice.

It has 104 rules with 261 conditions and uses forward chaining with certainty factors.

This is an educational project and not a medical diagnosis. Always consult a doctor.

## Files

- `app.py` - Streamlit interface
- `engine.py` - inference engine (inferencing, diagnosis, decision making, decision support)
- `knowledge.py` - questions, diseases, rules and demo cases
- `models.py` - rule structure
- `requirements.txt` - libraries needed

## Run

```
pip install -r requirements.txt
streamlit run app.py
```

Live link: https://monsoonexpertsystem.streamlit.app/
