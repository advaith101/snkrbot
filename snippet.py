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
            ##method 1
            # elem = driver.find_elements_by_id("human-contact-form")
            # elem[0].submit()
            ##method 2
            driver.execute_script('grecaptcha.execute();')
            ##method 3
            # driver.execute_script("document.getElementsByName('post')[0].submit();");
            time.sleep(2)
            pause = input("Pause")
            # submit = driver.find_element_by_xpath("//button[text()='Submit']")
            # submit.style.visibility = "visible"
            # submit.style.display = "block"
            # submit.click()
            status = 1