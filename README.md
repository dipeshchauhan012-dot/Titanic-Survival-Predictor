# Titanic Survival Predictor

A modern, production-ready machine learning web application that predicts Titanic passenger survival using historical passenger data. This repository includes data analysis notebooks, a serialized Random Forest classifier pipeline, and an interactive Flask-based web application with a responsive Bootstrap 5 interface.

---

## Project Overview

The sinking of the Titanic is one of the most infamous shipwreck disasters in history. On April 15, 1912, during her maiden voyage, the widely considered "unsinkable" Titanic sank after colliding with an iceberg. Unfortunately, there were not enough lifeboats for everyone onboard, resulting in the death of 1502 out of 2224 passengers and crew.

While there was some element of luck involved in surviving, it seems some groups of people were more likely to survive than others, such as women, children, and the upper-class. 

This project aims to build a predictive model that answers the question: "What sorts of people were more likely to survive?" using passenger demographics and ticket profiles.

---

## Dataset Information

The model is trained on the classic Kaggle Titanic passenger dataset containing 891 passenger profiles.

- **Target Variable:** `Survived` (0 = Deceased, 1 = Survived)
- **Training Records:** 891 records
- **Data Columns (12 raw features):**
  - `PassengerId`: Unique identifier for each passenger
  - `Survived`: Survival status (0 or 1)
  - `Pclass`: Passenger ticket class (1 = 1st, 2 = 2nd, 3 = 3rd)
  - `Name`: Full passenger name
  - `Sex`: Gender (male, female)
  - `Age`: Passenger age in years
  - `SibSp`: Number of siblings or spouses traveling with the passenger
  - `Parch`: Number of parents or children traveling with the passenger
  - `Ticket`: Ticket number
  - `Fare`: Passenger ticket price
  - `Cabin`: Cabin number/deck allocation
  - `Embarked`: Port of embarkation (C = Cherbourg, Q = Queenstown, S = Southampton)

---

## Features Used & Feature Engineering

During model development, features that did not contribute to passenger survival (such as `PassengerId`, `Name`, `Ticket`, and `Cabin`) were dropped. 

### Core Features:
1. **Pclass (Ticket Class):** Categorical integer (1, 2, or 3) representing socio-economic status.
2. **Sex:** Categorical gender (male, female).
3. **Age:** Numeric age (imputed with median values during pre-processing).
4. **SibSp:** Integer indicating siblings/spouses aboard.
5. **Parch:** Integer indicating parents/children aboard.
6. **Fare:** Numeric price paid for the ticket.
7. **Embarked:** Port of embarkation (C, Q, or S).

### Engineered Features:
To boost predictive power, two calculated features were engineered:
- **FamilySize:** `SibSp + Parch + 1` representing total group size traveling together.
- **IsAlone:** Binary flag (`1` if `FamilySize == 1`, else `0`) indicating whether the passenger traveled alone.

---

## Exploratory Data Analysis (EDA) Summary

From the exploratory analysis conducted in `Titanic_Survival_Predictor.ipynb`, key historical survival factors were identified:

1. **Gender Bias:** The "Women and Children First" protocol was strongly reflected in the data. Female survival rate was ~74%, while the male survival rate was only ~19%.
2. **Class Advantage:** Socio-economic status had a high correlation with survival. Upper-deck 1st Class passengers had a **62%** survival rate, compared to a meager **24%** for 3rd Class passengers whose quarters were lower in the ship.
3. **Age Distribution:** The passenger distribution was right-skewed with a median age of 28. Young children (under 12) showed a higher rate of survival, whereas elderly passengers had lower survival outcomes.
4. **Group Cohesion:** Passengers traveling in small families (2 to 4 people) had higher survival rates than those traveling completely alone or in extremely large family groups (5+ people).

---

## Models Tested & Accuracy Results

The project explored multiple classification models to optimize accuracy:

### 1. Logistic Regression (Tested in Jupyter Notebook)
- **Architecture:** Pipeline with `StandardScaler`, Dummy Encoders (`Sex_male`, `Embarked_Q`, `Embarked_S`), and `LogisticRegression(max_iter=1000)`.
- **Validation Split:** 80% Train, 20% Test.
- **Accuracy:** **81.01%**
- **Confusion Matrix:**
  - True Negatives (Deceased): 90
  - False Positives: 15
  - False Negatives: 19
  - True Positives (Survived): 55

### 2. Random Forest Classifier (Production Model: `titanic_model.pkl`)
- **Architecture:** Scikit-Learn Pipeline combining a `ColumnTransformer` (standard scaler + median imputer for numerical data, one-hot encoder for categorical variables) with a `RandomForestClassifier` (200 estimators, random state 42).
- **Features Evaluated:** Includes all raw features plus engineered variables (`FamilySize`, `IsAlone`).
- **Use Case:** Saved as `titanic_model.pkl` using `joblib` and used for real-time inference on the web application backend.

---

## How to Run the Project

### Method A: Run the Flask Web Application (Local Server)

1. **Navigate to the directory:**
   ```bash
   cd Titanic-Survival-Predictor
   ```
2. **Set up a Virtual Environment:**
   * *Windows (PowerShell):*
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   * *macOS/Linux:*
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```
3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Start the server:**
   ```bash
   python app.py
   ```
5. **View the site:**
   Open your browser and navigate to `http://127.0.0.1:5000`.

### Method B: Run the Jupyter Analysis Notebook

1. Ensure you have Jupyter installed:
   ```bash
   pip install jupyter
   ```
2. Run the notebook kernel:
   ```bash
   jupyter notebook Titanic_Survival_Predictor.ipynb
   ```

---

## Future Improvements

- **Hyperparameter Optimization:** Implement grid search (`GridSearchCV`) or randomized search to tune the Random Forest and test gradient boosting models (XGBoost, LightGBM).
- **Name Casing & Title Extraction:** Parse title indicators (e.g. Mr., Mrs., Miss., Master., Dr.) from passenger names to better infer social status and age ranges.
- **Deck Mapping:** Parse the first letter of cabin allocations to map passengers to specific decks on the ship, as deck proximity to lifeboats had high correlation with survival.
- **Continuous Integration (CI):** Establish automated GitHub Actions to test Flask routes and predictions.
