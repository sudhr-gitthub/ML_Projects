from flask import Flask, request, render_template, jsonify
import pickle
import numpy as np

app = Flask(__name__)

# Load the model components
# Note: Since the pkl contains both PolynomialFeatures and LinearRegression, 
# we must apply them in the correct order.
with open('Fish_model.pkl', 'rb') as f:
    model_data = pickle.load(f)

# In your specific pkl, the components are stored sequentially
poly = model_data[0] # PolynomialFeatures
model = model_data[1] # LinearRegression

@app.route('/')
def home():
    return "Fish Weight Prediction API is Running. Use the /predict endpoint."

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get data from POST request
        data = request.get_json()
        
        # Features required: Length1, Length2, Length3, Height, Width
        features = [
            data['Length1'], 
            data['Length2'], 
            data['Length3'], 
            data['Height'], 
            data['Width']
        ]
        
        # Convert to numpy array and reshape for prediction
        final_features = np.array([features])
        
        # 1. Transform features to polynomial
        poly_features = poly.transform(final_features)
        
        # 2. Predict using linear model
        prediction = model.predict(poly_features)
        
        return jsonify({'predicted_weight': float(prediction[0])})
    
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    app.run(debug=True)
