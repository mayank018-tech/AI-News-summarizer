import pandas as pd

df = pd.read_csv("data/MIT_AI_ARTICLES.csv")

print("Shape:", df.shape)
print("\nColumns:")
print(df.columns)

print("\nFirst 5 rows:")

print(df.head())

print("\nMissing values:")
print(df.isnull().sum())

print("\nCategories:")
print(df["category"].value_counts())