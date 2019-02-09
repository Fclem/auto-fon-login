import copy
import os
import time
import requests
# import Cookie
import base64
import cookielib, urllib2

password = 'VGVyYXphNTEx\n'
hostname = "fiere.fr"  # example
perdu = "http://perdu.com"
__portal = "https://telekom.portal.fon.com/SRCDTA01/fon/bdcd064dfc5cce9905f53e3615a1c4656d7529b6?res=logoff&uamip=172.17.2.1&uamport=3990&challenge=be37c3fac498793f944ef2818272996a&called=D4-21-22-DB-4A-60&mac=B8-27-EB-A2-E3-AD&ip=172.17.2.2&nasid=D4-21-22-DB-4A-60&sessionid=5c5c9cb600000001&userurl=http%3a%2f%2f%2f&md=6DD37CEE8EE25481A2519BA930C3199C"
login_url = ''
WISPstr = 'WISPAccessGatewayParam'
loginS = '<LoginURL>'
loginE = '</LoginURL>'
stage_2_url = 'https://telekom.portal.fon.com/FON_EXT/hotspot/de_DE/partial/start.html'
stage_3_url = 'https://rlp.telekom.de/wlan/rest/contentapi;jsessionid='
fake_login_url = 'https://rlp.telekom.de/wlan/rest/login;jsessionid=79E904F9475C14DB720C30FC3D74A91F.P3'
final_login_url = 'https://rlp.telekom.de/wlan/rest/login;jsessionid='
JSESSIONID = ''
auth_data = {
        'username': 'fiereclement@gmail.com',
        'password': base64.decodestring(password),
}
input_fields = {}
cookie_jar = cookielib.CookieJar()

def stage2_data(req):
    return '''{"location":{}
"user":{}
"session":{}
"rlpRequest":''' + str(req) + '''
"partnerRegRequest":{}}'''

def get_headers(ref=login_url) :
    return { #https://telekom.portal.fon.com
        "Origin": 'https://telekom.portal.fon.com',
        "Content-Type": "application/json",
       ## "Access-Control-Request-Headers": "content-type",
       # "Access-Control-Request-Method": "POST",
        "Referer": ref
    }

def get_response():
    return os.system("ping -D -c 1 -W 1 " + hostname)

def observe():
    while not get_response():
        time.sleep(5)

    print 'Disconnected !'
    reconnect_stage1()

def opener(url):
    return urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))

def connector(url):
    print('Opening ' + url)
    r = opener(url).open(perdu)
    # print(r.headers)
    return r

def get_wispr_from_content(content):
    return content[content.find(WISPstr) - 5:]

def get_login_url_from_wispr(wispr):
    loginS = '<LoginURL>'
    loginE = '</LoginURL>'
    return wispr[wispr.find(loginS) + len(loginS): wispr.find(loginE)]

def get_login_url_from_content(content):
    return get_login_url_from_wispr(get_wispr_from_content(content))

def reconnect_stage1():
    global login_url, cookie_jar
    # stage 1
    r = connector(perdu)
    login_url = get_login_url_from_content(r.read())
    if login_url:
        print('login url: ' + login_url)
        # reconnect_stage2()
        get_session_id()
        stage2()
        # submit1()
    else:
        print('No login URL, cannot continue')

def last(content, start=0):
    return content.find('<input', start)

def get_prop(prop_name, input_field):
    lbl_name = prop_name + '="'
    start = input_field.find(lbl_name)
    if start > 0:
        start += len(lbl_name)
        return input_field[start: input_field.find('"', start)]
    return ''

def get_name(input_field):
    return get_prop('name', input_field)

def get_value(input_field):
    return get_prop('value', input_field).replace('\n', '')

def stage2():
    global input_fields
    rq = submit_generic(stage_2_url, requests.get, get_headers(login_url))
    # print(rq.content)
    body = rq.content
    last_i = last(body)
    while last_i > 0:
        the_field = body[last_i : body.find('/>', last_i)]
        if 'type="hidden"' in the_field:
            # print(input_field)
            name = get_name(the_field)
            value = get_value(the_field)
            # print(name, value)
            input_fields.update({name: value})
        last_i = last(body, last_i+1)

    new_data = stage2_data(input_fields)
    print('new_dat : ' + str(new_data))
    stage3(new_data)

def stage3(data_arg):
    rq = submit_generic(stage_3_url + JSESSIONID, method=requests.post, headers=get_headers(login_url), data=data_arg)
    print(rq.headers)
    print(rq.content)
    submit2()


'''
def reconnect_stage2():
    global cookie_jar
    # stage 1
    r = connector(login_url)

    content = r.read()
    # print(content)
    submit1()
'''

def submit_generic(url, method, headers=dict(), data=''):
    global cookie_jar

    print('Submitting (' + str(method) + ') ' + url)
    # rq = requests.get(final_login_url, data=data, cookies=cookie)
    if headers:
        print('with: ' + str(headers))
    if cookie_jar:
        print('Send-Cookies :' + str(cookie_jar))
    print('data: ' + str(data))
    new_cookies = copy.copy(cookie_jar)
    res = method(url, data=data, cookies=new_cookies, headers=headers)
    for each in new_cookies:
        cookie_jar.set_cookie(each)
    return res

def get_session_id():
    global JSESSIONID, cookie_jar
    rq = submit_generic(fake_login_url, requests.get)

    print(rq)
    JSESSIONID = rq.cookies.get('JSESSIONID')
    print('JSESSIONID: ' + JSESSIONID)
    '''
    for each in rq.cookies:
        cookie_jar.set_cookie(each)
    '''

def submit2():
    global cookie_jar
    # rq = submit_new(final_login_url + JSESSIONID)
    rq = submit_generic(final_login_url + JSESSIONID, method=requests.post, headers=get_headers(login_url), data=auth_data)

    print(rq)
    print(rq.headers)
    print(rq.text)

if __name__ == '__main__':
    print 'hello'
    import socket

    # make sure we have DNS
    addr1 = socket.gethostbyname('1and1.com')
    print(addr1)

    reconnect_stage1()

    # observe()

