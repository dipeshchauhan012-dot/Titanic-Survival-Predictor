import os
import joblib
import pandas as pd
import numpy as np
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Titanic Survival Predictor",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS styling for a professional modern look
st.markdown("""
    <style>
    .reportview-container {
        background: #0f172a;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        color: #f8fafc;
    }
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #94a3b8;
        font-size: 1.15rem;
        margin-bottom: 2rem;
    }
    .card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .metric-title {
        font-size: 0.85rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.4rem;
        color: #38bdf8;
        font-weight: 700;
        margin-top: 4px;
    }
    .outcome-header {
        font-size: 1.6rem;
        font-weight: 700;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .outcome-survived {
        color: #10b981;
    }
    .outcome-deceased {
        color: #ef4444;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Model Loading Helper
@st.cache_resource
def load_titanic_model():
    model_path = os.path.join(os.path.dirname(__file__), 'titanic_model.pkl')
    if not os.path.exists(model_path):
        st.error(f"CRITICAL ERROR: Model file `{model_path}` not found in the directory.")
        return None
    try:
        return joblib.load(model_path)
    except Exception as e:
        st.error(f"CRITICAL ERROR: Failed to load model: {e}")
        return None

model = load_titanic_model()

# 4. Sidebar Input Panel
st.sidebar.markdown("## 🚢 Passenger Profile")
st.sidebar.markdown("Configure passenger characteristics below:")

pclass_opt = st.sidebar.selectbox(
    "Ticket Class (Pclass)",
    ["1st Class - Upper Deck", "2nd Class - Middle Deck", "3rd Class - Lower Deck"],
    index=2
)
# Map to model integer
pclass = 1 if "1st" in pclass_opt else (2 if "2nd" in pclass_opt else 3)

sex = st.sidebar.radio("Gender (Sex)", ["Male", "Female"], index=0).lower()

age = st.sidebar.slider("Age (Years)", min_value=0, max_value=80, value=28, step=1)

sibsp = st.sidebar.number_input("Siblings / Spouses Aboard (SibSp)", min_value=0, max_value=8, value=0, step=1)

parch = st.sidebar.number_input("Parents / Children Aboard (Parch)", min_value=0, max_value=6, value=0, step=1)

fare = st.sidebar.slider("Ticket Fare Paid ($)", min_value=0.0, max_value=512.0, value=32.0, step=0.5)

embarked_opt = st.sidebar.selectbox(
    "Port of Embarkation",
    ["Southampton, United Kingdom", "Cherbourg, France", "Queenstown, Ireland"],
    index=0
)
# Map to model abbreviation
embarked = "S" if "Southampton" in embarked_opt else ("C" if "Cherbourg" in embarked_opt else "Q")

# 5. Feature Engineering
family_size = sibsp + parch + 1
is_alone = 1 if family_size == 1 else 0

# 6. Main Dashboard Layout
st.markdown("<h1 class='main-title'>Titanic Survival Predictor</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>A machine learning dashboard utilizing a Random Forest Classifier to estimate passenger survival probability.</p>", unsafe_allow_html=True)

# 7. Passenger Summary Card (Main Panel)
st.markdown("### 📋 Passenger Profile Summary")
st.markdown("""
<div class='card'>
    This card shows the demographic features configured in the sidebar, along with real-time engineered feature inputs.
</div>
""", unsafe_allow_html=True)

sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)

with sum_col1:
    st.markdown("<div class='metric-title'>Class & Gender</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-value'>{pclass_opt.split(' - ')[0]} / {sex.capitalize()}</div>", unsafe_allow_html=True)

with sum_col2:
    st.markdown("<div class='metric-title'>Age & Fare</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-value'>{age} yrs / ${fare:.2f}</div>", unsafe_allow_html=True)

with sum_col3:
    st.markdown("<div class='metric-title'>Family Size</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-value'>{family_size} person(s)</div>", unsafe_allow_html=True)

with sum_col4:
    st.markdown("<div class='metric-title'>Travel Status</div>", unsafe_allow_html=True)
    alone_lbl = "Traveling Alone" if is_alone == 1 else "With Family"
    st.markdown(f"<div class='metric-value'>{alone_lbl}</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 8. Run Model Inference
st.markdown("### 📊 Prediction Engine")
if st.button("Analyze Survival Likelihood", type="primary"):
    if model is None:
        st.error("Model not available. Please verify model loading in logs.")
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

        # Perform prediction and probabilities
        try:
            prediction = int(model.predict(input_df)[0])
            probabilities = model.predict_proba(input_df)[0]
            
            non_survival_prob = float(probabilities[0])
            survival_prob = float(probabilities[1])
            
            # Confidence Score: probability of the predicted class
            confidence = survival_prob if prediction == 1 else non_survival_prob
            
            st.markdown("---")
            
            # Columns for graphical output and factor list
            res_col1, res_col2 = st.columns([1, 1])
            
            with res_col1:
                st.markdown("#### Outcome Status")
                if prediction == 1:
                    st.markdown("<div class='outcome-header outcome-survived'>🎉 Passenger Survived</div>", unsafe_allow_html=True)
                    st.success("The model predicts this passenger survived the disaster.")
                else:
                    st.markdown("<div class='outcome-header outcome-deceased'>❌ Passenger Deceased</div>", unsafe_allow_html=True)
                    st.error("The model predicts this passenger did not survive the disaster.")
                
                # Confidence Score Metric
                st.metric("Model Confidence Score", f"{confidence:.1%}")
                
                # Progress Bar for Survival Probability
                st.write(f"**Survival Probability:** {survival_prob:.1%}")
                st.progress(survival_prob)

            with res_col2:
                st.markdown("#### Primary Decision Factors")
                
                # Generate custom factors based on inputs
                factors = []
                
                # Gender Factor
                if sex == "female":
                    factors.append("🟢 **Gender Advantage:** Female passengers received priority boarding under 'Women and Children First' rules.")
                else:
                    factors.append("🔴 **Gender Disadvantage:** Male passengers faced historically low survival rates (~19%) due to evacuation protocols.")
                
                # Ticket Class Factor
                if pclass == 1:
                    factors.append("🟢 **Socio-Economic Advantage:** 1st Class passengers had deck priority and faster access to lifeboats.")
                elif pclass == 3:
                    factors.append("🔴 **Socio-Economic Disadvantage:** 3rd Class cabins were on lower decks, complicating evacuation routes.")
                
                # Age Factor
                if age <= 12:
                    factors.append(f"🟢 **Age Advantage:** Young child ({age} yrs old) received high evacuation priority.")
                elif age >= 60:
                    factors.append(f"🔴 **Age Disadvantage:** Elderly passenger ({age} yrs old) faced physical evacuation challenges.")
                
                # Family Size Factor
                if family_size == 1:
                    factors.append("🔴 **Alone Disadvantage:** Passengers traveling alone had lower documented survival rates.")
                elif 2 <= family_size <= 4:
                    factors.append("🟢 **Family size Advantage:** Small families (2-4) supported each other and survived at higher rates.")
                else:
                    factors.append("🔴 **Large Family Disadvantage:** Large groups (5+) faced coordination difficulties during boarding.")

                # Fare Factor
                if fare > 100.0:
                    factors.append(f"🟢 **Fare Advantage:** High fare paid (${fare:.2f}) indicates luxury cabin proximity.")

                # Render factors
                for f in factors:
                    st.markdown(f)
                    
        except Exception as e:
            st.error(f"Inference Error: An error occurred during prediction processing. Detail: {e}")
