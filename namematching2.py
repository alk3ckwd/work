import pandas as pd
import string
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()
clinic_list = filedialog.askopenfilename(title='List from Clinic')
WC_Prac = filedialog.askopenfilename(title='Clinic List from WC')
WC_All = filedialog.askopenfilename(title='All Patients from WC')

clinic_pats_orig = pd.read_csv(clinic_list,quotechar='"',skipinitialspace=True, keep_default_na=False)
clinic_pats = clinic_pats_orig.copy()
wc_prac_orig = pd.read_csv(WC_Prac,quotechar='"',skipinitialspace=True, keep_default_na=False)
wc_prac = wc_prac_orig.copy()
wc_all_orig = pd.read_csv(WC_All,quotechar='"',skipinitialspace=True, keep_default_na=False)
wc_all = wc_all_orig.copy()

providers_table = pd.read_csv('Provider_list.csv')
providers_table = providers_table.dropna().copy()
provider_dict = providers_table.to_dict('index')

####need to add row Identifiers to each file so you can match the original formatting of the name to the file currently being generated.

def normalize(s):
    #print(s)
    s = s.lower()
    s = s.replace(" ", "")
    s = ''.join([i for i in s if i not in frozenset(string.punctuation)])
    return s

def update_pcp(clinic_id, wc_id, df):
    clinic_npi = df.loc[(df['ID'] == clinic_id) & (df['Wellcentive Patient ID'] == wc_id)]['NPI']
    wc_npi = df.loc[(df['ID'] == clinic_id) & (df['Wellcentive Patient ID'] == wc_id)]['Physicians NPI']
    if df.loc[(df['ID'] == clinic_id) & (df['Wellcentive Patient ID'] == wc_id)]['Patient Status'] != 'Active':
        return clinic_npi
    
    

clinic_pats['Last Name'] = clinic_pats['Last Name'].apply(normalize)
clinic_pats['First Name'] = clinic_pats['First Name'].apply(normalize)

wc_prac['Patient Last Name'] = wc_prac['Patient Last Name'].apply(normalize)
wc_prac['Patient First Name'] = wc_prac['Patient First Name'].apply(normalize)

wc_all['Patient Last Name'] = wc_all['Patient Last Name'].apply(normalize)
wc_all['Patient First Name'] = wc_all['Patient First Name'].apply(normalize)

#patients in WC but not in Clinic
matching = clinic_pats.merge(wc_prac, how='right', left_on=['Last Name', 'First Name', 'Birth Date'], right_on=['Patient Last Name', 'Patient First Name', 'Date Of Birth'])
to_inactivate = matching[matching.isnull().any(axis=1)].copy()
to_inactivate = to_inactivate[to_inactivate['Patient Status'] != 'Not Active'].copy()
to_inactivate = to_inactivate[to_inactivate['Physician Last Name'] != 'WVCHealth'].copy()
to_inactivate = to_inactivate[['Wellcentive Patient ID']].copy()
GI_base = to_inactivate.merge(wc_prac_orig, how='left', on='Wellcentive Patient ID')
GI_required = GI_base[['Patient First Name', 'Patient Last Name', 'Date Of Birth', 'Gender', 'Physician First Name', 'Physician Last Name', 'Physician NPI']].copy()
GI_required['Date Of Birth'] = pd.to_datetime(GI_required['Date Of Birth'], infer_datetime_format=True)
GI_required['Date Of Birth'] = GI_required['Date Of Birth'].apply(lambda x: x.strftime('%Y%m%d'))
GI_required['Active Status'] = 0
GI_required.to_csv('list of patients to inactivate.csv')


#patients in Clinic but inactive in WC
matching = clinic_pats.merge(wc_all, how='left', left_on=['Last Name', 'First Name', 'Birth Date'], right_on=['Patient Last Name', 'Patient First Name', 'Date Of Birth'])
matching = matching.merge(providers_table, how='left', left_on=['Preferred Caregiver'], right_on=['EMR Designation'])                                                                                           
id_mapping = matching[['ID', 'Wellcentive Patient ID']].copy()
inactives = matching[matching['Patient Status'] == 'Not Active'].copy()

GI_required = GI_base[['Patient First Name', 'Patient Last Name', 'Date Of Birth', 'First Name', 'Last Name', 'Birth Date', 'Gender_x', 'NPI', 'Address', 'City', 'Zip']]
GI_required.insert(7,'Active Status',1)
GI_required.insert(8,'PCP First Name', '')
GI_required.insert(9, 'PCP Last name', '')
GI_required.to_csv('patients to activate.csv')
