import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier

print("⏳ Generating dummy model...")

# 1. Simulate Training Data (Image size 100x100 RGB = 30,000 features)
# We create 10 fake images
img_size = 100 * 100 * 3
X_train = np.random.rand(10, img_size)

# 0 = No Damage, 1 = Damage
y_train = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1])

# 2. Train a simple classifier
model = RandomForestClassifier()
model.fit(X_train, y_train)

# 3. Save as 'model.pkl'
filename = 'model.pkl'
with open(filename, 'wb') as file:
    pickle.dump(model, file)

print(f"✅ Success! '{filename}' has been created.")
print("👉 Now upload this file to your GitHub 'Hurricane_Damage' folder.")
