import pandas as pd

df = pd.read_csv('data/disease_dataset.csv')
print('Load thanh cong!')
print('So mau  :', df.shape[0])
print('So cot  :', df.shape[1])
print('So benh :', df['Disease'].nunique())
print()
print(df.head(3))