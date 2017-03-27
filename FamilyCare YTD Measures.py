import pandas as pd

path = r'C:\Users\mmcvicar\Documents\Python Scripts\FamilyCare_YTD_Measures_11-11-2016_.csv'

df = pd.DataFrame.from_csv(path, header=1,index_col=None)
df['Date Of Birth'] = pd.to_datetime(df['Date Of Birth'], infer_datetime_format=True)
df['Date Performed'] = pd.to_datetime(df['Date Performed'], infer_datetime_format=True)

All_FC = df.groupby(['Wellcentive Patient ID', 'Date Of Birth', 'Physician First Name', 'Physician Last Name', 'Primary Physician Provider Group'], as_index=False).reset_index()


Adol = df[(df['Description']=='Well Child Visit') | (df['Description'] == 'Health Maintenance Exam (HME)')]
Dev = df[(df['Description']=='Developmental Screening (ASQ)') | (df['Description'] == 'Developmental Screening (Unspecified/Other)')]
ER = df[(df['Description']=='ER Visit')]


def kill_nas(df):
    return df.dropna(subset=['Date Performed'])

def format_time(field):
    return pd.to_datetime(field, infer_datetime_format=True)

def get_unique_pats(df):
    return pd.DataFrame(pd.unique(df['Wellcentive Patient ID']), columns=['Pat_ID'])

Adol = kill_nas(Adol)
Dev = kill_nas(Dev)
ER = kill_nas(ER)

#Adol['Date Performed'] = format_time(Adol['Date Performed'])
#Dev['Date Performed'] = format_time(Dev['Date Performed'])
#ER['Date Performed'] = format_time(ER['Date Performed'])

Adol_IDs = get_unique_pats(Adol)
Dev_IDs = get_unique_pats(Dev)
ER_IDs = get_unique_pats(ER)

#Adol
#
#Denominator
#Adol_in_age
Adol_Last_WC = Adol.sort_values('Date Performed', ascending=False).groupby(['Wellcentive Patient ID', 'Physician First Name', 'Physician Last Name', 'Primary Physician Provider Group'], as_index=False).first()
#Adol_Denom = pd.DataFrame({'Denom': Adol_Last_WC.groupby(['Physician First Name', 'Physician Last Name', 'Primary Physician Provider Group']).size()}).reset_index()

Adol_WC_in_2016 = Adol_Last_WC[Adol_Last_WC['Date Performed'] >= '2016-01-01']
#Adol_Num = pd.DataFrame({'Num': Adol_WC_in_2016.groupby(['Physician First Name', 'Physician Last Name', 'Primary Physician Provider Group']).size()}).reset_index()

#Adol_WC
#Dev


#ER
ER = ER[ER['Date Performed'] >= '01-01-2016']
