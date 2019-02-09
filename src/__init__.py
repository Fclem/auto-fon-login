from __future__ import print_function
import os
import time
import base64
import sys
import getpass
import datetime
from selenium import webdriver

class DisconnectedException(BaseException):
    pass

save_credentials_to_file = True

auth_username = ''
auth_password = ''

hostname = "fiere.fr"  # ping target for inet probe
perdu = "http://perdu.com" # opening page target to get Captive Portable page

chrome_driver_base_path = '/usr/lib/chromium-browser'

last_screenshot_path = '/home/clem/last.png'
final_screenshot_path = '/home/clem/final.png'

login_tab_class_name = 'tab-login-hotspot'
username_input_field_name = 'username'
password_input_field_name = 'password'

login_submit_button_xpath = '//*[@id="tab-tab-login-hotspot"]/div[1]/div/form/button'
disconnect_button_xpath = '//*[@id="top-section"]/div/div[6]/div[3]/div[1]/div[4]/a[3]/span'

os.environ['PATH'] += ':' + chrome_driver_base_path

driver = None

username_save_file = './.username'
password_save_file = './.password'

def read_from_file(path):
    if not os.path.isfile(path):
        return ''
    with open(path) as my_file:
        text = my_file.read()
        if len(text):
            printT('Loaded data from ' + str(path))
        return text

def save_to_file(path, content):
    with open(path, 'w') as my_file:
        my_file.write(content)
    printT('Saved data to ' + str(path))

def load_username():
    return read_from_file(username_save_file)

def load_password():
    return read_from_file(password_save_file)

def save_username():
    if save_credentials_to_file and auth_username.strip():
        save_to_file(username_save_file, auth_username)

def save_password():
    if save_credentials_to_file and auth_password.strip():
        save_to_file(password_save_file, auth_password)

def printT(text, pre=''):
    time = str(datetime.datetime.now())
    print(pre + '[' + time + '] ' + text)

def print_dot():
    print('.', end='')
    sys.stdout.flush()

def inet_reachable():
    return not bool(os.system("ping -D -c 3 -W 2 " + hostname + ' > /dev/null'))

def get_driver():
    global driver
    if not driver:
        printT('Running chromedriver')
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument("window-size=1920,1080")
        driver = webdriver.Chrome(chrome_options=options)
        driver.implicitly_wait(30)
    return driver

def navigate(url=perdu):
    try:
        get_driver()
        printT('Navigating to ' + url)
        driver.get(url)
        printT('Loaded.')
    except Exception as e:
        printT('Was not able to get chrome driver : ' + str(e))
        # TODO : notify
        sys.exit(0)

def handle_creds():
    global auth_username, auth_password

    if not len(auth_username):
        auth_username = load_username()
        while not auth_username:
            auth_username = base64.standard_b64encode(raw_input('Enter login email : '))
            save_username()

    if not len(auth_password):
        auth_password = load_password()
        while not auth_password:
            if save_credentials_to_file:
                print('WARNING : theses credentials will be stored on disk as CLEARTEXT.')
            auth_password = base64.standard_b64encode(getpass.getpass('Enter login password : '))
            save_password()

def connect():
    navigate()
    time.sleep(15)
    try:
        tab = driver.find_element_by_class_name(login_tab_class_name)
        printT('### login tab : ' + str(tab))
        tab.click()

        username = driver.find_element_by_name(username_input_field_name)
        username.clear()

        password = driver.find_element_by_name(password_input_field_name)
        password.clear()

        printT('Filling username and password')
        username.send_keys(base64.standard_b64decode(auth_username))
        password.send_keys(base64.standard_b64decode(auth_password))

        button = driver.find_element_by_xpath(login_submit_button_xpath)
        printT('### button : ' + str(button))

        printT('Submitting...')
        button.click()
        # TODO : check for invalid creds message
        printT('Waiting for inet access confirmation...')

        if not inet_reachable():
            while not inet_reachable():
                print_dot()
            print('')

        if inet_reachable():
            printT("Logged In.")
        else:
            printT('### Something went wrong.')

    except Exception as ex:
        printT('### Exception on connect : ' + str(ex))
        # printT('Unrecoverable error')
        # driver.save_screenshot(last_screenshot_path)
        # printT('Saved state screenshot to ' + last_screenshot_path)
