import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.datasets import load_iris

# Load Iris dataset (instead of CSV)
iris = load_iris()
df = pd.DataFrame(data=iris.data, columns=iris.feature_names)
df['species'] = iris.target
df['species'] = df['species'].replace({0: 'setosa', 1: 'versicolor', 2: 'virginica'})

# Use only petal length and petal width
X = df[["petal length (cm)", "petal width (cm)"]].values
y = df["species"].replace({"setosa": 0, "versicolor": 1, "virginica": 2}).values

# Split the dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Standardize features
sc = StandardScaler()
X_train_std = sc.fit_transform(X_train)
X_test_std = sc.transform(X_test)

# Train SVM with linear kernel
svm = SVC(kernel='linear', C=1.0, random_state=42)
svm.fit(X_train_std, y_train)

# Predictions
y_pred = svm.predict(X_test_std)

# Accuracy
accuracy = np.mean(y_pred == y_test)
print(f"Accuracy: {accuracy * 100:.2f}%")