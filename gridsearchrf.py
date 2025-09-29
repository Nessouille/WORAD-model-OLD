import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler

# Load dataset
df = pd.read_csv("latest.csv").dropna()

# Shuffle dataset
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# Features and labels
X = df.drop(columns=["Label"])
y = df["Label"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create a pipeline: StandardScaler -> RandomForest
pipeline = make_pipeline(
    StandardScaler(),
    RandomForestClassifier(random_state=42)
)

# Define hyperparameter grid
param_grid = {
    "randomforestclassifier__n_estimators": [100, 200, 300],  # Number of trees
    "randomforestclassifier__max_depth": [None, 10, 20],  # Tree depth
    "randomforestclassifier__min_samples_split": [2, 5, 10],  # Min samples to split a node
    "randomforestclassifier__min_samples_leaf": [1, 2, 5]  # Min samples per leaf
}

# Perform Grid Search with 5-fold cross-validation
grid_search = GridSearchCV(pipeline, param_grid, cv=5, n_jobs=-1, verbose=2)
grid_search.fit(X_train, y_train)

# Print best parameters
print("Best parameters found:", grid_search.best_params_)

# Evaluate on test set
best_model = grid_search.best_estimator_
test_score = best_model.score(X_test, y_test)
print(f"Test Accuracy: {test_score:.2f}")

# Save the best model
joblib.dump(best_model, "best_worad_rf.pkl")    
print("Best Random Forest model saved successfully!")
