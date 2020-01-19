import pandas as pd
import os

final_df = pd.DataFrame() #creates a new dataframe that's empty
for x in range (13,20):
    relative_path = 'excel_sheets'
    current_dir = os.getcwd()
    joined = os.path.join("/", current_dir, relative_path)
    df = pd.read_csv(f"{joined}\\transfer_payment_{x}.csv")
    for i, row in df.iterrows():
        df.at[i, 'FSCL_YR'] = df['FSCL_YR'][i][-4:]
    final_df = final_df.append(df)
final_df.to_csv('transfer_payment.csv')