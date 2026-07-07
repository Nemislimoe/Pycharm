import pandas as pd


# Невеликий набір даних про студентів

data = {

"name": ["Anna", "Ivan", "Oleh", "Maria"],

"hours_studied": [5, 10, 7, 2],

"exam_score": [50, 90, 70, 30]

}


df = pd.DataFrame(data)

print("Таблиця студентів:")

print(df)


# Supervised learning: передбачимо score на основі hours_studied

for index, row in df.iterrows():

predicted = row["hours_studied"] * 10 # дуже примітивна модель

print(f"{row['name']}: predicted score = {predicted}, actual = {row['exam_score']}")


# Unsupervised learning: просте групування за кількістю годин

df["group"] = ["high" if h >= 7 else "low" for h in df["hours_studied"]]

print("\nГрупи студентів за годинами навчання:")

print(df[["name", "hours_studied", "group"]])