# app_ml/ml_algorithms/__init__.py

import os
import time
import psutil
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from PIL import Image
from django.conf import settings

def load_dataset(dataset_path):
    X, y = [], []
    class_names = sorted(os.listdir(dataset_path))
    for class_name in class_names:
        class_path = os.path.join(dataset_path, class_name)
        print(class_path)
        if os.path.isdir(class_path):
            print(class_path)
            for image_name in os.listdir(class_path):
                print(image_name)
                image_path = os.path.join(class_path, image_name)
                image = Image.open(image_path).convert('RGB')
                image = image.resize((64, 64))  # Resize for consistency
                X.append(np.array(image).flatten())
                y.append(class_name)
    
    return np.array(X), np.array(y)

def train_and_evaluate(dataset_path):
    X, y = load_dataset(dataset_path)
    le = LabelEncoder()
    y = le.fit_transform(y)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    algorithms = {
        'Logistic Regression': LogisticRegression(max_iter=1000),
        'Neural Network': MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=1000),
        'SVM': SVC(probability=True),
        'Naive Bayes': GaussianNB(),
        'Random Forest': RandomForestClassifier(),
        'Decision Tree': DecisionTreeClassifier()
    }

    results = {}

    for name, model in algorithms.items():
        start_time = time.time()
        start_cpu = psutil.cpu_percent()

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)

        end_time = time.time()
        end_cpu = psutil.cpu_percent()

        results[name] = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted'),
            'recall': recall_score(y_test, y_pred, average='weighted'),
            'f1_score': f1_score(y_test, y_pred, average='weighted'),
            'auc': roc_auc_score(y_test, y_prob, multi_class='ovr', average='weighted'),
            'cpu_usage': end_cpu - start_cpu,
            'execution_time': end_time - start_time
        }

    return results

