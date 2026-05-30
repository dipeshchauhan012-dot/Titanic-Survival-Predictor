import os
import sys
import traceback
import joblib
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, render_template

# Initialize Flask App
app = Flask(__name__)

# Model path
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'titanic_model.pkl')
model = None

# Load the model at startup
try:
    print(f"Loading Titanic ML model from: {MODEL_PATH}")
    model = joblib.load(MODEL_PATH)
    print("Model loaded successfully!")
except Exception as e:
    print(f"CRITICAL ERROR: Failed to load Titanic ML model: {e}", file=sys.stderr)
    traceback.print_exc()

@app.route('/')
def index():
    """Render the main index page."""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict Titanic survival based on passenger attributes.
    Expects JSON payload with parameters:
      - Pclass: int (1, 2, or 3)
      - Sex: str ('male' or 'female')
      - Age: float/int or null (positive value)
      - SibSp: int (>= 0)
      - Parch: int (>= 0)
      - Fare: float/int or null (>= 0.0)
      - Embarked: str ('C', 'Q', or 'S')
    """
    if model is None:
        return jsonify({
            'success': False,
            'error': 'ML model is not loaded on the server. Please check server logs.'
        }), 500

    try:
        # Check request content type
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Request must be JSON'
            }), 400

        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No input data provided'
            }), 400

        # Define and validate required fields
        required_fields = ['Pclass', 'Sex', 'SibSp', 'Parch', 'Embarked']
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        # Validate Pclass
        try:
            pclass = int(data['Pclass'])
            if pclass not in [1, 2, 3]:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Pclass must be 1, 2, or 3'
            }), 400

        # Validate Sex
        sex = str(data['Sex']).strip().lower()
        if sex not in ['male', 'female']:
            return jsonify({
                'success': False,
                'error': "Sex must be 'male' or 'female'"
            }), 400

        # Validate Embarked
        embarked = str(data['Embarked']).strip().upper()
        if embarked not in ['C', 'Q', 'S']:
            return jsonify({
                'success': False,
                'error': "Embarked must be 'C', 'Q', or 'S'"
            }), 400

        # Validate SibSp (Siblings/Spouses)
        try:
            sibsp = int(data['SibSp'])
            if sibsp < 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'SibSp must be a non-negative integer'
            }), 400

        # Validate Parch (Parents/Children)
        try:
            parch = int(data['Parch'])
            if parch < 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Parch must be a non-negative integer'
            }), 400

        # Validate and parse Age (can be None/null, where SimpleImputer will fill it)
        age = data.get('Age')
        if age is not None and age != '':
            try:
                age = float(age)
                if age < 0:
                    return jsonify({
                        'success': False,
                        'error': 'Age cannot be negative'
                    }), 400
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'error': 'Age must be a valid number'
                }), 400
        else:
            age = np.nan

        # Validate and parse Fare (can be None/null, where SimpleImputer will fill it)
        fare = data.get('Fare')
        if fare is not None and fare != '':
            try:
                fare = float(fare)
                if fare < 0:
                    return jsonify({
                        'success': False,
                        'error': 'Fare cannot be negative'
                    }), 400
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'error': 'Fare must be a valid number'
                }), 400
        else:
            fare = np.nan

        # Calculate Engineered Features
        # FamilySize = SibSp + Parch + 1
        family_size = sibsp + parch + 1
        # IsAlone = 1 if FamilySize == 1, else 0
        is_alone = 1 if family_size == 1 else 0

        # Create input DataFrame matching model pipeline expectation
        # Column names must be exact: Pclass, Sex, Age, SibSp, Parch, Fare, Embarked, FamilySize, IsAlone
        passenger_df = pd.DataFrame([{
            'Pclass': pclass,
            'Sex': sex,
            'Age': age,
            'SibSp': sibsp,
            'Parch': parch,
            'Fare': fare,
            'Embarked': embarked,
            'FamilySize': family_size,
            'IsAlone': is_alone
        }])

        # Perform prediction
        prediction = int(model.predict(passenger_df)[0])
        probabilities = model.predict_proba(passenger_df)[0]
        
        # probabilities array corresponds to classes [0, 1]
        non_survival_prob = float(probabilities[0])
        survival_prob = float(probabilities[1])

        # Return predictions and features details
        return jsonify({
            'success': True,
            'prediction': prediction,
            'survival_probability': round(survival_prob, 4),
            'non_survival_probability': round(non_survival_prob, 4),
            'calculated_features': {
                'FamilySize': family_size,
                'IsAlone': bool(is_alone)
            }
        })

    except Exception as e:
        print(f"Error during prediction: {e}", file=sys.stderr)
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'An internal server error occurred while computing the prediction.'
        }), 500

# Error handlers for HTML requests
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('index.html'), 500

if __name__ == '__main__':
    # Dynamically bind to PORT for Render compatibility
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
