import pandas as pd 
import matplotlib.pyplot as plt

file = 'Transfer_Payments/pt-tp-2003-eng.csv'

df = pd.read_csv(file)
isdep = df.['MINE']== 'AGRICULTURE AND AGRI-FOOD'
df2 = df[isdep]
#df_melt = pd.melt(df,id_vars=['AGRICULTURE AND AGRI-FOOD'])
print(df2.head())