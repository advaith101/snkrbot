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
import scipy.interpolate as si
import datetime
import asyncio
import requests
import keyboard
import csv
import multiprocessing
import undetected_chromedriver as uc
uc.install()
import pickle
from bs4 import BeautifulSoup
from random import uniform, randint
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
from timeit import default_timer as timer
from twocaptcha import TwoCaptcha


##CONSTANT VARIABLES###

# Randomization Related
SHORT_MIN_RAND = .07
SHORT_MAX_RAND = .1
MIN_RAND        = 0.64
MAX_RAND        = 1.27
LONG_MIN_RAND   = 4.78
LONG_MAX_RAND = 11.1

# 2Captcha info
twocaptcha_api = "0b76765fc403384d58a4793b4e53c15a"

###END OF CONSTANT VARIABLES###


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
def kill_ads(driver, mode='robot'):
    #Check if ad is present
    time.sleep(5)
    if mode != 'human':
        try:
            ad = WebDriverWait(driver, 2).until(
                EC.visibility_of_all_elements_located((By.XPATH, "//div[@role='dialog']")))
            print('1')
            
            actions = ActionChains(driver)
            for i in range(6):
                wait_between(MIN_RAND,MAX_RAND)
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
    else:
        try:
            ad = WebDriverWait(driver, 2).until(
                EC.visibility_of_all_elements_located((By.XPATH, "//div[@role='dialog']")))
            print('1')
            location = ad[0].location
            x, y = location['x'], location['y']
            size = ad[0].size
            w, h = size['width'], size['height']
            acs = ActionChains(driver)
            acs.move_to_element(ad[0])
            acs.move_by_offset(w//2 + 15, 0)
            acs.click()
        except Exception as e:
            print(type(e))
            return 0

#Type in a human like behavior
def human_type(driver, text, mode=None):
    for i in range(len(text)):
        wait_between(SHORT_MIN_RAND, SHORT_MAX_RAND)
        driver.send_keys(text[i])


#Generates entities
def generateEntities():
    dummy_entities = []
    with open('dummy_entities.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            dummy_entities.append(row)
    return dummy_entities

# Using B-spline for simulate humane like mouse movments
def human_like_mouse_move(driver, start_element=None):
    action = ActionChains(driver)
    points = [[6, 2], [3, 2],[0, 0], [0, 2]]
    points = np.array(points)
    x = points[:,0]
    y = points[:,1]

    t = range(len(points))
    ipl_t = np.linspace(0.0, len(points) - 1, 100)

    x_tup = si.splrep(t, x, k=1)
    y_tup = si.splrep(t, y, k=1)

    x_list = list(x_tup)
    xl = x.tolist()
    x_list[1] = xl + [0.0, 0.0, 0.0, 0.0]

    y_list = list(y_tup)
    yl = y.tolist()
    y_list[1] = yl + [0.0, 0.0, 0.0, 0.0]

    x_i = si.splev(ipl_t, x_list)
    y_i = si.splev(ipl_t, y_list)

    if start_element != None:
        startElement = start_element

        action.move_to_element(startElement);
        action.perform();

    c = 5 # change it for more movement
    i = 0
    for mouse_x, mouse_y in zip(x_i, y_i):
        action.move_by_offset(mouse_x,mouse_y);
        action.perform();
        print("Move mouse to, %s ,%s" % (mouse_x, mouse_y))
        i += 1
        if i == c:
            break;

#Solve ReCaptcha
def do_captcha(driver):
    iframes = driver.find_elements_by_tag_name("iframe")
    driver.switch_to.frame(driver.find_elements_by_tag_name("iframe")[0])
    #find sitekey of captcha
    time.sleep(2)
    while 1:
        try:
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            iframe = soup.find('iframe', {'title' : 'reCAPTCHA'})['src']  
            possible_ks = iframe.split('&')
            break
        except:
            time.sleep(2)
            continue
    sitekey = ''
    for i in possible_ks:
        if i[0:2] == 'k=':
            sitekey = i[2:]
    print(iframe)
    print(sitekey)
    url = driver.current_url
    form = {"method": "userrecaptcha",
        "googlekey": sitekey,
        "key": twocaptcha_api, 
        "pageurl": iframe,
        "invisible": 1,
        "json": 1}
    print("TEST")
    response = requests.post('http://2captcha.com/in.php', data=form)
    request_id = response.json()['request']
    print(response.json())
    url = f"http://2captcha.com/res.php?key={twocaptcha_api}&action=get&id={request_id}&json=1"
    status = 0
    while not status:
        res = requests.get(url)
        print(res.json())
        if res.json()['status']==0:
            time.sleep(3)
        else:
            requ = res.json()['request']
            # js0 = f'document.getElementById("captcha-submit").style.visibility = "visible";'
            # jsn = f'document.getElementById("captcha-submit").style.display = "block";'
            js = f'document.getElementById("g-recaptcha-response").innerHTML="{requ}";'
            js1 = f'document.getElementById("g-recaptcha-response").style.visibility = "visible";;'
            js2 = f'document.getElementById("g-recaptcha-response").style.display = "block";'
            # driver.execute_script(js0)
            # driver.execute_script(jsn)
            driver.execute_script(js)
            driver.execute_script(js1)
            driver.execute_script(js2)
            # elem = driver.find_elements_by_id("human-contact-form")
            driver.execute_script('grecaptcha.execute();')
            # driver.execute_script("document.getElementsByName('post')[0].submit();");
            # elem[0].submit()
            time.sleep(2)
            pause = input("Pause")
            # submit = driver.find_element_by_xpath("//button[text()='Submit']")
            # submit.style.visibility = "visible"
            # submit.style.display = "block"
            # submit.click()
            status = 1
    # solver = TwoCaptcha(twocaptcha_api)
    # result = solver.recaptcha(sitekey=sitekey, url=url)
    # print(result)
    pause = input("Pause")
    


# Use time.sleep for waiting and uniform for randomizing
def wait_between(a, b):
    rand=uniform(a, b)
    time.sleep(rand)

#Run single instance of a web driver buying the shoe for the given entity
def run_single_instance(entity, mode="banner", model=None, size=None, productID=None, captcha_mode='solve'):
    time_elapsed = timer()
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
    # options = uc.ChromeOptions()
    # ua = UserAgent()
    # user_agent = ua.random
    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
    user_agent_rotator = UA(software_names=software_names, operating_systems=operating_systems, limit=100)
    user_agent = user_agent_rotator.get_random_user_agent()
    # print('\n')
    # print(user_agent)
    options.add_argument(f'user-agent={user_agent}')
    # options.add_argument("--incognito")
    options.add_extension('./buster.crx')


    #start web driver and navigate to product page
    FOOTLOCKER_HOME_URL = "https://www.footlocker.com/"
    FOOTLOCKER_PRODUCT_URL = "https://www.footlocker.com/en/product/~/{}.html".format(productID) if productID != None else None
    # TESTPAGE_HOME_URL = "https://www.facebook.com/"
    LOGGER = logging.getLogger()
    driver = webdriver.Chrome(options=options)
    # driver = uc.Chrome(options=options)
    try:
        driver.get(FOOTLOCKER_HOME_URL)
        if captcha_mode == 'bypass':
            cookies = pickle.load(open("cookies.pkl", "rb"))
            for cookie in cookies:
                driver.add_cookie(cookie)
    except:
        driver.close()
        sys.exit("Unable to connect to URL - Check internet and proxy")
    if mode == "banner":
        while 1:
            try:
                if ad_is_killed == False:
                    i = kill_ads(driver)
                    ad_is_killed = True if i == 1 else False
                search = driver.find_element_by_xpath('//a[@type="link"]')
                break
            except:
                time.sleep(2)
                continue
        wait_between(MIN_RAND, MAX_RAND)
        human_like_mouse_move(driver)
        search.click()
        if ad_is_killed == False:
            i = kill_ads(driver)
            ad_is_killed = True if i == 1 else False
        possible_shoes = WebDriverWait(driver, 20).until(
            EC.visibility_of_all_elements_located((By.CLASS_NAME, "ProductCard")))
        print("Number of Shoes from Search: {}".format(len(possible_shoes)))
        wait_between(MIN_RAND, MAX_RAND)
        human_like_mouse_move(driver)
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
        wait_between(MIN_RAND, MAX_RAND)
        human_like_mouse_move(driver)
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
            wait_between(MIN_RAND, MAX_RAND)
            human_like_mouse_move(driver)
            size_label[0].click()
            break
        except:
            time.sleep(1)
            continue
    if ad_is_killed == False:
        i = kill_ads(driver)
        ad_is_killed = True if i == 1 else False
    # ac = ActionChains(driver)
    # ac.click(size_label[0])
    # ac.send_keys(Keys.TAB)
    # ac.send_keys(Keys.TAB)
    # ac.send_keys(Keys.RETURN)
    # cart_path = '//button[text()="Add To Cart"]'
    cart_path = '//button[@type="submit"]'
    
    add_to_cart = WebDriverWait(driver, 20).until(
        EC.visibility_of_all_elements_located((By.XPATH, cart_path)))
    print("Add To Cart elements found: {}".format(len(add_to_cart)))
    if len(add_to_cart) != 1:
        error = "Error selecting adding to cart"
        driver.close()
        raise Exception(error)
    while 1:
        try:
            wait_between(MIN_RAND, MAX_RAND)
            human_like_mouse_move(driver)
            add_to_cart[0].click()
            break
        except: continue

    #do recaptcha and add shoe to cart again once recaptcha is finished
    print("\nReCaptcha Time :)\n")
    if captcha_mode == 'solve':
        # do_captcha(driver)
        # pause = input("Pause")

        # for i in range(600):
        #     try:
        #         recaptcha_present = WebDriverWait(driver, 5).until(
        #             EC.visibility_of_all_elements_located((By.XPATH, '//div[@role="dialog"]')))
                
        #     except: break
        pause = input("Press Enter when done with the Captcha")
        #handle weird footlocker api error when finishing recaptcha (just go back to product page and add to cart and should work)
        if "api" in driver.current_url or "product" not in driver.current_url:
            driver.execute_script("window.history.go(-1)")
        size_label = WebDriverWait(driver, 20).until(
                EC.visibility_of_all_elements_located((By.XPATH, size_path)))
        if len(size_label) != 1:
            error = "Error selecting size"
            driver.close()
            raise Exception(error)
        for i in range(0,10):
            try:
                wait_between(MIN_RAND, MAX_RAND)
                human_like_mouse_move(driver)
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
                wait_between(MIN_RAND, MAX_RAND)
                human_like_mouse_move(driver)
                cart[0].click()
                wait_between(MIN_RAND, MAX_RAND)
                human_like_mouse_move(driver)
                break
            except: continue
        pickle.dump( driver.get_cookies() , open("cookies.pkl","wb"))
    print(driver.current_url)

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
    wait_between(MIN_RAND, MAX_RAND)
    human_like_mouse_move(driver)
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
    wait_between(MIN_RAND, MAX_RAND)
    human_like_mouse_move(driver)
    fname = WebDriverWait(driver, 20).until(
                EC.visibility_of_all_elements_located((By.XPATH, '//input[@name="firstName"]')))
    fname[0].send_keys(entity['first_name'])
    wait_between(MIN_RAND, MAX_RAND)
    human_like_mouse_move(driver)
    lname = WebDriverWait(driver, 20).until(
                EC.visibility_of_all_elements_located((By.XPATH, '//input[@name="lastName"]')))
    lname[0].send_keys(entity['last_name'])
    wait_between(MIN_RAND, MAX_RAND)
    human_like_mouse_move(driver)
    email = WebDriverWait(driver, 20).until(
                EC.visibility_of_all_elements_located((By.XPATH, '//input[@name="email"]')))
    email[0].send_keys(entity['email'])
    wait_between(MIN_RAND, MAX_RAND)
    human_like_mouse_move(driver)
    phone = WebDriverWait(driver, 20).until(
                EC.visibility_of_all_elements_located((By.XPATH, '//input[@name="phone"]')))
    phone[0].send_keys(entity['telephone'])
    wait_between(MIN_RAND, MAX_RAND)
    human_like_mouse_move(driver)
    save_n_continue = WebDriverWait(driver, 20).until(
                EC.visibility_of_all_elements_located((By.XPATH, '//button[text()="Save & Continue"]')))
    while 1:
        try:
            save_n_continue[0].click()
            wait_between(MIN_RAND, MAX_RAND)
            human_like_mouse_move(driver)
            break
        except: continue
    st_address = WebDriverWait(driver, 20).until(
                EC.visibility_of_all_elements_located((By.XPATH, '//input[@name="line1"]')))
    st_address[0].send_keys(entity["shipping_stinfo"])
    wait_between(MIN_RAND, MAX_RAND)
    human_like_mouse_move(driver)
    if entity['shipping_aptno'] != "":
        aptno = WebDriverWait(driver, 20).until(
                EC.visibility_of_all_elements_located((By.XPATH, '//input[@name="line2"]')))
        aptno[0].send_keys(entity["shipping_aptno"])
        wait_between(MIN_RAND, MAX_RAND)
        human_like_mouse_move(driver)
    postal = WebDriverWait(driver, 20).until(
                EC.visibility_of_all_elements_located((By.XPATH, '//input[@name="postalCode"]')))
    postal[0].send_keys(entity["shipping_zip"])
    wait_between(MIN_RAND, MAX_RAND)
    human_like_mouse_move(driver)
    print("2222")
    save_n_continue2 = WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.XPATH, '//button[text()="Save & Continue"]')))
    while 1:
        try:
            save_n_continue2[0].click()
            wait_between(MIN_RAND, MAX_RAND)
            human_like_mouse_move(driver)
            break
        except: continue
    
    print("3333")
    try:
        verify_addr = WebDriverWait(driver, 6).until(
                    EC.visibility_of_all_elements_located((By.XPATH, '//h3[text()="Verify Your Address"]')))
        save_n_continue3 = WebDriverWait(driver, 6).until(
                    EC.visibility_of_all_elements_located((By.XPATH, '//button[@type="submit"]')))
        if len(save_n_continue3) > 0:
            while 1:
                try:
                    wait_between(MIN_RAND, MAX_RAND)
                    human_like_mouse_move(driver)
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
    wait_between(MIN_RAND, MAX_RAND)
    human_like_mouse_move(driver)
    time.sleep(1)
    iframes[1].click()
    time.sleep(1)
    actions = ActionChains(driver)
    actions.send_keys(entity["card_exp_mm"])
    actions.perform()
    wait_between(MIN_RAND, MAX_RAND)
    human_like_mouse_move(driver)
    print("entered card expiry month")
    time.sleep(1)
    iframes[2].click()
    time.sleep(1)
    actions = ActionChains(driver)
    actions.send_keys(entity["card_exp_yy"])
    actions.perform()
    wait_between(MIN_RAND, MAX_RAND)
    human_like_mouse_move(driver)
    print("entered card expiry year")
    time.sleep(1)
    iframes[3].click()
    time.sleep(1)
    actions = ActionChains(driver)
    actions.send_keys(entity["card_pin"])
    actions.perform()
    wait_between(MIN_RAND, MAX_RAND)
    human_like_mouse_move(driver)
    print("entered card pin")


    #place order
    # cururl = driver.current_url
    # place_order = WebDriverWait(driver, 20).until(
    #             EC.visibility_of_all_elements_located((By.XPATH, '//button[text()="Place Order"]')))
    # if len(place_order) > 0:
    #     while 1:
    #         try:
    #             place_order[0].click()
    #             break
    #         except: continue
    # else:
    #     raise Exception("Could not find or click place order button")

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
        # size = str(np.random.randint(low=18, high=30)/2)
        size = "12.0"
        # instance = pool.apply_async(run_single_instance, args=(entity, format_mode(mode), model if mode == "2" else None, size, product_id if mode == "3" else None))
        instance = run_single_instance(entity, format_mode(mode), model if mode == "2" else None, size, product_id if mode == "3" else None)
    pool.close()
    pool.join()
    print("\n\n Terminating SnkrBot... Bot Start Time: {}\n\n".format(datetime.datetime.now()))




#main method
if __name__ == '__main__':
    run_snkrbot()






