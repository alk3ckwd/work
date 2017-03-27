import pandas as pd

df = pd.DataFrame({'A':['A0', 'A1', 'A1'],
		   'B':['B0', 'B1', 'B2']})


print(df.groupby(['A'])['B'].apply(", ".join))

