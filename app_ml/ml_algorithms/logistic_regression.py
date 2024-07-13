# app_ml/ml_algorithms/logistic_regression.py

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import time
import psutil

def train_logistic_regression(X_train, y_train, X_test, y_test):
    start_time = time.time()
    start_cpu = psutil.cpu_percent()

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)

    end_time = time.time()
    end_cpu = psutil.cpu_percent()

    return {
        'model': model,
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, average='weighted'),
        'recall': recall_score(y_test, y_pred, average='weighted'),
        'f1_score': f1_score(y_test, y_pred, average='weighted'),
        'auc': roc_auc_score(y_test, y_prob, multi_class='ovr', average='weighted'),
        'cpu_usage': end_cpu - start_cpu,
        'execution_time': end_time - start_time
    }