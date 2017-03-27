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
prefs = {"download.default_directory": "S:\\Quality Improvement Initiatives\\Asthma\\Metrics & Reports\\Daily CMART Download",
         "download.directory_upgrade": True,
         "download.propt_for_download": False}
chrome_options.add_experimental_option("prefs",prefs)
chrome_options.add_argument("-incognito")


browser = webdriver.Chrome(executable_path='C:\\Users\\mmcvicar\\Downloads\\chromedriver.exe',chrome_options=chrome_options)
browser.get('https://app.wellcentive.com/CHA')

uname = browser.find_element_by_name('j_username')
uname.send_keys('cha admin')

pwrd = browser.find_element_by_name('j_password')
pwrd.send_keys('chachf5901')

pwrd.submit()

refresh = browser.find_element_by_css_selector('#refresh_futures_report_2544')
refresh.click()

wait = WebDriverWait(browser, 999)
run = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#run')))
run.click()


element = wait.until(EC.element_to_be_clickable((By.ID,'close_job_notify_button')))
element.click()


viewReport = browser.find_element_by_css_selector('#reportTable > tbody > tr:nth-child(3) > td:nth-child(7) > input')
viewReport.click()

PCP = browser.find_element_by_css_selector('#reportPreviewHeader > div:nth-child(7) > div > label:nth-child(1)')
PCP.click()

export = browser.find_element_by_css_selector('#reportPreviewHeader > div:nth-child(8) > table > tbody > tr > td > div > button')
export.click()

gen = browser.find_element_by_css_selector('#generateCsv')
gen.click()

import time
time.sleep(5)


browser.quit()




























