import os
import joblib
import pandas as pd
import numpy as np
import streamlit as st

# Set Page Configuration
st.set_page_config(
    page_title="Titanic Survival Predictor",
    page_icon="🚢",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom styling for a premium dark/linear theme
st.markdown("""
    <style>
    .main {
        background-color: #0a0e1a;
        color: #f3f4f6;
    }
    .stButton>button {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        color: black;
        font-weight: bold;
        border: none;
        border-radius: 10px;
        padding: 10px 24px;
        width: 100%;
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.25);
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 242, 254, 0.4);
        color: black;
    }
    div[data-role="alert"] {
        border-radius: 12px;
    }
    .metric-card {
        background: rgba(30, 41, 67, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Cache model loading
@st.cache_resource
def load_model():
    model_path = os.path.join(os.path.dirname(__file__), 'titanic_model.pkl')
    try:
        return joblib.load(model_path)
    except Exception as e:
        st.error(f"Failed to load model from {model_path}: {e}")
        return None

model = load_model()

# Sidebar content
st.sidebar.image("static/images/titanic_hero.png" if os.path.exists("static/images/titanic_hero.png") else "https://img.icons8.com/color/96/titanic.png", use_container_width=True)
st.sidebar.title("About the Predictor")
st.sidebar.markdown("""
This application predicts whether a Titanic passenger would have survived the disaster based on their demographic and ticketing profile.

It uses a **Random Forest Classifier** trained on historical records.

### Historical Survival Rates:
* **Overall Survival:** ~38%
* **First Class:** ~62% survived
* **Third Class:** ~24% survived
* **Females:** ~74% survived
* **Males:** ~19% survived
""")

st.title("🚢 Titanic Survival Predictor")
st.markdown("Run real-time predictions using our trained classification pipeline.")

# Input Layout
st.subheader("Passenger Attributes")
col1, col2 = st.columns(2)

with col1:
    pclass_label = st.selectbox(
        "Ticket Class (Pclass)",
        ["1st Class (Upper Deck)", "2nd Class (Middle Deck)", "3rd Class (Lower Deck)"],
        index=2
    )
    # Map selection label to numeric Pclass
    pclass = 1 if "1st" in pclass_label else (2 if "2nd" in pclass_label else 3)
    
    sex = st.radio("Gender (Sex)", ["Male", "Female"], index=0).lower()
    
    embarked_label = st.selectbox(
        "Port of Embarkation",
        ["Southampton, UK", "Cherbourg, France", "Queenstown, Ireland"],
        index=0
    )
    # Map selection label to Embarked port abbreviation
    embarked = "S" if "Southampton" in embarked_label else ("C" if "Cherbourg" in embarked_label else "Q")

with col2:
    age = st.slider("Passenger Age (Years)", min_value=0, max_value=80, value=28, step=1)
    
    sibsp = st.number_input("Siblings / Spouses Aboard (SibSp)", min_value=0, max_value=10, value=0, step=1)
    
    parch = st.number_input("Parents / Children Aboard (Parch)", min_value=0, max_value=10, value=0, step=1)
    
    fare = st.slider("Ticket Fare Paid ($)", min_value=0.0, max_value=300.0, value=32.0, step=0.5)

# Engineered Features Calculations (Real-Time Display)
family_size = sibsp + parch + 1
is_alone = 1 if family_size == 1 else 0

st.markdown("---")
st.subheader("Calculated Features (Engineered)")
feat_col1, feat_col2 = st.columns(2)
with feat_col1:
    st.markdown(f"<div class='metric-card'><strong>Family Size:</strong> <span style='color:#00f2fe;font-weight:bold;'>{family_size}</span></div>", unsafe_allow_html=True)
with feat_col2:
    alone_status = "Yes" if is_alone == 1 else "No"
    st.markdown(f"<div class='metric-card'><strong>Traveling Alone?</strong> <span style='color:#00f2fe;font-weight:bold;'>{alone_status}</span></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Prediction Action
if st.button("Predict Survival"):
    if model is None:
        st.error("Model is not loaded. Please inspect logs.")
    else:
        # Create input DataFrame matching model pipeline columns
        input_df = pd.DataFrame([{
            'Pclass': pclass,
            'Sex': sex,
            'Age': float(age),
            'SibSp': int(sibsp),
            'Parch': int(parch),
            'Fare': float(fare),
            'Embarked': embarked,
            'FamilySize': family_size,
            'IsAlone': is_alone
        }])

        # Run inference
        prediction = int(model.predict(input_df)[0])
        probabilities = model.predict_proba(input_df)[0]
        survival_prob = float(probabilities[1])

        st.markdown("---")
        st.subheader("Prediction Result")

        if prediction == 1:
            st.success(f"### 🎉 Passenger Survived! (Survival Chance: {survival_prob:.1%})")
        else:
            st.error(f"### 😔 Passenger Deceased. (Survival Chance: {survival_prob:.1%})")

        # Key Model Insights
        st.markdown("#### Key Model Insights:")
        
        # Gender Info
        if sex == "female":
            st.info("🟢 **Gender Advantage:** Female passengers received priority boarding on lifeboats.")
        else:
            st.warning("🔴 **Gender Penalty:** Male passengers had historically low rescue rates under lifeboat rules.")

        # Class Info
        if pclass == 1:
            st.info("🟢 **Socio-Economic Advantage:** 1st Class passengers had direct deck access and higher rescue priority.")
        elif pclass == 3:
            st.warning("🔴 **Socio-Economic Penalty:** 3rd Class quarters faced slower evacuation due to lower deck positions.")
        
        # Family Info
        if family_size == 1:
            st.warning("🔴 **Alone Penalty:** Passengers traveling completely alone showed lower rates of coordinated rescue.")
        elif 2 <= family_size <= 4:
            st.info("🟢 **Family Advantage:** Moderate group size (2-4) supported mutual aid during boarding.")
        else:
            st.warning("🔴 **Large Family Penalty:** Coordinating large groups (5+) made finding lifeboat spaces challenging.")

        # Fare Info
        if fare > 100.0:
            st.info("🟢 **Fare Advantage:** Extremely high fare indicates VIP deck placement.")
