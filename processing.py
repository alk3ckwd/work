import pandas as pd
import string
import tkinter as tk
from tkinter import filedialog

#######SET THESE VARIABLES BEFORE RUNNING#####

#As shown in WC
CLINIC_NAME = ['Metropolitan Pediatrics - Westside','Metropolitan Pediatrics - Happy Valley','Metropolitan Pediatrics - Northwest','Metropolitan Pediatrics - Gresham']
UNKNOWN_PCP_FIRST_NAME = 'Unknown'
UNKNOWN_PCP_LAST_NAME = 'Metropolitan Pediatrics'
UNKNOWN_PCP_NPI = '0000000000'

#As shown in clinic file
CLINIC_FILE_FIRST_NAME = 'PAT_FIRST_NAME' #WC = 'Patient First Name'
CLINIC_FILE_LAST_NAME = 'PAT_LAST_NAME' #WC = 'Patient Last Name'
CLINIC_FILE_DOB = 'PAT_DOB' #WC = 'Date Of Birth'
CLINIC_FILE_PCP = 'CURRENT_PCP_PROV_NAME' 
CLINIC_FILE_GENDER = 'PAT_SEX' #WC = 'Gender'
CLINIC_FILE_ID = 'PAT_MRN_ID' #WC = 'Wellcentive Patient ID'
CLINIC_FILE_ADDRESS = 'ADD_LINE_1' #WC = 'Patient Last Name'
CLINIC_FILE_CITY = 'CITY'
CLINIC_FILE_ZIP = 'ZIP'
CLINIC_MEDICAID = 'FamilyCare'

##############################################



root = tk.Tk()
root.withdraw()
clinic_list = filedialog.askopenfilename(title='List from Clinic')
WC_All = filedialog.askopenfilename(title='All Patients from WC')

clinic_pats_orig = pd.read_csv(clinic_list, quotechar='"', skipinitialspace=True, keep_default_na=False, encoding='iso-8859-1')
clinic_pats = clinic_pats_orig.copy()
wc_all_orig = pd.read_csv(WC_All, quotechar='"', skipinitialspace=True, keep_default_na=False)
wc_all = wc_all_orig.copy()

providers_table = pd.read_csv('Provider_list.csv')
providers_table = providers_table.dropna().copy()

def normalize(s):
    #print(s)
    s = s.lower()
    s = s.replace(" ", "")
    s = ''.join([i for i in s if i not in frozenset(string.punctuation)])
    return s

def set_pcp(clinic_id, wc_id, df):
    clinic_npi = df.loc[(df[CLINIC_FILE_ID] == clinic_id) & (df['Wellcentive Patient ID'] == wc_id)]['NPI']
    #wc_npi = df.loc[(df[CLINIC_FILE_ID] == clinic_id) & (df['Wellcentive Patient ID'] == wc_id)]['Physicians NPI']
    if df.loc[(df['ID'] == clinic_id) & (df['Wellcentive Patient ID'] == wc_id)]['Patient Status'] != 'Active':
        return clinic_npi
    

clinic_pats[CLINIC_FILE_LAST_NAME] = clinic_pats[CLINIC_FILE_LAST_NAME].apply(normalize)
clinic_pats[CLINIC_FILE_FIRST_NAME] = clinic_pats[CLINIC_FILE_FIRST_NAME].apply(normalize)
#clinic_pats['Clinic Name'] = CLINIC_NAME

payers = wc_all.groupby(by='Wellcentive Patient ID')['Payer Name'].apply(','.join).to_frame()
del wc_all['Payer Name']
wc_all = wc_all.merge(payers, left_on='Wellcentive Patient ID', right_index=True)

wc_all['Patient Last Name'] = wc_all['Patient Last Name'].apply(normalize)
wc_all['Patient First Name'] = wc_all['Patient First Name'].apply(normalize)



#patients in WC but not in Clinic
WC_clinic_pats = wc_all[wc_all['Primary Physician Provider Group'].isin(CLINIC_NAME)].copy()
matching = clinic_pats.merge(WC_clinic_pats, how='right', left_on=[CLINIC_FILE_LAST_NAME, CLINIC_FILE_FIRST_NAME, CLINIC_FILE_DOB], 
                             right_on=['Patient Last Name', 'Patient First Name', 'Date Of Birth'])

to_inactivate = matching[matching.isnull().any(axis=1)].copy()
to_inactivate = to_inactivate[to_inactivate['Patient Status'] != 'Not Active'].copy()

to_inactivate = to_inactivate[to_inactivate['Payer Name'].str.contains(CLINIC_MEDICAID) == False]
to_inactivate = to_inactivate[['Wellcentive Patient ID']].copy()
GI_base = to_inactivate.merge(wc_all_orig, how='left', on='Wellcentive Patient ID')
GI_required = GI_base[['Patient First Name', 'Patient Last Name', 'Date Of Birth', 'Gender', 'Physician First Name', 
                       'Physician Last Name', 'Physician NPI']].copy()

GI_required['Date Of Birth'] = pd.to_datetime(GI_required['Date Of Birth'], infer_datetime_format=True)
GI_required['Date Of Birth'] = GI_required['Date Of Birth'].apply(lambda x: x.strftime('%Y%m%d'))
GI_required.insert(3, 'Domain', 'Demographics')
GI_required.insert(4, 'First', GI_required['Patient First Name'])
GI_required.insert(5, 'Last', GI_required['Patient Last Name'])
GI_required.insert(6, 'DOB', GI_required['Date Of Birth'])
for i in [7,8]:
    GI_required.insert(i, 'blank' + str(i), '')

for i in [10,11, 12, 13]:
    GI_required.insert(i, 'blank' + str(i), '')
    
GI_required.insert(14,'Active Status',0)

for i in range(18, 45):
    GI_required.insert(i, 'blank' + str(i), '')

GI_required = GI_required.drop_duplicates(GI_required.columns.values.tolist(),keep='first')
GI_required.to_csv(UNKNOWN_PCP_LAST_NAME + '_patients_to_inactivate.csv')

#patients in Clinic but inactive in WC
matching = clinic_pats.merge(wc_all, how='left', left_on=[CLINIC_FILE_LAST_NAME, CLINIC_FILE_FIRST_NAME, CLINIC_FILE_DOB], 
                             right_on=['Patient Last Name', 'Patient First Name', 'Date Of Birth'])

matching = matching.merge(providers_table, how='left', left_on=[CLINIC_FILE_PCP], right_on=['EMR Designation'])

inactives = matching[matching['Patient Status'] == 'Not Active'].copy()
at_another_clinic = matching[matching['Patient Status'] == 'Active'].copy()
id_mapping = inactives[[CLINIC_FILE_ID, 'Wellcentive Patient ID']].copy()

GI_base = id_mapping.merge(wc_all_orig, how='left', on=['Wellcentive Patient ID']).copy()
GI_base = GI_base.merge(clinic_pats_orig, how='left', on=[CLINIC_FILE_ID]).copy()
GI_base = GI_base.merge(providers_table, how='left', left_on=[CLINIC_FILE_PCP], right_on=['EMR Designation'])

GI_required = GI_base[['Patient First Name', 'Patient Last Name', 'Date Of Birth', CLINIC_FILE_FIRST_NAME, CLINIC_FILE_LAST_NAME,
                       CLINIC_FILE_DOB, CLINIC_FILE_GENDER, 'NPI', CLINIC_FILE_ADDRESS, CLINIC_FILE_CITY, CLINIC_FILE_ZIP]].copy()

GI_required['Date Of Birth'] = pd.to_datetime(GI_required['Date Of Birth'], infer_datetime_format=True)
GI_required[CLINIC_FILE_DOB] = pd.to_datetime(GI_required[CLINIC_FILE_DOB], infer_datetime_format=True)
GI_required['Date Of Birth'] = GI_required['Date Of Birth'].apply(lambda x: x.strftime('%Y%m%d'))
GI_required[CLINIC_FILE_DOB] = GI_required[CLINIC_FILE_DOB].apply(lambda x: x.strftime('%Y%m%d'))

GI_required.insert(7,'PCP First Name','')
GI_required.insert(8,'PCP Last Name','')

GI_required.NPI = GI_required.NPI.fillna(UNKNOWN_PCP_NPI)
try:
    GI_required.loc[GI_required['NPI'] == UNKNOWN_PCP_NPI, ['PCP First Name', 'PCP Last Name']] = UNKNOWN_PCP_FIRST_NAME, UNKNOWN_PCP_LAST_NAME
except:
    pass

GI_required.insert(3,'Domain', 'Demographics')

for i in [7,8]:
    GI_required.insert(i, 'blank' + str(i), '')

for i in [10,11, 12, 13]:
    GI_required.insert(i, 'blank' + str(i), '')
    
GI_required.insert(14,'Active Status',1)

for i in range(18, 25):
    GI_required.insert(i, 'blank' + str(i), '')
    
GI_required.insert(26, 'blank 26','')

GI_required.insert(28, 'State', '')

for i in range(31, 46):
    GI_required['blank' + str(i)] = ''

GI_required = GI_required.drop_duplicates(GI_required.columns.values.tolist(),keep='first')
GI_required.to_csv(UNKNOWN_PCP_LAST_NAME + '_patients to activate.csv')