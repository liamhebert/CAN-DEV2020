import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np

file = 'Transfer_Payments/pt-tp-2003-eng.csv'

df = pd.read_csv(file)
isdep = df['MINE']== 'AGRICULTURE AND AGRI-FOOD'
Agr = df[isdep]
#df_melt = pd.melt(df,id_vars=['AGRICULTURE AND AGRI-FOOD'])
tot = np.array(Agr['AGRG_PYMT_AMT']).sum()

plt.pie(np.array(Agr['AGRG_PYMT_AMT']),labels =Agr['RCPNT_NML_EN_DESC'])

#plt.show()
plt.show()