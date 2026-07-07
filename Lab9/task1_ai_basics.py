# Простий приклад "AI"

# Створюємо дані про тварин

animals = ["cat", "dog", "bird", "fish"]


# "AI" визначає, яка тварина може літати

for animal in animals:

if animal in ["bird"]:

print(f"{animal.title()} can fly")

else:

print(f"{animal.title()} cannot fly")


# Проста ML-модель (на прикладі правил)

# Якщо age < 18 → дитина, інакше дорослий

ages = [5, 12, 20, 35]


for age in ages:

category = "child" if age < 18 else "adult"

print(f"Age {age} → {category}")