#!/usr/bin/env python
from __future__ import print_function
from src import *
from disconnect import disconnect_func

def observe(interval=5):
    if inet_reachable():
        printT('Monitoring until disconnection occurs (probe every ' + str(interval) + ' sec)...')

        while inet_reachable():
            print_dot()
            time.sleep(interval)
        print('')

    printT('Not connected to internet !')
    raise DisconnectedException('Disconnected !')

def watcher():
    try:
        while True:
            try:
                observe()
            except DisconnectedException as e:
                connect()
    except KeyboardInterrupt as e:
        printT('Interrupted !', pre='\n')
        try:
            disconnect_func()
            printT("Closing driver...")
            driver.close()
        except Exception as e:
            printT('### Ignoring ex on cleanup : ' + str(e))

if __name__ == '__main__':
    printT('Started')

    handle_creds()

    # get_driver()

    watcher()

    printT('Done.')