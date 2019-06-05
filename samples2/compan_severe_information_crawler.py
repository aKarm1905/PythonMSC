import requests
import pandas as pd
from bs4 import BeautifulSoup

"""
@author: cheating
https://gist.github.com/rifleak74
作者：
楊超霆（臺灣行銷研究有限公司 資料科學研發工程師）
https://medium.com/pythonstock/%E8%82%A1%E7%A5%A8%E5%B0%8F%E7%A7%98%E6%9B%B8%E5%B9%AB%E4%BD%A0%E6%8E%8C%E6%8F%A1-%E5%85%AC%E5%8F%B8%E9%87%8D%E5%A4%A7%E8%A8%8A%E6%81%AF-%E7%AC%AC%E4%B8%80%E6%99%82%E9%96%93%E5%B0%B1%E5%85%88%E8%B7%91-%E9%99%84python%E7%A8%8B%E5%BC%8F%E7%A2%BC-ef9a4c63a2e2
"""

 # 要抓取的網址
url = 'http://mops.twse.com.tw/mops/web/ajax_t05st01'

my_headers = {'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36', 
              'Referer': 'http://mops.twse.com.tw/mops/web/t05st01',# 必要 
              'Cookie': 'jcsession=jHttpSession@5bd6be0c; _ga=GA1.3.32395516.1542113354; _gid=GA1.3.1756921164.1542336195; newmops2=co_id%3D2002%7Cyear%3D107%7Cmonth%3D%7Cb_date%3D%7Ce_date%3D%7C'# 必要 
} 


data  = {
            'encodeURIComponent': '1',
            'step': '1',
            'firstin': '1',
            'off': '1',
            'TYPEK': 'all',
            'co_id': '2002',
            'year': '107'
        }

r_post  =  requests.post(url, data = data, headers  =  my_headers, timeout  =  5).text
soup  =  BeautifulSoup(r_post, 'html.parser')
gettable = soup.find('table', {'class':'hasBorder'})
gettitle = soup.find_all('pre')
