import os
import time
import base64
import sys
import getpass
import datetime
from selenium import webdriver

class DisconnectedException(BaseException):
    pass

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

def printT(text):
    time = str(datetime.datetime.now())
    print('[' + time + '] ' + text)

def inet_reachable():
    return not bool(os.system("ping -D -c 1 -W 1 " + hostname + ' > /dev/null'))

def observe(interval=5):
    printT('Monitoring until disconnection occurs (probe every ' + str(interval) + ' sec)...')

    while inet_reachable():
        print '.',
        time.sleep(interval)
    print ''

    printT('Disconnected !')
    raise DisconnectedException('Disconnected !')

def get_driver():
    global driver
    printT('Running chromedriver')
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument("window-size=1920,1080")
    driver = webdriver.Chrome(chrome_options=options)
    return driver

def navigate(url=perdu):
    try:
        if not driver:
            get_driver()
        printT('Navigating to ' + url)
        driver.get(url)
        driver.implicitly_wait(10)
        printT('Loaded.')
    except Exception as e:
        printT('Was not able to get chrome driver : ' + str(e))
        # TODO : notify
        sys.exit(0)


def connect():
    navigate()

    try:
        tab = driver.find_element_by_class_name(login_tab_class_name)
        printT('### login tab : ' + str(tab))

        tab.click()
        driver.implicitly_wait(2)

        username = driver.find_element_by_name(username_input_field_name)
        username.clear()

        password = driver.find_element_by_name(password_input_field_name)
        password.clear()

        printT('Filling username and password')
        username.send_keys(base64.standard_b64decode(auth_username))
        password.send_keys(base64.standard_b64decode(auth_password))

        driver.implicitly_wait(2)

        button = driver.find_element_by_xpath(login_submit_button_xpath)
        printT('### button : ' + str(button))

        printT('Submitting...')
        button.click()
        # TODO : check for invalid creds message
        printT('Waiting for inet access confirmation...')

        while not inet_reachable():
            print '.',
            time.sleep(1)
        print ''

        if inet_reachable():
            printT("Logged In.")
        else:
            printT('something went wrong.')

        printT('saving final screen-shot...')
        driver.save_screenshot(final_screenshot_path)

    except Exception as ex:
        printT(str(ex))
        printT('Unrecoverable error')
        driver.save_screenshot(last_screenshot_path)
        printT('Saved state screenshot to ' + last_screenshot_path)

def disconnect():
    # FIXME : untested
    printT('Disconnecting...')
    button = driver.find_element_by_xpath(disconnect_button_xpath)
    printT('### button : ' + str(button))
    button.click()
    if not inet_reachable():
        printT('Now disconnected')
        exit(0)
    else:
        printT('Disconnection failed')
        exit(1)


if __name__ == '__main__':
    global auth_username, auth_password
    printT('Started')
    
    try:
        if not auth_username:
            auth_username = base64.standard_b64encode(raw_input('Enter login email : '))
            printT('email: ' + auth_username)

        if not auth_password:
            auth_password = base64.standard_b64encode(getpass.getpass('Enter login password : '))
    except KeyboardInterrupt:
        printT('Interrupted !')

    get_driver()

    try:
        while True:
            try:
                observe()
            except DisconnectedException as e:
                connect()
    except KeyboardInterrupt:
        printT('Interrupted !')
        printT("Closing driver...")
        driver.close()

    printT('Done.')