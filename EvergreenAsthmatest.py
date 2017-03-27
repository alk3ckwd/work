# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 14:54:54 2017

@author: mmcvicar
"""

import pandas as pd
import numpy as np

f = '02-12-2017 thru 02-18-2017.xlsx'
main_df = pd.read_excel('S:\Matt McVicar\Evergreen Asthma uploader\\' + f, sheetname='Sheet1', header=2)
main_df = main_df.reset_index(drop=True)

columns = ['Patient First','Patient Last','DOB','Type','Date']
wc_df = pd.DataFrame(columns=columns)

def map_enc_type(enc_type):
    encs = {
            'phone encounter':'asthma phone encounter',
            'asthma sick visit':'asthma sick visit',
            'specialist sick visit':'asthma sick visit',
            'asthma status check in office':'asthma status check (ASC)',
            'asthma well visit - maintenance':'asthma well visit',
            'specialist well visit':'asthma well visit',
            'office visit with RN/MA':'Asthma office visit with RN/MA'
            }
    if enc_type in encs.keys():
        return encs[enc_type]
    return np.NaN

def encounters(df):
    df['1 TYPE OF ASTHMA VISIT'] = df['1 TYPE OF ASTHMA VISIT'].apply(map_enc_type)
    df.rename(columns = {'1 TYPE OF ASTHMA VISIT':'Type','Enc Date':'Date'}, inplace = True)
    return df
    
def spiro(df):
    df.rename(columns = {'92SPIROMETRY DATE DONE':'Date'}, inplace = True)
    df.insert(3,'Type','Spirometry')
    return df
    
def environ(df):
    df.rename(columns = {'93ENVIRONMENTAL ASSESSMENT DATE':'Date'}, inplace = True)
    df.insert(3,'Type','Asthma Environmental Triggers Assessment')
    return df

def actionplan(df):
    df.rename(columns = {'94ASTHMA ACTION PLAN DONE':'Date'}, inplace = True)
    df.insert(3,'Type','Asthma Action Plan Completed')
    return df

def buffer_columns(df):
    df.insert(3,'Domain','Care')
    for i in range(5,8):
        df.insert(i,'Blank'+str(i),'')
    for i in range(9,19):
        df.insert(i,'Blank'+str(i),'')
    return df

def fix_dates(df):
    cols_to_fix = ['DOB','Date']
    for col in cols_to_fix:
        df[col] = pd.to_datetime(df[col], infer_datetime_format=True)
        df[col] = df[col].apply(lambda x: x.strftime('%Y%m%d'))
    return df
    
wc_df = wc_df.append(encounters(main_df[['Patient First','Patient Last', 'DOB', '1 TYPE OF ASTHMA VISIT','Enc Date']]),ignore_index=True)
wc_df = wc_df.append(spiro(main_df[['Patient First','Patient Last', 'DOB', '92SPIROMETRY DATE DONE']]),ignore_index=True)  
wc_df = wc_df.append(environ(main_df[['Patient First','Patient Last', 'DOB', '93ENVIRONMENTAL ASSESSMENT DATE']]),ignore_index=True)
wc_df = wc_df.append(actionplan(main_df[['Patient First','Patient Last', 'DOB', '94ASTHMA ACTION PLAN DONE']]),ignore_index=True)
wc_df = wc_df.dropna()
wc_df = fix_dates(wc_df)
wc_df = buffer_columns(wc_df)