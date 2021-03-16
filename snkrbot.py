import os
import sys
import six
# import pause
import argparse
import logging.config
import re
import time
import random
import json
import mysql.connector as mysql
import pandas as pd
import numpy as np
import datetime
import asyncio
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
import stripe



### BEGINNING OF HELPER FUNCTIONS ###

async def generateProxy():
	#TODO
	pass

async def generateCard():
	#TODO
	pass

### END OF HELPER FUNCTIONS ###

### MAIN SNKRBOT FUNCTION ###
async def run_snkrbot():

	FOOTLOCKER_HOME_URL = "https://www.footlocker.com/"
	LOGGER = logging.getLogger()
	print("\n\n Initializing Bot...\n\n")

	# model = input("Enter Shoe Model Name (eg. Kobe 11, Jordan Retro 3, etc): ")
	# size = input("Enter Shoe Size (eg. 11, 13.5): ")
	# emails_input = input("Enter comma seperated list of emails (eg. john@abc.com, janet@def.com)")
	# emails = [i.strip() for i in emails_input.split(",")]

	# entities = []
	# for i in range(0, len(emails)):
	# 	entity = {}
	# 	#get email address, shipping info, and telephone
	# 	print("Enter details for email {} below \n".format(emails[i]))
	# 	entity["shipping_stinfo"] = input("Enter street address (eg. 4180 Flowers Drive): ")
	# 	entity["shipping_aptno"] = input("Enter apt number (optional - enter 'no' if not applicable): ")
	# 	entity["shipping_zip"] = input("Enter zip code: ")
	# 	entity["shipping_city"] = input("Enter city: ")
	# 	entity["shipping_state"] = input("Enter State: ")
	# 	print("Enter personal details for email {} below \n".format(emails[i]))
	# 	entity["first_name"] = input("Enter first name: ")
	# 	entity["last_name"] = input("Enter last name: ")
	# 	entity["telephone"] = input("Enter telephone number: ")
	# 	#assign credit card - TODO
	# 	entities.append(entity)

	# print("Check your entities:\n{}".format(entities))
	# for entity in entities:
	# 	#create proxy and web driver for each entity
	# 	driver = webdriver.Chrome() 
	# 	driver.get(FOOTLOCKER_HOME_URL)
	# 	elem = driver.find_element_by_css_selector('a.Hero-image')
	# 	print(len(elem))
	# 	print(elem)
	# 	elem.click()
	# 	print(driver.current_url)
	# 	driver.close()

	#create proxy and web driver for each entity
	driver = webdriver.Chrome(executable_path='./chromedriver') 
	driver.get(FOOTLOCKER_HOME_URL)
	elem = driver.find_element_by_class_name('Link')
	print(elem)
	elem.click()
	print(driver.current_url)
	driver.close()


if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	asyncio.ensure_future(run_snkrbot())
	loop.run_forever()
	loop.close()
