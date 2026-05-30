document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements - Inputs
    const form = document.getElementById('prediction-form');
    const ageInput = document.getElementById('Age');
    const ageVal = document.getElementById('age-val');
    const fareInput = document.getElementById('Fare');
    const fareVal = document.getElementById('fare-val');
    const sibspInput = document.getElementById('SibSp');
    const parchInput = document.getElementById('Parch');
    
    // DOM Elements - Real-time Calculated Feature Badges
    const familySizeBadge = document.getElementById('calc-family-size');
    const isAloneBadge = document.getElementById('calc-is-alone');

    // DOM Elements - Results Section
    const resultPlaceholder = document.getElementById('result-placeholder');
    const resultContent = document.getElementById('result-content');
    const predictionStatus = document.getElementById('prediction-status');
    const gaugeFill = document.getElementById('gauge-fill');
    const gaugePercentage = document.getElementById('gauge-percentage');
    const factorsContainer = document.getElementById('factors-list');

    // DOM Elements - Button & Loader
    const btnPredict = document.getElementById('btn-predict');
    const btnText = document.getElementById('btn-text');
    const btnSpinner = document.getElementById('btn-spinner');

    // Constants for SVG Gauge Animation
    const GAUGE_CIRCUMFERENCE = 439.6; // 2 * Math.PI * 70

    // 1. Synchronize range sliders with numeric badges
    if (ageInput && ageVal) {
        ageInput.addEventListener('input', (e) => {
            const val = e.target.value;
            ageVal.textContent = val ? `${val} yrs` : 'Not specified';
        });
    }

    if (fareInput && fareVal) {
        fareInput.addEventListener('input', (e) => {
            const val = parseFloat(e.target.value).toFixed(2);
            fareVal.textContent = `$${val}`;
        });
    }

    // 2. Real-time Derived Features (FamilySize, IsAlone)
    function updateFamilyFeatures() {
        const sibsp = parseInt(sibspInput.value) || 0;
        const parch = parseInt(parchInput.value) || 0;
        
        // FamilySize = SibSp + Parch + 1
        const familySize = sibsp + parch + 1;
        // IsAlone = 1 if FamilySize == 1 else 0
        const isAlone = familySize === 1;

        // Update UI
        familySizeBadge.textContent = familySize;
        isAloneBadge.textContent = isAlone ? 'Yes' : 'No';
    }

    if (sibspInput && parchInput) {
        sibspInput.addEventListener('change', updateFamilyFeatures);
        sibspInput.addEventListener('input', updateFamilyFeatures);
        parchInput.addEventListener('change', updateFamilyFeatures);
        parchInput.addEventListener('input', updateFamilyFeatures);
        
        // Initial calculation
        updateFamilyFeatures();
    }

    // 3. Form Submit handling via AJAX
    form.addEventListener('submit', (e) => {
        e.preventDefault();

        // Clear previous error messages
        document.querySelectorAll('.validation-error-msg').forEach(el => el.style.display = 'none');

        // Validation flags
        let isValid = true;

        // Retrieve input values
        const pclassRadio = document.querySelector('input[name="Pclass"]:checked');
        const sexRadio = document.querySelector('input[name="Sex"]:checked');
        const embarkedRadio = document.querySelector('input[name="Embarked"]:checked');
        const age = ageInput.value.trim();
        const fare = fareInput.value.trim();
        const sibsp = sibspInput.value.trim();
        const parch = parchInput.value.trim();

        // Validation Pclass
        if (!pclassRadio) {
            showError('Pclass', 'Please select a passenger ticket class');
            isValid = false;
        }

        // Validation Sex
        if (!sexRadio) {
            showError('Sex', 'Please select a passenger gender');
            isValid = false;
        }

        // Validation Embarked
        if (!embarkedRadio) {
            showError('Embarked', 'Please select port of embarkation');
            isValid = false;
        }

        // Validation Age
        if (age !== '') {
            const ageNum = parseFloat(age);
            if (isNaN(ageNum) || ageNum < 0 || ageNum > 120) {
                showError('Age', 'Please enter a valid age between 0 and 120');
                isValid = false;
            }
        }

        // Validation Fare
        if (fare !== '') {
            const fareNum = parseFloat(fare);
            if (isNaN(fareNum) || fareNum < 0) {
                showError('Fare', 'Please enter a non-negative fare');
                isValid = false;
            }
        }

        // Validation SibSp
        const sibspNum = parseInt(sibsp);
        if (isNaN(sibspNum) || sibspNum < 0) {
            showError('SibSp', 'Must be 0 or greater');
            isValid = false;
        }

        // Validation Parch
        const parchNum = parseInt(parch);
        if (isNaN(parchNum) || parchNum < 0) {
            showError('Parch', 'Must be 0 or greater');
            isValid = false;
        }

        if (!isValid) return;

        // Show spinner, disable button
        btnSpinner.style.display = 'inline-block';
        btnText.textContent = 'Calculating...';
        btnPredict.disabled = true;

        // Prepare JSON payload
        const payload = {
            Pclass: parseInt(pclassRadio.value),
            Sex: sexRadio.value,
            Age: age !== '' ? parseFloat(age) : null,
            SibSp: parseInt(sibsp),
            Parch: parseInt(parch),
            Fare: fare !== '' ? parseFloat(fare) : null,
            Embarked: embarkedRadio.value
        };

        // Send POST request
        fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errData => {
                    throw new Error(errData.error || 'Server error occurred');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                renderResult(data, payload);
            } else {
                alert(`Error: ${data.error}`);
            }
        })
        .catch(err => {
            console.error('Prediction Error:', err);
            alert(`Calculation failed: ${err.message}`);
        })
        .finally(() => {
            // Restore button state
            btnSpinner.style.display = 'none';
            btnText.textContent = 'Predict Survival';
            btnPredict.disabled = false;
        });
    });

    // Display inline input errors
    function showError(fieldId, message) {
        const errorEl = document.getElementById(`${fieldId}-error`);
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.style.display = 'block';
        }
    }

    // Render results on screen with smooth animations
    function renderResult(data, payload) {
        // 1. Toggle visibility from placeholder to content
        resultPlaceholder.style.display = 'none';
        resultContent.style.display = 'block';

        // 2. Set Prediction Status Banner
        const survived = data.prediction === 1;
        predictionStatus.textContent = survived ? 'PASSENGER SURVIVED' : 'PASSENGER DECEASED';
        predictionStatus.className = 'prediction-status-card ' + (survived ? 'status-survived' : 'status-deceased');

        // 3. Animate Radial Gauge Percentage
        const prob = data.survival_probability;
        const targetPercent = Math.round(prob * 100);
        
        // Reset gauge offset first
        gaugeFill.style.strokeDashoffset = GAUGE_CIRCUMFERENCE;
        
        // Switch gradient colors based on prediction
        if (survived) {
            gaugeFill.setAttribute('stroke', 'url(#gauge-gradient-survived)');
        } else {
            gaugeFill.setAttribute('stroke', 'url(#gauge-gradient-deceased)');
        }

        // Animate count and gauge fill offset
        setTimeout(() => {
            // Animate stroke offset
            const offset = GAUGE_CIRCUMFERENCE - (prob * GAUGE_CIRCUMFERENCE);
            gaugeFill.style.strokeDashoffset = offset;

            // Animate number count-up
            let currentVal = 0;
            const duration = 1200; // ms
            const intervalTime = 15; // ms
            const step = targetPercent / (duration / intervalTime);
            
            const timer = setInterval(() => {
                currentVal += step;
                if (currentVal >= targetPercent) {
                    gaugePercentage.textContent = `${targetPercent}%`;
                    clearInterval(timer);
                } else {
                    gaugePercentage.textContent = `${Math.round(currentVal)}%`;
                }
            }, intervalTime);
        }, 100);

        // 4. Generate Dynamic Factor Insights
        generateFactorsList(payload, survived);
    }

    // Generate smart feature impact details based on passenger inputs
    function generateFactorsList(payload, survived) {
        factorsContainer.innerHTML = '';

        const factors = [];

        // Gender Impact
        if (payload.Sex === 'female') {
            factors.push({
                icon: 'fa-venus',
                text: 'Female gender is the strongest positive predictor (Women & Children First protocol).',
                impact: 'positive',
                weight: 'High'
            });
        } else {
            factors.push({
                icon: 'fa-mars',
                text: 'Male passengers suffered historically low survival rates due to lifeboat priorities.',
                impact: 'negative',
                weight: 'High'
            });
        }

        // Ticket Class Impact
        if (payload.Pclass === 1) {
            factors.push({
                icon: 'fa-gem',
                text: '1st Class passenger tickets granted priority boarding and closer access to lifeboats.',
                impact: 'positive',
                weight: 'High'
            });
        } else if (payload.Pclass === 3) {
            factors.push({
                icon: 'fa-users',
                text: '3rd Class quarters were deep in the ship; lower decks suffered slower evacuations.',
                impact: 'negative',
                weight: 'High'
            });
        } else {
            factors.push({
                icon: 'fa-user-tie',
                text: '2nd Class passengers had intermediate survival rates and moderate deck access.',
                impact: 'neutral',
                weight: 'Medium'
            });
        }

        // Age Impact
        if (payload.Age !== null) {
            if (payload.Age <= 12) {
                factors.push({
                    icon: 'fa-child',
                    text: `Child passenger (${payload.Age} yrs old) received high evacuation priority.`,
                    impact: 'positive',
                    weight: 'Medium'
                });
            } else if (payload.Age >= 60) {
                factors.push({
                    icon: 'fa-blind',
                    text: `Elderly passenger (${payload.Age} yrs old) faced severe physical challenges.`,
                    impact: 'negative',
                    weight: 'Medium'
                });
            } else {
                factors.push({
                    icon: 'fa-user',
                    text: `Adult passenger aged ${payload.Age} years.`,
                    impact: 'neutral',
                    weight: 'Low'
                });
            }
        } else {
            factors.push({
                icon: 'fa-question-circle',
                text: 'Age not specified. Imputed using demographic media values.',
                impact: 'neutral',
                weight: 'Low'
            });
        }

        // Family Size / Alone status
        const familySize = payload.SibSp + payload.Parch + 1;
        if (familySize === 1) {
            factors.push({
                icon: 'fa-male',
                text: 'Traveling alone (no family). Historically associated with lower rescue probability.',
                impact: 'negative',
                weight: 'Medium'
            });
        } else if (familySize >= 2 && familySize <= 4) {
            factors.push({
                icon: 'fa-people-roof',
                text: `Moderate family size (${familySize} people) supported mutual aid during boarding.`,
                impact: 'positive',
                weight: 'Medium'
            });
        } else {
            factors.push({
                icon: 'fa-users-rectangle',
                text: `Large family size of ${familySize} made it difficult to coordinate and find spaces in lifeboats.`,
                impact: 'negative',
                weight: 'High'
            });
        }

        // Fare Impact
        if (payload.Fare !== null) {
            if (payload.Fare > 100) {
                factors.push({
                    icon: 'fa-dollar-sign',
                    text: 'Extremely high fare paid. Highly correlated with survival and executive cabins.',
                    impact: 'positive',
                    weight: 'Medium'
                });
            } else if (payload.Fare < 10) {
                factors.push({
                    icon: 'fa-dollar-sign',
                    text: 'Very low ticket fare paid, common for lowest standard third-class cabins.',
                    impact: 'negative',
                    weight: 'Low'
                });
            }
        }

        // Embarked Impact
        if (payload.Embarked === 'C') {
            factors.push({
                icon: 'fa-anchor',
                text: 'Embarked at Cherbourg. Passengers from France were wealthier on average.',
                impact: 'positive',
                weight: 'Low'
            });
        }

        // Populate HTML
        factors.push(...factors.slice(0, 4)); // Limit to max 4 most important
        
        // Remove duplicates and render
        const rendered = [];
        factors.forEach(f => {
            if (rendered.length < 4 && !rendered.some(r => r.text === f.text)) {
                rendered.push(f);
                
                const item = document.createElement('div');
                item.className = 'factor-item';
                
                item.innerHTML = `
                    <div class="factor-icon ${f.impact}">
                        <i class="fas ${f.icon}"></i>
                    </div>
                    <div class="factor-text">${f.text}</div>
                    <div class="factor-weight ${f.weight.toLowerCase()}">${f.weight}</div>
                `;
                factorsContainer.appendChild(item);
            }
        });
    }
});
