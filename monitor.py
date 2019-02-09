#!/usr/bin/env python
from __future__ import print_function
from src import *
from disconnect import disconnect_func

def observe(interval=5):
    if inet_reachable():
        print_with_ts('Monitoring until disconnection occurs (probe every ' + str(interval) + ' sec)...')

        while inet_reachable():
            print_dot()
            time.sleep(interval)
        print_and_log('')

    print_with_ts('Not connected to internet !')
    raise DisconnectedException('Disconnected !')

def watcher():
    try:
        while True:
            try:
                observe()
            except DisconnectedException as e:
                connect()
    except KeyboardInterrupt as e:
        print_with_ts('Interrupted !', pre='\n')
        '''
        try:
            disconnect_func()
        except Exception as e:
            print_with_ts('### Ignoring ex on cleanup : ' + str(e))
        '''
        print_with_ts("Closing driver...")
        driver.close()

if __name__ == '__main__':
    print_with_ts('Started')

    handle_creds()

    # get_driver()

    watcher()

    print_with_ts('Done.')