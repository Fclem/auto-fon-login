#!/usr/bin/env python
from __future__ import print_function
from src import *

random_disconnect_url = 'https://telekom.portal.fon.com/SRCDTA01/fon/972cdbd54e855df583d29fc8b516ac6482bf6028?res=postaccessportal&nasid=D4-21-22-DB-4A-60&uamip=172.17.2.1&uamport=3990&mac=B8-27-EB-A2-E3-AD&ip=172.17.2.2&userurl=http%3A%2F%2Fperdu.com%2F#/welcome'

def disconnect_func():
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
    printT('Started')
    get_driver()
    navigate(random_disconnect_url)
    disconnect_func()
