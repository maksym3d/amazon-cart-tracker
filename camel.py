# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib2, cookielib
import sys
reload(sys)
sys.setdefaultencoding('UTF8')
ccj = cookielib.CookieJar()

def get_camel_info(asin, headers=None):
    url = 'http://camelcamelcamel.com/product/%s' % asin
    chart_url = 'http://charts.camelcamelcamel.com/us/%s/amazon.png?force=1&zero=0&w=1024&h=640&desired=false&legend=1&ilt=1&tp=all&fo=0&lang=en' % asin
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(ccj))
    
    if headers != None: opener.addheaders = headers
    try:
        content = opener.open(url).read()
    except Exception as e:
        return None
    # f = open('html/%s.html' % asin, 'w')
    # f.write(content)
    # f.close()
    
    soup = BeautifulSoup(content, "lxml")
    seller_types = [
        {
            'header': 'Amazon Price History'
        },
        {
            'header': '3rd Party New Price History'
        },
        {
            'header': '3rd Party Used Price History'
        }           
    ]        
    data = {
        'prices': {
             'current': {
            },
            'lowest': {
            },
            'highest': {
            
            },
            'average': {
            }
        },
        'url': url,
        'chart_url': chart_url
       
    }
    for seller_type in seller_types:
        header = soup.find('h3', string = seller_type['header'])
        if header == None:
            continue
        type_div = header.parent
        for price_type in data['prices']:
            price_div = type_div.find((lambda tag: tag.name == "td" and price_type.capitalize() in tag.text))
            # print price_div
            try:
                price = price_div.find_next_sibling('td').text.replace('$', '')
                price = float(price)
                date = price_div.find_next_sibling('td').find_next_sibling('td').text
    
            except Exception as e:
                price = None
                date = None
           
            data['prices'][price_type][seller_type['header']] = {
                'price': price,
                'date': date
            }
    #sleep(3)
    return data

# print get_camel_info('B005ADY8V4')