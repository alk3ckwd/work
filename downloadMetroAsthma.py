import json
import http.client
import os
import urllib
import pandas as pd
import numpy as np
import pysftp

def authenticate(hostname, client_id, client_secret, username, password):
    """ Authenticate via username/password. Returns json token object.
     
    Args:
    string hostname - hostname like "myaccount.sharefile.com"
    string client_id - OAuth2 client_id key
    string client_secret - OAuth2 client_secret key
    string username - my@user.name
    string password - my password """
 
    uri_path = '/oauth/token'
     
    headers = {'Content-Type':'application/x-www-form-urlencoded'}
    params = {'grant_type':'password', 'client_id':client_id, 'client_secret':client_secret,
              'username':username, 'password':password}
     
    https = http.client.HTTPSConnection(hostname)

    https.request('POST', uri_path, urllib.parse.urlencode(params), headers=headers)
    response = https.getresponse()
    str_response = response.read().decode('utf-8')
     
    #print(response.status, response.reason)
    token = None
    if response.status == 200:
        token = json.loads(str_response)
        #print('Received token info', token)
     
    https.close()
    return token
 
def get_authorization_header(token):
    return {'Authorization':'Bearer %s'%(token['access_token'])}
     
def get_hostname(token):
    return '%s.sf-api.com'%(token['subdomain'])

def get_folder_contents(token, item_id):
    """ Get a folder using some of the common query parameters that are available. This will
    add the expand, select parameters. The following are used:
     
    expand=Children to get any Children of the folder
    select=Id,Name,Children/Id,Children/Name,Children/CreationDate to get the Id, Name of the folder
    and the Id, Name, CreationDate of any Children
 
    Args:
    dict json token acquired from authenticate function
    string item_id - a folder id """
 
    uri_path = '/sf/v3/Items(%s)?$expand=Children&$select=Id,Name,Children/Id,Children/Name,Children/CreationDate'%(item_id)
    #print('GET %s%s'%(get_hostname(token), uri_path))
    https = http.client.HTTPSConnection(get_hostname(token))
    https.request('GET', uri_path, headers=get_authorization_header(token))
    response = https.getresponse()
    str_response = response.read().decode('utf-8')
     
    #print(response.status, response.reason)
    items = json.loads(str_response)
    #print(items['Id'], items['Name'])
    if 'Children' in items:
        children = items['Children']
        for child in children:
            #print(child['Id'], child['CreationDate'], child['Name'])
            if 'chaupload' in child['Name']:
                file_path = 'S:/Matt McVicar/Metro Ashtma uploader/' + child['Name']
                if not os.path.isfile(file_path):
                    #print("Found new file: " + child['Name'])
                    download_item(token, child['Id'], file_path)
                    return child['Name']
                    #print("Downloaded to: " + file_path)
    https.close()
    

def download_item(token, item_id, local_path):
    """ Downloads a single Item. If downloading  folder the local_path name should end in .zip.
     
    Args:
    dict json token acquired from authenticate function
    string item_id - the id of the item to download
    string local_path - where to download the item to, like "c:\\path\\to\\the.file" """
 
    uri_path = '/sf/v3/Items(%s)/Download'%(item_id)
    #print('GET %s%s'%(get_hostname(token), uri_path))
    https = http.client.HTTPSConnection(get_hostname(token))
    https.request('GET', uri_path, headers=get_authorization_header(token))
    response = https.getresponse()
    #str_response = response.read().decode('utf-8')
    location = response.getheader('location')
    redirect = None
    if location:
        redirect_uri = urllib.parse.urlparse(location)
        redirect = http.client.HTTPSConnection(redirect_uri.netloc)
        redirect.request('GET', '%s?%s'%(redirect_uri.path, redirect_uri.query))
        response = redirect.getresponse()
         
    with open(local_path, 'wb') as target:
        b = response.read(1024*8)
        while b:
            target.write(b)
            b = response.read(1024*8)
             
    #print(response.status, response.reason)
    https.close()
    if redirect:
        redirect.close()


        
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
    df['TYPE OF ASTHMA VISIT'] = df['TYPE OF ASTHMA VISIT'].apply(map_enc_type)
    df.rename(columns = {'TYPE OF ASTHMA VISIT':'Type','Enc Date':'Date'}, inplace = True)
    return df
    
def spiro(df):
    df.rename(columns = {'SPIROMETRY DATE DONE':'Date'}, inplace = True)
    df.insert(3,'Type','Spirometry')
    return df
    
def environ(df):
    df.rename(columns = {'ENVIRONMENTAL ASSESSMENT DATE':'Date'}, inplace = True)
    df.insert(3,'Type','Asthma Environmental Triggers Assessment')
    return df

def actionplan(df):
    df.rename(columns = {'ASTHMA ACTION PLAN DONE':'Date'}, inplace = True)
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

def process(f):
    columns = ['Patient First','Patient Last','DOB','Type','Date']
    wc_df = pd.DataFrame(columns=columns)
    
    #df = pd.read_excel('S:\Matt McVicar\Metro Ashtma uploader\\' + f,sheetname='New')

    main_df = pd.read_excel('S:\Matt McVicar\Metro Ashtma uploader\\' + f,sheetname='New')
    wc_df = wc_df.append(encounters(main_df[['Patient First','Patient Last', 'DOB', 'TYPE OF ASTHMA VISIT','Enc Date']]),ignore_index=True)
    wc_df = wc_df.append(spiro(main_df[['Patient First','Patient Last', 'DOB', 'SPIROMETRY DATE DONE']]),ignore_index=True)  
    wc_df = wc_df.append(environ(main_df[['Patient First','Patient Last', 'DOB', 'ENVIRONMENTAL ASSESSMENT DATE']]),ignore_index=True)
    wc_df = wc_df.append(actionplan(main_df[['Patient First','Patient Last', 'DOB', 'ASTHMA ACTION PLAN DONE']]),ignore_index=True)
    wc_df = wc_df.dropna()
    wc_df = fix_dates(wc_df)
    wc_df = buffer_columns(wc_df)
    
    wc_df.to_csv('S:\Matt McVicar\Metro Ashtma uploader\GI Files\\' + f.replace('xlsx','csv'))

def upload(f):
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    conn = pysftp.Connection('data.wellcentive.com', username='CHA_CHF', password='V37aPO2bJ6e5wFcLoL+V', cnopts=cnopts)

    conn.put('S:\Matt McVicar\Metro Ashtma uploader\GI Files\\' + f.replace('xlsx','csv'))
        

if __name__ == '__main__':
    hostname = "metropediatrics.sharefile.com"
    username = "mmcvicar@ch-alliance.org"
    password = "$oftBall42"
    client_id = 'rVD369bgeGQARhvuYBSk5GFfpdIqEgwD'
    client_secret = 'zYfDGg3q6HZh27dGr3z0wduf4LwoJMnseT5F6uvrwl4v1NPN'
    #f = 'chaupload_2_06_17.xlsx'
    #process(f)
    token = authenticate(hostname, client_id, client_secret, username, password)
    if token:
        new_file = get_folder_contents(token, 'fo3d5a60-9db8-42d2-ad4f-a6601aa4ff9f')
        if new_file:
            process(new_file)
            upload(new_file)
        else:
            print("No new file")

