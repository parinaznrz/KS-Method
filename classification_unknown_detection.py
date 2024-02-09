
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns
from appscanner.appscanner import AppScanner
from appscanner.preprocessor import Preprocessor


########################################################################
#                              Read data                               #
########################################################################
preprocessor = Preprocessor(verbose=True)
X_train, y_train = preprocessor.load(r'.p')
X_test_original, y_test_original = preprocessor.load(r'.p') #if you have known dataset for test
X_test_new, y_test_new = preprocessor.load(r'.p')
X_validation_external, y_validation_external = preprocessor.load(r'.p')

# Modify Labels in External Validation and New Test Data
y_validation_external[:] = 'unknown'
y_test_new[:] = 'unknown'

# Split Training Data (70/30)
X_train_split, X_validation_split, y_train_split, y_validation_split = train_test_split(
    X_train, y_train, test_size=0.3, random_state=42)

# Combine Split Validation Data with External Set
X_validation_combined = np.concatenate((X_validation_split, X_validation_external))
y_validation_combined = np.concatenate((y_validation_split, y_validation_external))

# Combine Test Dataset
X_test_combined = np.concatenate((X_test_original, X_test_new))
y_test_combined = np.concatenate((y_test_original, y_test_new))

# Scale Features
scaler = MinMaxScaler()
X_train_split = scaler.fit_transform(X_train_split)
X_validation_combined = scaler.transform(X_validation_combined)
X_test_combined = scaler.transform(X_test_combined)

########################################################################
#                  Find the Best Threshold on Validation Set           #
########################################################################
best_threshold = 0
best_f1_score = 0

for threshold in np.arange(0, 1, 0.1):
    scanner = AppScanner(threshold=threshold)
    scanner.fit(X_train_split, y_train_split)
    y_pred_val = scanner.predict(X_validation_combined)

    # Calculate macro-average F1-score
    f1 = f1_score(y_validation_combined, y_pred_val, average='macro', labels=np.unique(np.concatenate((y_train, ['unknown']))))
    print(f"Threshold: {threshold:.1f}, F1-Score: {f1:.4f}")

    if f1 > best_f1_score:
        best_f1_score = f1
        best_threshold = threshold

print(f"Best Threshold: {best_threshold}, Best F1-Score: {best_f1_score}")


########################################################################
#                          Test Set Evaluation                         #
########################################################################
scanner = AppScanner(threshold=best_threshold)
scanner.fit(X_train_split, y_train_split)

y_pred_combined = scanner.predict(X_test_combined)

# Unique labels including 'unknown'
l1 = np.unique(np.concatenate((y_train, ['unknown'])))

# Classification Report and Confusion Matrix for Combined Test Set
print("Classification Report on Combined Test Set:")
print(classification_report(y_true=y_test_combined, y_pred=y_pred_combined, labels=l1, digits=4))

# Plot the confusion matrix for Combined Test Set
confusion_combined = confusion_matrix(y_true=y_test_combined, y_pred=y_pred_combined, labels=l1)
plt.figure(figsize=(12, 10))
sns.heatmap(confusion_combined, annot=True, fmt='d', cmap='Blues', xticklabels=l1, yticklabels=l1)
plt.title('Confusion Matrix for Combined Test Set')
plt.xlabel('Predicted Labels')
plt.ylabel('True Labels')
plt.show()
