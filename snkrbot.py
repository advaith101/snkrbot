import os
import sys
import six
import platform
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
import keyboard
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType
from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
from selenium.webdriver.common.action_chains import ActionChains


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
	return proxy

#Generates credit card for given entity
async def generateCard(entity):
	#TODO
	pass

#Checks if connections is there (i.e. if proxy works)
async def has_connection(driver):
    try:
        driver.find_element_by_xpath('//span[@jsselect="heading" and @jsvalues=".innerHTML:msg"]')
        return False
    except: return True

#Checks for ad popup and kills it if present
async def kill_ads(driver):
	#Check if ad is present
	await asyncio.sleep(5)
	try:
		ad = WebDriverWait(driver, 2).until(
			EC.visibility_of_all_elements_located((By.XPATH, "//div[@role='dialog']")))
		print('1')
		await asyncio.sleep(3)
		actions = ActionChains(driver)
		for i in range(6):
			actions.send_keys(Keys.TAB)
			actions.perform()
		if "windows" in platform.platform(terse=True).lower() or "linux" in platform.platform(terse=True).lower():
			actions.send_keys(Keys.ENTER)
			actions.perform()
		else:
			actions.send_keys(Keys.RETURN)
			actions.perform()
		print('2')
		return 1
	except Exception as e:
		print(type(e))
		return 0


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
		entity["shipping_aptno"] = input("Enter apt number (optional - press ENTER if not applicable): ")
		entity["shipping_zip"] = input("Enter zip code: ")
		entity["shipping_city"] = input("Enter city: ")
		entity["shipping_state"] = input("Enter State: ")
		print("\nEnter personal details for email {} below".format(emails[i]))
		entity["first_name"] = input("Enter first name: ")
		entity["last_name"] = input("Enter last name: ")
		entity["telephone"] = input("Enter telephone number: ")
		entity["card_no"] = input("Enter credit card number: ")
		entity["card_exp_mm"] = input("Enter 2-digit credit card expiry month (eg. 08, 11): ")
		entity["card_exp_yy"] = input("Enter 2-digit credit card expiry year (eg. 19, 21): ")
		entity["card_pin"] = input("Enter credit card pin (eg. 221): ")
		#assign credit card - TODO
		entities.append(entity)
	print("Check your entities:\n{}".format(entities))
	return entities

#Run single instance of a web driver buying the shoe for the given entity
async def run_single_instance(entity, mode="banner", model=None, size=None, productID=None):
	ad_is_killed = False
	while 1:
		# proxy = await generateProxy()
		# proxy_addr = proxy['ip'] + ':' + str(proxy['port'])
		# print(proxy_addr)
		# webdriver.DesiredCapabilities.CHROME['proxy'] = {
		#     "httpProxy":proxy_addr,
		#     "ftpProxy":proxy_addr,
		#     "sslProxy":proxy_addr,
		#     "proxyType":"MANUAL",
		# }
		#start web driver and navigate to product page
		FOOTLOCKER_HOME_URL = "https://www.footlocker.com/"
		FOOTLOCKER_PRODUCT_URL = "https://www.footlocker.com/en/product/~/{}.html".format(productID) if productID != None else None
		# FOOTLOCKER_HOME_URL = "https://www.facebook.com/"
		LOGGER = logging.getLogger()
		driver = webdriver.Chrome(executable_path='./chromedriver')
		try:
			driver.get(FOOTLOCKER_HOME_URL)
			break
		except:
			driver.close()
			exit()
			continue
	if mode == "banner":
		while 1:
			try:
				search = driver.find_element_by_xpath('//a[@type="link"]')
				break
			except:
				await asyncio.sleep(5)
				continue
		search.click()
		if ad_is_killed == False:
			i = await kill_ads(driver)
			ad_is_killed = True if i == 1 else False
		possible_shoes = WebDriverWait(driver, 20).until(
	 		EC.visibility_of_all_elements_located((By.CLASS_NAME, "ProductCard")))
		print("Number of Shoes from Search: {}".format(len(possible_shoes)))
		possible_shoes[0].click()
	elif mode == "productID" and productID != None:
		try:
			driver.get(FOOTLOCKER_PRODUCT_URL)
		except:
			print("\nError - Product page not found\n")
			driver.close()
			exit()
	else:
		while 1:
			try:
				search = driver.find_element_by_name("query")
				break
			except:
				await asyncio.sleep(5)
				continue
		search.send_keys(model)
		if "windows" in platform.platform(terse=True).lower() or "linux" in platform.platform(terse=True).lower():
			search.send_keys(Keys.ENTER)
		else:
			search.send_keys(Keys.RETURN)
		if ad_is_killed == False:
			i = await kill_ads(driver)
			ad_is_killed = True if i == 1 else False
		possible_shoes = WebDriverWait(driver, 20).until(
	 		EC.visibility_of_all_elements_located((By.CLASS_NAME, "ProductCard")))
		print("Number of Shoes from Search: {}".format(len(possible_shoes)))
		possible_shoes[0].click()

	#select size and add to cart
	if ad_is_killed == False:
		i = await kill_ads(driver)
		ad_is_killed = True if i == 1 else False
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
	#wait 10s for size buttons to be clickable
	for i in range(0,10):
		try:
			size_label[0].click()
			break
		except:
			await asyncio.sleep(1)
			continue
	if ad_is_killed == False:
		i = await kill_ads(driver)
		ad_is_killed = True if i == 1 else False
	cart_path = '//button[text()="Add To Cart"]'
	add_to_cart = WebDriverWait(driver, 20).until(
 		EC.visibility_of_all_elements_located((By.XPATH, cart_path)))
	print("Add To Cart elements found: {}".format(len(add_to_cart)))
	if len(add_to_cart) != 1:
		error = "Error selecting adding to cart"
		driver.close()
		raise Exception(error)
	while 1:
		try:
			add_to_cart[0].click()
			break
		except: continue

	#do recaptcha and add shoe to cart again once recaptcha is finished
	recaptcha_compete = input("\nCompete ReCaptcha. Press ENTER when ReCaptcha is finished: ")
	if recaptcha_compete != "":
		driver.close()
		print("\n ReCaptcha failed, exiting..")
		exit()
	#handle weird footlocker api error when finishing recaptcha (just go back to product page and add to cart and should work)
	if "api" in driver.current_url or "product" not in driver.current_url:
		driver.execute_script("window.history.go(-1)")
	print(driver.current_url)
	size_label = WebDriverWait(driver, 20).until(
			EC.visibility_of_all_elements_located((By.XPATH, size_path)))
	if len(size_label) != 1:
		error = "Error selecting size"
		driver.close()
		raise Exception(error)
	for i in range(0,10):
		try:
			size_label[0].click()
			break
		except:
			await asyncio.sleep(1)
			continue
	cart = WebDriverWait(driver, 20).until(
			EC.visibility_of_all_elements_located((By.XPATH, cart_path)))
	print("\nAdd To Cart elements found: {}".format(len(cart)))
	if len(cart) != 1:
		error = "Error selecting adding to cart"
		driver.close()
		raise Exception(error)
	while 1:
		try:
			cart[0].click()
			break
		except: continue

	#go to cart and proceed to checkout
	view_cart_path = '//a[text()="View Cart"]'
	view_cart = WebDriverWait(driver, 20).until(
			EC.visibility_of_all_elements_located((By.XPATH, view_cart_path)))
	if len(view_cart) != 1:
		error = "Error in going to cart"
		driver.close()
		raise Exception(error)
	while 1:
		try:
			view_cart[0].click()
			break
		except: continue
	guest_chkout_path = '//a[text()="Guest Checkout"]'
	guest_chkout = WebDriverWait(driver, 20).until(
			EC.visibility_of_all_elements_located((By.XPATH, guest_chkout_path)))
	if len(guest_chkout) != 1:
		error = "Error in going to cart"
		driver.close()
		raise Exception(error)
	if ad_is_killed == False:
		i = await kill_ads(driver)
		ad_is_killed = True if i == 1 else False
	while 1:
		try:
			guest_chkout[0].click()
			break
		except: continue

	#enter personal and shipping info
	fname = WebDriverWait(driver, 20).until(
				EC.visibility_of_all_elements_located((By.XPATH, '//input[@name="firstName"]')))
	fname[0].send_keys(entity['first_name'])
	lname = WebDriverWait(driver, 20).until(
				EC.visibility_of_all_elements_located((By.XPATH, '//input[@name="lastName"]')))
	lname[0].send_keys(entity['last_name'])
	email = WebDriverWait(driver, 20).until(
				EC.visibility_of_all_elements_located((By.XPATH, '//input[@name="email"]')))
	email[0].send_keys(entity['email'])
	phone = WebDriverWait(driver, 20).until(
				EC.visibility_of_all_elements_located((By.XPATH, '//input[@name="phone"]')))
	phone[0].send_keys(entity['telephone'])
	save_n_continue = WebDriverWait(driver, 20).until(
				EC.visibility_of_all_elements_located((By.XPATH, '//button[text()="Save & Continue"]')))
	while 1:
		try:
			save_n_continue[0].click()
			break
		except: continue
	st_address = WebDriverWait(driver, 20).until(
				EC.visibility_of_all_elements_located((By.XPATH, '//input[@name="line1"]')))
	st_address[0].send_keys(entity["shipping_stinfo"])
	if entity['shipping_aptno'] != "":
		aptno = WebDriverWait(driver, 20).until(
				EC.visibility_of_all_elements_located((By.XPATH, '//input[@name="line2"]')))
		aptno[0].send_keys(entity["shipping_aptno"])
	postal = WebDriverWait(driver, 20).until(
				EC.visibility_of_all_elements_located((By.XPATH, '//input[@name="postalCode"]')))
	postal[0].send_keys(entity["shipping_zip"])
	await asyncio.sleep(2)
	print("2222")
	save_n_continue2 = WebDriverWait(driver, 20).until(
				EC.visibility_of_all_elements_located((By.XPATH, '//button[text()="Save & Continue"]')))
	while 1:
		try:
			save_n_continue2[0].click()
			break
		except: continue
	await asyncio.sleep(3)
	print("3333")
	try:
		verify_addr = WebDriverWait(driver, 6).until(
					EC.visibility_of_all_elements_located((By.XPATH, '//h3[text()="Verify Your Address"]')))
		save_n_continue3 = WebDriverWait(driver, 6).until(
					EC.visibility_of_all_elements_located((By.XPATH, '//button[@type="submit"]')))
		if len(save_n_continue3) > 0:
			while 1:
				try:
					save_n_continue3[0].click()
					break
				except: continue
	except: pass
	await asyncio.sleep(5)

	#enter card info
	print("\nEntering credit card info... This doesn't work sometimes due to high security measures by footlocker.\n")
	# while credit_card_option != "":
	iframes = WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.XPATH,"//iframe[@class='js-iframe']")))
	print("found iframes for entering card info. number of iframes = {}".format(len(iframes)))
	iframes[0].click()
	await asyncio.sleep(1)
	actions = ActionChains(driver)
	actions.send_keys(entity["card_no"])
	actions.perform()
	print("entered card number")
	await asyncio.sleep(1)
	iframes[1].click()
	await asyncio.sleep(1)
	actions = ActionChains(driver)
	actions.send_keys(entity["card_exp_mm"])
	actions.perform()
	print("entered card expiry month")
	await asyncio.sleep(1)
	iframes[2].click()
	await asyncio.sleep(1)
	actions = ActionChains(driver)
	actions.send_keys(entity["card_exp_yy"])
	actions.perform()
	print("entered card expiry year")
	await asyncio.sleep(1)
	iframes[3].click()
	await asyncio.sleep(1)
	actions = ActionChains(driver)
	actions.send_keys(entity["card_pin"])
	actions.perform()
	print("entered card pin")

	await asyncio.sleep(2)

	#place order
	cururl = driver.current_url
	place_order = WebDriverWait(driver, 20).until(
				EC.visibility_of_all_elements_located((By.XPATH, '//button[text()="Place Order"]')))
	if len(place_order) > 0:
		while 1:
			try:
				place_order[0].click()
				break
			except: continue
	else:
		raise Exception("Could not find or click place order button")

	#check if order went through
	await asyncio.sleep(1)
	print("\nSuccess - Shoe Ordered") if driver.current_url != cururl else print("\nFailure - Check your information, something is wrong with it.")
	return 0 if driver.current_url != cururl else 1










### END OF HELPER FUNCTIONS ###



### MAIN SNKRBOT FUNCTION ###
async def run_snkrbot():

	###for testing purposes only###
	dummy_entity = {
		"email": "sahajveera@gmail.com",
		"shipping_stinfo": "1070 Hemphill Avenue",
		"shipping_zip": "30318",
		"shipping_city": "Atlanta",
		"shipping_state": "GA",
		"shipping_aptno": "",
		"first_name": "Sahajveer",
		"last_name": "Anand",
		"telephone": "2018353507",
		"card_no": "4111111111111111",
		"card_exp_mm": "03",
		"card_exp_yy": "24",
		"card_pin": "858"
	}

	print("\n\n Initializing SnkrBot... Bot Start Time: {}\n\n".format(datetime.datetime.now()))
	mode = input("Which mode would you like to use?\n\n1. Banner: Navigates to shoe based on top banner of homepage (useful for new drops)\n2. Search: Searches for shoe based on your shoe name\n3. ProductID: Based on your productID\n\nEnter the number of your choice: ")
	if mode == "2":
		print("Enter Shoe Info Below")
		model = input("Shoe Model Name (eg. Kobe 11, Jordan Retro 3, etc): ")
	elif mode == "3":
		product_id = input("Enter productID: ")
	size = str(np.random.randint(low=9, high=15))
	format_mode = lambda i : ["banner", "search", "productID"][int(i)-1]
	success = await run_single_instance(dummy_entity, mode=format_mode(mode), model=model if mode == "2" else None, size=size, productID=product_id if mode == "3" else None)
	sys.exit(success)
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
