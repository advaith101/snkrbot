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
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType
from http_request_randomizer.requests.proxy.requestProxy import RequestProxy



### BEGINNING OF HELPER FUNCTIONS ###

async def generateProxy():
	url = "https://proxy-orbit1.p.rapidapi.com/v1/"
	querystring = {"location":"US","protocols":"socks4"}
	headers = {
	    'x-rapidapi-key': "3889c7d562mshc5aa5aa1b862ccep12d593jsn5db6c5fe0ec7",
	    'x-rapidapi-host': "proxy-orbit1.p.rapidapi.com"
	    }
	response = requests.request("GET", url, headers=headers, params=querystring)
	print(response.text)
	proxy = json.loads(response.text)
	return proxy['ip']

#Generates credit card for given entity
async def generateCard(entity):
	#TODO
	pass

#Generates entities
async def generateEntities():
	entities = []
	emails_input = input("Enter comma seperated list of emails (eg. john@abc.com, janet@def.com)")
	emails = [i.strip() for i in emails_input.split(",")]
	for i in range(0, len(emails)):
		entity = {}
		entity["email"] = emails[i]
		#get email address, shipping info, and telephone
		print("\nEnter details for email {} below\n".format(emails[i]))
		entity["shipping_stinfo"] = input("Enter street address (eg. 4180 Flowers Drive): ")
		entity["shipping_aptno"] = input("Enter apt number (optional - enter 'no' if not applicable): ")
		entity["shipping_zip"] = input("Enter zip code: ")
		entity["shipping_city"] = input("Enter city: ")
		entity["shipping_state"] = input("Enter State: ")
		print("\nEnter personal details for email {} below".format(emails[i]))
		entity["first_name"] = input("Enter first name: ")
		entity["last_name"] = input("Enter last name: ")
		entity["telephone"] = input("Enter telephone number: ")
		#assign credit card - TODO
		entities.append(entity)
	print("Check your entities:\n{}".format(entities))
	return entities

#Run single instance of a web driver buying the shoe for the given entity
async def run_single_instance(model, size, entity):
	# webdriver.DesiredCapabilities.CHROME['proxy'] = {
	#     "httpProxy":proxy['ip'],
	#     "ftpProxy":proxy['ip'],
	#     "sslProxy":proxy['ip'],
	#     "proxyType":"MANUAL",
	# }

	#start web driver and navigate to product page
	FOOTLOCKER_HOME_URL = "https://www.footlocker.com/"
	LOGGER = logging.getLogger()
	driver = webdriver.Chrome(executable_path='./chromedriver') 
	driver.get(FOOTLOCKER_HOME_URL)
	search = driver.find_element_by_name("query")
	search.send_keys(model)
	#search.send_keys(Keys.ENTER)
	search.send_keys(Keys.RETURN)
	possible_shoes = WebDriverWait(driver, 20).until(
 		EC.visibility_of_all_elements_located((By.CLASS_NAME, "ProductCard")))
	print("Number of Shoes from Search: {}".format(len(possible_shoes)))
	possible_shoes[0].click()

	#select size and add to cart
	if "." not in size:
		size += ".0"
	label_string = "" if len(size.split('.')[0]) >= 2 else "0"
	label_string += size.split('.')[0] + size.split('.')[1]
	size_path = '//label[@for="ProductDetails_radio_size_{}"]'.format(label_string)
	size_label = WebDriverWait(driver, 20).until(
 		EC.visibility_of_all_elements_located((By.XPATH, size_path)))
	if len(size_label) != 1:
		error = "Error selecting size"
		driver.close()
		raise Exception(error)
	size_label[0].click()
	cart_path = '//button[text()="Add To Cart"]'
	add_to_cart = WebDriverWait(driver, 20).until(
 		EC.visibility_of_all_elements_located((By.XPATH, cart_path)))
	print("Add To Cart elements found: {}".format(len(add_to_cart)))
	if len(add_to_cart) != 1:
		error = "Error selecting adding to cart"
		driver.close()
		raise Exception(error)
	add_to_cart[0].click()




### END OF HELPER FUNCTIONS ###



### MAIN SNKRBOT FUNCTION ###
async def run_snkrbot():

	###for testing purposes only###
	dummy_entity = {
		"email": "johnsmith@gmail.com",
		"shipping_stinfo": "4180 Flowers Drive",
		"shipping_zip": "30341",
		"shipping_city": "Atlanta",
		"shipping_state": "GA",
		"first_name": "John",
		"last_name": "Smith",
		"telephone": "9194757292"
	}

	print("\n\n Initializing SnkrBot...\n\n")
	print("Enter Shoe Info Below")
	model = input("Shoe Model Name (eg. Kobe 11, Jordan Retro 3, etc): ")
	size = input("Shoe Size (eg. 11, 13.5): ")
	await run_single_instance(model, size, dummy_entity)
	# entities = await generateEntities()
	# insances = []
	# for entity in entities:
	# 	instance = asyncio.create_task(run_single_instance(model, size, entity))
	# 	insances.append(instance)
	# for instance in insances:
	# 	await instance




#main method
if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	asyncio.ensure_future(run_snkrbot())
	loop.run_forever()
	loop.close()
