import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, precision_score, recall_score

# Sample dataset
data = {
    'document': ['I love this movie', 'This was an amazing play', 
                 'I feel bored with this song', 'This show is a waste of time'],
    'class': ['positive', 'positive', 'negative', 'negative']
}
df = pd.DataFrame(data)

# Convert text to token counts
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(df['document'])
y = df['class']

# Split: use at least 1 sample per class in test → better to use small fixed split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=42, stratify=y)

# Train Naive Bayes
clf = MultinomialNB()
clf.fit(X_train, y_train)

# Predict
y_pred = clf.predict(X_test)

# Evaluate
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')

print(f"Accuracy: {accuracy:.2f}")
print(f"Precision: {precision:.2f}")
print(f"Recall: {recall:.2f}")