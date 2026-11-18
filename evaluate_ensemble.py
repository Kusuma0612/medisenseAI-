
import os
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

from model_service import predict_ensemble


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Change this path if your test dataset is stored elsewhere.
TEST_CSV = os.path.join(BASE_DIR, "dataset", "test.csv")

df = pd.read_csv(TEST_CSV)

# Support either of these input column names.
text_column = (
    "Patient_Text" if "Patient_Text" in df.columns
    else "Symptoms"
)

actual_column = "Disease"

df = df.dropna(subset=[text_column, actual_column])

actual_labels = []
predicted_labels = []

print("Evaluating proposed soft-voting ensemble...")

for index, row in df.iterrows():

    patient_text = str(row[text_column]).strip()
    actual_disease = str(row[actual_column]).strip()

    result = predict_ensemble(patient_text)

    predicted_disease = str(
        result["predicted_disease"]
    ).strip()

    actual_labels.append(actual_disease)
    predicted_labels.append(predicted_disease)

    if (len(predicted_labels) % 100) == 0:
        print(f"Processed {len(predicted_labels)} samples")

print("\n========== ENSEMBLE EVALUATION ==========")

accuracy = accuracy_score(
    actual_labels, predicted_labels
)

precision = precision_score(
    actual_labels,
    predicted_labels,
    average="macro",
    zero_division=0
)

recall = recall_score(
    actual_labels,
    predicted_labels,
    average="macro",
    zero_division=0
)

f1 = f1_score(
    actual_labels,
    predicted_labels,
    average="macro",
    zero_division=0
)

print(f"Accuracy  : {accuracy:.6f} ({accuracy * 100:.2f}%)")
print(f"Precision : {precision:.6f} ({precision * 100:.2f}%)")
print(f"Recall    : {recall:.6f} ({recall * 100:.2f}%)")
print(f"Macro F1  : {f1:.6f} ({f1 * 100:.2f}%)")

print("\nTotal evaluated samples:", len(actual_labels))
print("Ensemble method: Soft Voting")
