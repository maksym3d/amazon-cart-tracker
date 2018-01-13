#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib, urllib2, cookielib
import json
import sys
from bs4 import BeautifulSoup
from cmath import asin
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from camel import get_camel_info
import smtplib
import os
from code import coder2

reload(sys)
sys.setdefaultencoding('UTF8')

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
forms_method = "POST"

headers = [
    ('User-agent', user_agent)
]

def send_email(email_info, message):
    try:
        s = smtplib.SMTP_SSL("%s:%d" % (email_info['smtp_url'], email_info['smtp_port']))
        s.login(email_info['user'], email_info['password'])
    except smtplib.SMTPAuthenticationError:
        print('Failed to login')
    else:
        print('Logged in! Composing message..')
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Price Alert'
        msg['From'] = email_info['user']
        msg['To'] = email_info['user']
        part = MIMEText(message, 'plain')
        msg.attach(part)
        s.sendmail(email_info['user'], email_info['user'], msg.as_string())
        print('Message has been sent.')

def send_report(email_info, items):
    message = ''
    for item in items:
        price_diff = item['history'][-1]['price'] - item['history'][-2]['price']
        title = item['title']
        asin = item['asin']
        link = item['link']
        price = item['history'][-1]['price']
        message += '%.2f (%.2f) %s %s\n' % (price_diff, price, asin, title)
        message += '%s\n' % link
        if 'camel_info' in item and item['camel_info'] != None:
            message += '%s\n%s\n' % (item['camel_info']['url'], item['camel_info']['chart_url'])
            if 'Amazon Price History' in item['camel_info']['prices']['lowest']:
                try:
                    message += '    CCC Min: %.2f (%s)\n' %  (item['camel_info']['prices']['lowest']['Amazon Price History']['price'], item['camel_info']['prices']['lowest']['Amazon Price History']['date'])
                    message += '    CCC Max: %.2f (%s)\n' %  (item['camel_info']['prices']['highest']['Amazon Price History']['price'], item['camel_info']['prices']['lowest']['Amazon Price History']['date'])
                    message += '    CCC Avg: %.2f (%s)\n' %  (item['camel_info']['prices']['average']['Amazon Price History']['price'], item['camel_info']['prices']['lowest']['Amazon Price History']['date'])
                except Exception as e:
                    print asin
                    print item
                    print e
        message += '\n\n'
    
    send_email(email_info, message)

def get_config(config):
    with open(config, 'r') as f:
        return json.loads(f.read())
    
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime.datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError ("Type not serializable")

def json_hook(obj):
    newDic = {}

    for key in obj:
        try:
            if float(key) == int(float(key)):
                newKey = int(key)
            else:
                newKey = float(key)
            newDic[newKey] = obj[key]
            continue
        except ValueError:
            pass
        try:
            newDic[str(key)] = datetime.datetime.strptime(obj[key])
            continue
        except TypeError:
            pass

        newDic[str(key)] = obj[key]
    return newDic

def save_cookies_lwp(cookiejar, filename):
    lwp_cookiejar = cookielib.LWPCookieJar()
    for c in cookiejar:
        args = dict(vars(c).items())
        args['rest'] = args['_rest']
        del args['_rest']
        c = cookielib.Cookie(**args)
        lwp_cookiejar.set_cookie(c)
    lwp_cookiejar.save(filename, ignore_discard=True)

def load_cookies_from_lwp(filename):
    lwp_cookiejar = cookielib.LWPCookieJar()
    lwp_cookiejar.load(filename, ignore_discard=True)
    return lwp_cookiejar

def write_str_to_file(file_name, content):
    f = open(file_name, 'w')
    f.write(content)
    f.close()
    
def init_from_login(config):
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = headers
    _ = opener.open(config['url']['logout'])
    resp = opener.open(config['url']['base'])
    soup = BeautifulSoup(resp, "lxml")
    login_url = config['url']['base'] + '/' + soup.find('span', string='Sign in').find_previous('a')['href']
    resp = opener.open(login_url)
    soup = BeautifulSoup(resp, "lxml")
    sign_in_form = soup.find('form', attrs={'name': 'signIn'})
    sign_in_url = sign_in_form['action']
    
    login_params = {}
    login_field_name = 'email'
    passw_field_name = 'password'
    for inp in sign_in_form.find_all('input'):
        try:
            if 'id' in inp and inp['id'] == 'ap_email':
                login_field_name = inp['name']
            elif  'id' in inp and inp['id'] == 'ap_password':
                passw_field_name = inp['name']
            elif inp['type'] == 'hidden':
                login_params[inp['name']] = inp['value']
        except:
            pass
    login_params[login_field_name] = config['user']
    login_params[passw_field_name] = config['password']
    sign_in_data = urllib.urlencode(login_params).encode('ascii')
    sign_in_headers = [
        ('Host', 'www.amazon.com'),
        ('Connection', 'keep-alive'),
        ('Content-Length', '%d' % len(sign_in_data)),
        ('Cache-Control', 'max-age=0'),
        ('Origin', 'https://www.amazon.com'),
        ('Upgrade-Insecure-Requests', '1'),
        ('User-Agent', user_agent),
        ('Content-Type', 'application/x-www-form-urlencoded'),
        ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
        ('Referer', login_url),
        ('Accept-Encoding', 'gzip, deflate, br'),
        ('Accept-Language', 'en-US,en;q=0.8')
    ]
    
    request = urllib2.Request(sign_in_url, data=sign_in_data)
    request.get_method = lambda: forms_method
    for header in sign_in_headers:
        request.add_header(*header)
        
    for cookie in cj:
        print cookie.name, cookie.value, cookie.domain
    print "------", sign_in_url, sign_in_data
    resp = opener.open(request)
    s = resp.read()
    for cookie in cj:
        print cookie.name, cookie.value, cookie.domain
    
    if config['writeoutfiles']: write_str_to_file(config['outfolderhtml'] + '/' + '0.html', s)
    save_cookies_lwp(cj, config['cookiefile'])
    return opener

def init_from_file(config):
    cj =  cookielib.CookieJar()
    if os.path.exists(config['cookiefile']):
        cj = load_cookies_from_lwp(config['cookiefile'])
        #for cookie in cj:
        #    print cookie
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = headers
    return opener


def parse_cart_subpage(config, html_content):
    items = []
    soup = BeautifulSoup(html_content.encode('UTF-8'), "lxml")
    prod_divs = soup.find_all((lambda tag: tag.name == "div" and tag.has_attr('data-asin')))
    for prod in prod_divs:
        title = prod.find('span', attrs={'class': 'sc-product-title'}).text.strip()
        price_origin = float(prod['data-price'])
        if 'Currently unavailable' in prod.text: continue
        price = float(prod.find("span", attrs={'class':'sc-price-sign' }).text.replace('$', '').replace(',', '').strip())
        asin = prod['data-asin']
        link = prod.find("a", attrs={'class':'sc-product-link' })['href']
        # print asin, title, price
        items.append({
            'asin': asin,
            'price': price,
            'title': title,
            'link': config['url']['base'] + '/' + link,
            'price_original': price_origin
        })
    return [items, soup]

def fetch_data(config):
    opener = init_from_file(config)
    resp = opener.open(config['url']['cart'])
    content = resp.read()
    soup = BeautifulSoup(content, "lxml")
    #encoding=resp.headers['content-type'].split('charset=')[-1]
    #content = unicode(content, encoding)
    if soup.find((lambda tag: tag.name == "h1" and 'Your Shopping Cart is empty' in tag.text)) != None:
        print "need to login"
        opener = init_from_login(config)
        resp = opener.open(config['url']['cart'])
        content = resp.read()
    
    [data_items, soup] = parse_cart_subpage(config, content)
    if config['writeoutfiles']: write_str_to_file(config['outfolderhtml'] + '/' + '1.html', content)
    counter = 1
    has_more = soup.find('div', attrs = {'data-has-more-items': '1'}) != None
    while has_more:
        form_data = {
            'listType': 'saved-for-later',
            'listId': 'saved-for-later',
            'hasPantryBundleAlready': 'false',
            'page': counter
        }
        form_data_encoded = urllib.urlencode(form_data).encode('UTF-8')
        headers = [
            ('Accept', 'application/json, text/javascript, */*; q=0.01'),
            #('Accept-Encoding', 'gzip, deflate, br'),
            ('Accept-Language', 'en-US,en;q=0.8'),
            ('Connection', 'keep-alive'),
            ('Content-Length',  '%s' % len(form_data_encoded)),
            ('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8;'),
            ('Host', 'www.amazon.com'),
            ('Origin', 'https://www.amazon.com'),
            ('Referer', 'https://www.amazon.com/gp/cart/view.html/ref=nav_cart'),
            ('User-Agent', user_agent),
            ('X-AUI-View', 'Desktop'),
            ('X-Requested-With', 'XMLHttpRequest')
        ]
        more_url = config['url']['more'].replace("COUNTER", str(counter))
        
        request = urllib2.Request(more_url, data=form_data_encoded)
        request.get_method = lambda: forms_method
        for header in headers:
            request.add_header(*header)
            
        resp = opener.open(request)
        content = resp.read()
        #encoding=resp.headers['content-type'].split('charset=')[-1]
        #content = unicode(content, encoding)
        data = json.loads(content)
        
        hasMoreItems = data['features']['desktop/saved-cart']['hasMoreItems']
        html = ''
        for item in data['features']['desktop/saved-cart']['items']:
            if 'html' in item:
                html =  html + '\n' + item['html']
        
        if config['writeoutfiles']: write_str_to_file(config['outfolderhtml'] + '/' + 'more%d.html' % counter, html)
        [items, soup] = parse_cart_subpage(config, html)
        data_items.extend(items)
        counter+=1
        if hasMoreItems != '1': has_more = False
    return data_items

def main():
    CONFIG_FILE = 'config.json'
    config = get_config(CONFIG_FILE)
    
    # Decrypt account info if requested
    if config['email']['decode_account_info']:
        key = os.environ[config['email']['environment_key']]
        cfr = coder2(key)
        config['email']['password'] =  cfr.decode(config['email']['password'])
        config['email']['user'] =  cfr.decode(config['email']['user'])
    
    if config['amazon']['decode_account_info']:
        key = os.environ[config['amazon']['environment_key']]
        cfr = coder2(key)
        config['amazon']['password'] =  cfr.decode(config['amazon']['password'])
        config['amazon']['user'] =  cfr.decode(config['amazon']['user'])
    
    # This folder will be used to save all fetched amazon pages
    if config['amazon']['writeoutfiles']:
        os.makedirs(config['amazon']['outfolderhtml'])
    items_to_notify = []
    print "Downloading Amazon cart info"
    items = fetch_data(config['amazon'])
    res = {}
    if os.path.exists(config['datafile']):
        with open(config['datafile'], 'r') as f:
            res = json.load(f, object_hook=json_hook)
    date_now = datetime.datetime.now()
    print "Processing items"
    for item in items:
        asin = item['asin']
        if asin not in res:
            res[asin] = {
                'title': item['title'],
                'asin': item['asin'],
                'link': item['link'],
                'first_price': item['price_original']
            }
        if 'camel_info' not in res[asin] or res[asin]['camel_info'] == None: res[asin]['camel_info'] = get_camel_info(asin, headers)
        record = res[asin]
        record['url'] = config['amazon']['url']['product'] + asin
        if 'history' not in record: record['history'] = []
        item['date'] = date_now
        if len(record['history']) == 0 or abs(record['history'][-1]['price'] - item['price']) > config['mindifference']:
            if len(record['history']) == 0:
                # TODO add new item - check camelcamel etc
                pass
            else:
                print item, item['price'] - record['history'][-1]['price']
                items_to_notify.append(record)
            record['history'].append(item)
    
    print "Found %d cart changes matching the threshold" % len(items_to_notify)
    if len(items_to_notify) > 0:
        send_report(config['email'], items_to_notify)

    # Save price info
    with open(config['datafile'], 'w') as f:
        res = json.dump(res, f, default=json_serial, indent=4, separators=(',', ': '))

if __name__ == '__main__':
    main()