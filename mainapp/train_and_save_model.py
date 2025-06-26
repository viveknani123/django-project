import pickle
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Load sample data (replace with your own if you have it)
data = load_iris()
X = data.data
y = data.target

# Split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Evaluate accuracy (optional)
accuracy = model.score(X_test, y_test)
print(f"Test accuracy: {accuracy:.2f}")

# Save the model
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("model.pkl has been created.")