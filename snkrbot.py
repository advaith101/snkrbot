import os
import sys
import six
import platform
import argparse
import logging.config
import re
import time
import random
import json
import pandas as pd
import numpy as np
import datetime
import asyncio
import requests
import keyboard
import csv
import multiprocessing
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.options import Options
from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
from selenium.webdriver.common.action_chains import ActionChains
from fake_useragent import UserAgent
from random_user_agent.user_agent import UserAgent as UA
from random_user_agent.params import SoftwareName, OperatingSystem



### BEGINNING OF HELPER FUNCTIONS ###

def generateProxy():
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
def generateCard(entity):
	#TODO
	pass

#Checks if connections is there (i.e. if proxy works)
def has_connection(driver):
    try:
        driver.find_element_by_xpath('//span[@jsselect="heading" and @jsvalues=".innerHTML:msg"]')
        return False
    except: return True

#Checks for ad popup and kills it if present
def kill_ads(driver):
	#Check if ad is present
	time.sleep(5)
	try:
		ad = WebDriverWait(driver, 2).until(
			EC.visibility_of_all_elements_located((By.XPATH, "//div[@role='dialog']")))
		print('1')
		time.sleep(3)
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
def generateEntities():
	dummy_entities = []
	with open('dummy_entities.csv', newline='') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			dummy_entities.append(row)
	return dummy_entities

#Run single instance of a web driver buying the shoe for the given entity
def run_single_instance(entity, mode="banner", model=None, size=None, productID=None):
	ad_is_killed = False

	#setup proxy
	# proxy = generateProxy()
	# proxy_addr = proxy['ip'] + ':' + str(proxy['port'])
	# print(proxy_addr)
	# webdriver.DesiredCapabilities.CHROME['proxy'] = {
	#     "httpProxy":proxy_addr,
	#     "ftpProxy":proxy_addr,
	#     "sslProxy":proxy_addr,
	#     "proxyType":"MANUAL",
	# }

	#setup user agent
	options = webdriver.ChromeOptions()
	# ua = UserAgent()
	# user_agent = ua.random
	software_names = [SoftwareName.CHROME.value]
	operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
	user_agent_rotator = UA(software_names=software_names, operating_systems=operating_systems, limit=100)
	user_agent = user_agent_rotator.get_random_user_agent()
	# print('\n')
	# print(user_agent)
	options.add_argument(f'user-agent={user_agent}')


	#start web driver and navigate to product page
	FOOTLOCKER_HOME_URL = "https://www.footlocker.com/"
	FOOTLOCKER_PRODUCT_URL = "https://www.footlocker.com/en/product/~/{}.html".format(productID) if productID != None else None
	# TESTPAGE_HOME_URL = "https://www.facebook.com/"
	LOGGER = logging.getLogger()
	driver = webdriver.Chrome(executable_path='./chromedriver', options=options)
	try:
		driver.get(FOOTLOCKER_HOME_URL)
	except:
		driver.close()
		sys.exit("Unable to connect to URL - Check internet and proxy")
	if mode == "banner":
		while 1:
			try:
				search = driver.find_element_by_xpath('//a[@type="link"]')
				break
			except:
				time.sleep(5)
				continue
		search.click()
		if ad_is_killed == False:
			i = kill_ads(driver)
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
				time.sleep(5)
				continue
		search.send_keys(model)
		if "windows" in platform.platform(terse=True).lower() or "linux" in platform.platform(terse=True).lower():
			search.send_keys(Keys.ENTER)
		else:
			search.send_keys(Keys.RETURN)
		if ad_is_killed == False:
			i = kill_ads(driver)
			ad_is_killed = True if i == 1 else False
		possible_shoes = WebDriverWait(driver, 20).until(
	 		EC.visibility_of_all_elements_located((By.CLASS_NAME, "ProductCard")))
		print("Number of Shoes from Search: {}".format(len(possible_shoes)))
		possible_shoes[0].click()

	#select size and add to cart
	if ad_is_killed == False:
		i = kill_ads(driver)
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
			time.sleep(1)
			continue
	if ad_is_killed == False:
		i = kill_ads(driver)
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
	print("\nReCaptcha Time :)\n")
	for i in range(600):
		try:
			recaptcha_present = WebDriverWait(driver, 5).until(
				EC.visibility_of_all_elements_located((By.XPATH, '//div[@role="dialog"]')))
			time.sleep(3)
		except: break

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
			time.sleep(1)
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
		i = kill_ads(driver)
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
	time.sleep(2)
	print("2222")
	save_n_continue2 = WebDriverWait(driver, 20).until(
				EC.visibility_of_all_elements_located((By.XPATH, '//button[text()="Save & Continue"]')))
	while 1:
		try:
			save_n_continue2[0].click()
			break
		except: continue
	time.sleep(3)
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
	time.sleep(5)

	#enter card info
	print("\nEntering credit card info... This doesn't work sometimes due to high security measures by footlocker.\n")
	# while credit_card_option != "":
	iframes = WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.XPATH,"//iframe[@class='js-iframe']")))
	print("found iframes for entering card info. number of iframes = {}".format(len(iframes)))
	iframes[0].click()
	time.sleep(1)
	actions = ActionChains(driver)
	actions.send_keys(entity["card_no"])
	actions.perform()
	print("entered card number")
	time.sleep(1)
	iframes[1].click()
	time.sleep(1)
	actions = ActionChains(driver)
	actions.send_keys(entity["card_exp_mm"])
	actions.perform()
	print("entered card expiry month")
	time.sleep(1)
	iframes[2].click()
	time.sleep(1)
	actions = ActionChains(driver)
	actions.send_keys(entity["card_exp_yy"])
	actions.perform()
	print("entered card expiry year")
	time.sleep(1)
	iframes[3].click()
	time.sleep(1)
	actions = ActionChains(driver)
	actions.send_keys(entity["card_pin"])
	actions.perform()
	print("entered card pin")

	time.sleep(2)

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
	time.sleep(1)
	print("\nSuccess - Shoe Ordered") if driver.current_url != cururl else print("\nFailure - Check your information, something is wrong with it.")
	return 0 if driver.current_url != cururl else 1










### END OF HELPER FUNCTIONS ###



### MAIN SNKRBOT FUNCTION ###
def run_snkrbot():

	print("\n\n Initializing SnkrBot... Bot Start Time: {}\n\n".format(datetime.datetime.now()))
	mode = input("Which mode would you like to use?\n\n1. Banner: Navigates to shoe based on top banner of homepage (useful for new drops)\n2. Search: Searches for shoe based on your shoe name\n3. ProductID: Based on your productID\n\nEnter the number of your choice: ")
	if mode == "2":
		print("Enter Shoe Info Below")
		model = input("Shoe Model Name (eg. Kobe 11, Jordan Retro 3, etc): ")
	elif mode == "3":
		product_id = input("Enter productID: ")
	format_mode = lambda i : ["banner", "search", "productID"][int(i)-1]

	# success = run_single_instance(dummy_entity, mode=format_mode(mode), model=model if mode == "2" else None, size=size, productID=product_id if mode == "3" else None)
	# sys.exit(success)

	entities = generateEntities()
	pool = multiprocessing.Pool(processes=len(entities))
	for entity in entities:
		size = str(np.random.randint(low=18, high=30)/2)
		instance = pool.apply_async(run_single_instance, args=(entity, format_mode(mode), model if mode == "2" else None, size, product_id if mode == "3" else None))
	pool.close()
	pool.join()




#main method
if __name__ == '__main__':
	run_snkrbot()






