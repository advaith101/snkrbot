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
		entity["card_no"] = input("Enter credit card number: ")
		entity["card_exp_mm"] = input("Enter 2-digit credit card expiry month (eg. 08, 11): ")
		entity["card_exp_yy"] = input("Enter 2-digit credit card expiry year (eg. 19, 21): ")
		entity["card_pin"] = input("Enter credit card pin (eg. 221): ")
		#assign credit card - TODO
		entities.append(entity)
	print("Check your entities:\n{}".format(entities))
	return entities

#Run single instance of a web driver buying the shoe for the given entity
async def run_single_instance(model, size, entity, mode="new_drop"):
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
		# FOOTLOCKER_HOME_URL = "https://www.facebook.com/"
		LOGGER = logging.getLogger()
		driver = webdriver.Chrome(executable_path='./chromedriver')
		try:
			driver.get(FOOTLOCKER_HOME_URL)
			break
		except:
			driver.close()
			continue
	if mode == "new_drop":
		while 1:
			try:
				search = driver.find_element_by_xpath('//a[@type="button"]')
				break
			except:
				await asyncio.sleep(5)
				continue
		search.click()
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
	#wait 10s for size buttons to be clickable
	for i in range(0,10):
		try:
			size_label[0].click()
			break
		except:
			await asyncio.sleep(1)
			continue
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
		except:
			continue

	#do recaptcha and add shoe to cart again once recaptcha is finished
	recaptcha_compete = input("\nCompete ReCaptcha. Enter '1' when ReCaptcha is finished: ")
	if recaptcha_compete != '1':
		driver.close()
		print("\n ReCaptcha failed, exiting..")
	#handle weird footlocker api error when finishing recaptcha (just go back to product page and add to cart and should work)
	if "api" in driver.current_url or "product" not in driver.current_url:
		driver.execute_script("window.history.go(-1)")
		print(driver.current_url)
		size = WebDriverWait(driver, 20).until(
				EC.visibility_of_all_elements_located((By.XPATH, size_path)))
		if len(size) != 1:
			error = "Error selecting size"
			driver.close()
			raise Exception(error)
		for i in range(0,10):
			try:
				size[0].click()
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
			except:
				continue

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
		except:
			continue
	guest_chkout_path = '//a[text()="Guest Checkout"]'
	guest_chkout = WebDriverWait(driver, 20).until(
			EC.visibility_of_all_elements_located((By.XPATH, guest_chkout_path)))
	if len(guest_chkout) != 1:
		error = "Error in going to cart"
		driver.close()
		raise Exception(error)
	print("\n If any ad pops up, close it")
	while 1:
		try:
			guest_chkout[0].click()
			break
		except:
			continue

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
		except:
			continue
	st_address = WebDriverWait(driver, 20).until(
				EC.visibility_of_all_elements_located((By.XPATH, '//input[@name="line1"]')))
	st_address[0].send_keys(entity["shipping_stinfo"])
	if entity['shipping_aptno'] != "no":
		aptno = WebDriverWait(driver, 20).until(
				EC.visibility_of_all_elements_located((By.XPATH, '//input[@name="line2"]')))
		aptno[0].send_keys(entity["shipping_aptno"])
	postal = WebDriverWait(driver, 20).until(
				EC.visibility_of_all_elements_located((By.XPATH, '//input[@name="postalCode"]')))
	postal[0].send_keys(entity["shipping_zip"])
	await asyncio.sleep(2)
	# city = WebDriverWait(driver, 20).until(
	# 			EC.visibility_of_all_elements_located((By.XPATH, '//input[@name="town"]')))
	# city[0].send_keys(entity["shipping_city"])
	# state = WebDriverWait(driver, 20).until(
	# 			EC.visibility_of_all_elements_located((By.XPATH, '//select[@name="region"]/option[text()={}]'.format(entity['shipping_state']))))
	# postal[0].click()
	print("2222")
	save_n_continue2 = WebDriverWait(driver, 20).until(
				EC.visibility_of_all_elements_located((By.XPATH, '//button[text()="Save & Continue"]')))
	while 1:
		try:
			save_n_continue2[0].click()
			break
		except:
			continue
	await asyncio.sleep(3)
	print("3333")
	save_n_continue3 = WebDriverWait(driver, 20).until(
				EC.visibility_of_all_elements_located((By.XPATH, '//button[@type="submit"]')))
	if len(save_n_continue3) > 0:
		while 1:
			try:
				save_n_continue3[0].click()
				break
			except:
				continue
	await asyncio.sleep(3)

	#enter card info
	credit_card_option = input("\n This doesn't work sometimes due to high security measures by footlocker. \nIf the bot pauses, enter the rest of credit card info and press '1' when complete: ")
	while credit_card_option != '1':
		WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[@class='js-iframe']")))
		card_no = WebDriverWait(driver, 20).until(
					EC.visibility_of_all_elements_located((By.XPATH, '//input[@id="encryptedCardNumber"]')))
		card_no[0].send_keys(entity["card_no"])
		driver.switch_to.default_content()
		WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[@class='js-iframe']")))
		card_exp_mm = WebDriverWait(driver, 20).until(
					EC.visibility_of_all_elements_located((By.XPATH, '//input[@id="encryptedExpiryMonth"]')))
		card_exp_mm[0].send_keys(entity["card_exp_mm"])
		driver.switch_to.default_content()
		WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[@class='js-iframe']")))
		card_exp_yy = WebDriverWait(driver, 20).until(
					EC.visibility_of_all_elements_located((By.XPATH, '//input[@id="encryptedExpiryYear"]')))
		card_exp_yy[0].send_keys(entity["card_exp_yy"])
		driver.switch_to.default_content()
		WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[@class='js-iframe']")))
		card_pin = WebDriverWait(driver, 20).until(
					EC.visibility_of_all_elements_located((By.XPATH, '//input[@id="encryptedSecurityCode"]')))
		card_pin[0].send_keys(entity["card_pin"])
		driver.switch_to.default_content()
	await asyncio.sleep(2)

	#place order
	place_order = WebDriverWait(driver, 20).until(
				EC.visibility_of_all_elements_located((By.XPATH, '//button[text()="Place Order"]')))
	if len(place_order) > 0:
		while 1:
			try:
				place_order[0].click()
				break
			except:
				continue
	else:
		raise Exception("Could not find or click place order button")

	print("\nInstance Completed")










### END OF HELPER FUNCTIONS ###



### MAIN SNKRBOT FUNCTION ###
async def run_snkrbot():

	###for testing purposes only###
	dummy_entity = {
		"email": "johnsmith@gmail.com",
		"shipping_stinfo": "1070 Hemphill Avenue",
		"shipping_zip": "30318",
		"shipping_city": "Atlanta",
		"shipping_state": "GA",
		"shipping_aptno": "no",
		"first_name": "John",
		"last_name": "Smith",
		"telephone": "9194757292",
		"card_no": "4111111111111111",
		"card_exp_mm": "08",
		"card_exp_yy": "21",
		"card_pin": "123"
	}

	print("\n\n Initializing SnkrBot...\n\n")
	print("Enter Shoe Info Below")
	model = input("Shoe Model Name (eg. Kobe 11, Jordan Retro 3, etc): ")
	size = input("Shoe Size (eg. 11, 13.5): ")
	await run_single_instance(model, size, dummy_entity, mode="search")
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
