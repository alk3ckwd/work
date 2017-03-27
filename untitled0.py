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

wait = WebDriverWait(browser, 999)
element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#jobDownloadHref0 > span')))

browser.quit()
