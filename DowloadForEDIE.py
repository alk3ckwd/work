# -*- coding: utf-8 -*-
"""
Created on Fri Jan 27 08:47:07 2017

@author: mmcvicar
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

#Automate Chrome to log in to Wellcentive and download the file
chrome_options = Options()
prefs = {"download.default_directory": "S:\\Quality Improvement Initiatives\\Care Management\\2013-Popln Mgmt\\PPM Technology and Tools\\Wellcentive - Implementation\\EDIE Lists",
         "download.directory_upgrade": True,
         "download.propt_for_download": False}
chrome_options.add_experimental_option("prefs",prefs)

browser = webdriver.Chrome(executable_path='C:\\Users\\mmcvicar\\Downloads\\chromedriver.exe',chrome_options=chrome_options)
browser.get('https://app.wellcentive.com/CHA')

uname = browser.find_element_by_name('j_username')
uname.send_keys('cha admin')

pwrd = browser.find_element_by_name('j_password')
pwrd.send_keys('chachf5901')

pwrd.submit()

rpts = browser.find_element_by_css_selector('#reports')
rpts.click()

gen = browser.find_element_by_css_selector('#generate95 > div')
gen.click()

gencsv = browser.find_element_by_css_selector('#generate95 > div > ul > li:nth-child(3) > a')
gencsv.click()

jobs = browser.find_element_by_id('jobs-header-link')
jobs.click()

wait = WebDriverWait(browser, 999)
element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#jobDownloadHref0 > span')))
element.click()


import time
time.sleep(5)
import glob
import os
dlfile = max(glob.iglob('S:\\Quality Improvement Initiatives\\Care Management\\2013-Popln Mgmt\\PPM Technology and Tools\\Wellcentive - Implementation\\EDIE Lists\\*.crdownload'),key=os.path.getctime)

while os.path.isfile(dlfile):
    time.sleep(1)

browser.quit()


###Get the latest file (the one we just downloaded) and process it
newest = max(glob.iglob('S:\\Quality Improvement Initiatives\\Care Management\\2013-Popln Mgmt\\PPM Technology and Tools\\Wellcentive - Implementation\\EDIE Lists\\*.csv'), 
             key=os.path.getctime)

import pandas as pd
df = pd.read_csv(newest,header=1)


df.rename(columns = {'Wellcentive Patient ID':'MRN',
                     'Address Line1':'Address',
                     'ZIP':'Zip',
                     'Date Of Birth': 'DOB',
                     'Patient First Name':'First',
                     'Patient Last Name': 'Last',
                     'Home Phone':'Home'}, inplace = True)

cols = ['MRN','Address','City','State','Zip','DOB','Gender','Home','First','Last']


df = df[cols]

df['DOB'] = pd.to_datetime(df['DOB'], infer_datetime_format=True)
df['DOB'] = df['DOB'].apply(lambda x: x.strftime('%Y%m%d'))
df.insert(5, 'SSN', '')
df.insert(len(df.columns),'Facility','or_chfound_report')
df.fillna('',inplace=True)


filename = 'S:\\Quality Improvement Initiatives\\Care Management\\2013-Popln Mgmt\\PPM Technology and Tools\\Wellcentive - Implementation\\EDIE Lists\\EDIE_Roster_' + time.strftime('%B_%Y') + '.csv'
df.to_csv(filename,index=False)




### Upload to Wellcentive SFTP

import pysftp
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None
conn = pysftp.Connection('sftp.collectivemedicaltech.com', username='ch-alliance.org', password='U2279u07', cnopts=cnopts,port=7834)
conn.put(filename)





























