"""
Передбачення виживання пасажирів на Титаніку
Навчання 5 моделей класифікації: Logistic Regression, Decision Tree,
Random Forest, KNN, SVM
"""

import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Створюємо папку для графіків, якщо її ще немає
os.makedirs("charts", exist_ok=True)

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, confusion_matrix, classification_report
)

pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 20)

SEP = "=" * 70


def log(title):
    print("\n" + SEP)
    print(title)
    print(SEP)


# =====================================================================
# 1. Завантаження даних
# =====================================================================
log("1. ЗАВАНТАЖЕННЯ ДАНИХ (Titanic dataset)")

raw = sns.load_dataset("titanic")

# Залишаємо колонки, вказані у завданні
df = raw[["pclass", "sex", "age", "sibsp", "parch",
          "fare", "embarked", "survived"]].copy()
df.columns = ["Pclass", "Sex", "Age", "SibSp", "Parch",
              "Fare", "Embarked", "Survived"]

print(f"Розмір датасету: {df.shape[0]} рядків, {df.shape[1]} колонок")
print("\nПерші 5 рядків:")
print(df.head())

print("\nІнформація про типи даних:")
print(df.dtypes)

# =====================================================================
# 2. Попередня обробка даних (EDA)
# =====================================================================
log("2. ПОПЕРЕДНЯ ОБРОБКА ДАНИХ (EDA)")

print("Пропущені значення до обробки:")
print(df.isnull().sum())

# Заповнення пропусків
age_median = df["Age"].median()
embarked_mode = df["Embarked"].mode()[0]
fare_median = df["Fare"].median()

df["Age"] = df["Age"].fillna(age_median)
df["Embarked"] = df["Embarked"].fillna(embarked_mode)
df["Fare"] = df["Fare"].fillna(fare_median)

print(f"\nМедіана віку, використана для заповнення: {age_median:.1f}")
print(f"Мода порту посадки, використана для заповнення: {embarked_mode}")

print("\nПропущені значення після обробки:")
print(df.isnull().sum())

# Базова статистика
print("\nОписова статистика числових ознак:")
print(df.describe())

# Розподіл цільової змінної
print("\nРозподіл цільової змінної (Survived):")
print(df["Survived"].value_counts())
print(df["Survived"].value_counts(normalize=True).round(3))

# --- Візуалізація 1: розподіл виживання ---
plt.figure(figsize=(6, 4.5))
ax = sns.countplot(data=df, x="Survived", hue="Survived",
                    palette=["#c0392b", "#27ae60"], legend=False)
ax.set_xticks([0, 1])
ax.set_xticklabels(["Не вижив (0)", "Вижив (1)"])
ax.set_title("Розподіл пасажирів за виживанням")
ax.set_xlabel("")
ax.set_ylabel("Кількість пасажирів")
for p in ax.patches:
    ax.annotate(f"{int(p.get_height())}",
                (p.get_x() + p.get_width() / 2, p.get_height()),
                ha="center", va="bottom", fontsize=10)
plt.tight_layout()
plt.savefig("charts/01_survived_distribution.png", dpi=150)
plt.close()

# --- Візуалізація 2: виживання за статтю та класом ---
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
sns.barplot(data=df, x="Sex", y="Survived", hue="Sex", ax=axes[0],
            palette=["#2980b9", "#e67e22"], legend=False)
axes[0].set_title("Частка виживання за статтю")
axes[0].set_ylabel("Частка виживших")

sns.barplot(data=df, x="Pclass", y="Survived", hue="Pclass", ax=axes[1],
            palette="Blues_d", legend=False)
axes[1].set_title("Частка виживання за класом квитка")
axes[1].set_ylabel("Частка виживших")
plt.tight_layout()
plt.savefig("charts/02_survival_by_sex_class.png", dpi=150)
plt.close()

# --- Кореляційна матриця (тільки числові до one-hot) ---
plt.figure(figsize=(6, 5))
num_df = df[["Pclass", "Age", "SibSp", "Parch", "Fare", "Survived"]]
corr = num_df.corr(numeric_only=True)
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0,
            square=True, cbar_kws={"shrink": 0.8})
plt.title("Кореляція між числовими ознаками")
plt.tight_layout()
plt.savefig("charts/03_correlation_heatmap.png", dpi=150)
plt.close()

print("\nКореляція ознак зі Survived:")
print(corr["Survived"].sort_values(ascending=False))

# One-hot encoding категоріальних ознак
df_encoded = pd.get_dummies(df, columns=["Sex", "Embarked"], drop_first=True)
print("\nКолонки після one-hot encoding:")
print(df_encoded.columns.tolist())
print(df_encoded.head())

# =====================================================================
# 3. Поділ на train/test та масштабування
# =====================================================================
log("3. ПОДІЛ НА TRAIN/TEST ТА МАСШТАБУВАННЯ")

X = df_encoded.drop(columns=["Survived"])
y = df_encoded["Survived"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Train: {X_train.shape[0]} прикладів")
print(f"Test:  {X_test.shape[0]} прикладів")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# =====================================================================
# 4-6. Навчання, передбачення та оцінка 5 моделей
# =====================================================================
log("4-6. НАВЧАННЯ ТА ОЦІНКА МОДЕЛЕЙ")

models = {
    "Logistic Regression": (LogisticRegression(max_iter=500, random_state=42), True),
    "Decision Tree": (DecisionTreeClassifier(max_depth=5, random_state=42), False),
    "Random Forest": (RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42), False),
    "K-Nearest Neighbors": (KNeighborsClassifier(n_neighbors=9), True),
    "Support Vector Machine": (SVC(kernel="rbf", C=1.0, random_state=42), True),
}

results = {}
reports = {}
matrices = {}

for name, (model, needs_scaling) in models.items():
    Xtr = X_train_scaled if needs_scaling else X_train
    Xte = X_test_scaled if needs_scaling else X_test

    model.fit(Xtr, y_train)
    y_pred = model.predict(Xte)

    acc = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=["Не вижив", "Вижив"])

    results[name] = acc
    matrices[name] = cm
    reports[name] = report

    log(f"Модель: {name}")
    print(f"Accuracy: {acc:.4f}")
    print("\nConfusion Matrix:")
    print(cm)
    print("\nClassification Report:")
    print(report)

# --- Візуалізація confusion matrices всіх моделей ---
fig, axes = plt.subplots(2, 3, figsize=(14, 8))
axes = axes.flatten()
for i, (name, cm) in enumerate(matrices.items()):
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False, ax=axes[i],
                xticklabels=["Не вижив", "Вижив"],
                yticklabels=["Не вижив", "Вижив"])
    axes[i].set_title(name, fontsize=11)
    axes[i].set_ylabel("Факт")
    axes[i].set_xlabel("Прогноз")
axes[-1].axis("off")
plt.tight_layout()
plt.savefig("charts/04_confusion_matrices.png", dpi=150)
plt.close()

# =====================================================================
# 7. Порівняння моделей
# =====================================================================
log("7. ПОРІВНЯННЯ МОДЕЛЕЙ")

results_df = pd.DataFrame({
    "Модель": list(results.keys()),
    "Accuracy": list(results.values())
}).sort_values("Accuracy", ascending=False).reset_index(drop=True)

print(results_df.to_string(index=False))

best_model = results_df.iloc[0]["Модель"]
best_acc = results_df.iloc[0]["Accuracy"]
print(f"\nНайточніша модель: {best_model} (accuracy = {best_acc:.4f})")

# --- Візуалізація порівняння точності ---
plt.figure(figsize=(8, 5))
colors = ["#27ae60" if m == best_model else "#2980b9" for m in results_df["Модель"]]
bars = plt.barh(results_df["Модель"], results_df["Accuracy"], color=colors)
plt.xlabel("Accuracy")
plt.title("Порівняння точності моделей класифікації")
plt.xlim(0, 1)
for bar, acc in zip(bars, results_df["Accuracy"]):
    plt.text(acc + 0.01, bar.get_y() + bar.get_height() / 2,
              f"{acc:.3f}", va="center", fontsize=10)
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig("charts/05_model_comparison.png", dpi=150)
plt.close()

print("\nГрафіки збережено в папці charts/")
print("\nГотово!")