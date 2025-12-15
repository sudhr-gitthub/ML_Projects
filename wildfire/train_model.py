import pandas as pd
import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression

# 1. Create dummy data matching the Algerian Forest Fire Dataset structure
# Columns: [Temp, RH, Ws, Rain, FFMC, DMC, DC, ISI, BUI, FWI]
X_train = np.array([
    [29, 57, 18, 0, 65.7, 3.4, 7.6, 1.3, 3.4, 0.5],  # No Fire
    [29, 61, 13, 1.3, 64.4, 4.1, 7.6, 1, 3.9, 0.4],  # No Fire
    [32, 40, 14, 0, 90.0, 50.0, 100.0, 15.0, 40.0, 20.0], # Fire
    [35, 30, 15, 0, 92.0, 60.0, 150.0, 18.0, 50.0, 25.0], # Fire
    [30, 50, 15, 0, 80.0, 20.0, 50.0, 5.0, 20.0, 10.0],   # Borderline
])

# 0 = No Fire, 1 = Fire
y_train = np.array([0, 0, 1, 1, 1])

# 2. Train a simple Logistic Regression model
model = LogisticRegression()
model.fit(X_train, y_train)

# 3. Save the model as 'wildfire.pkl'
joblib.dump(model, 'wildfire.pkl')

print("✅ Success! A new compatible 'wildfire.pkl' has been created.")
print(f"Model expects {model.n_features_in_} features (Temp, RH, Ws, Rain, FFMC, DMC, DC, ISI, BUI, FWI).")
