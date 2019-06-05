#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  7 14:35:07 2019
@author: Ivan
https://gist.github.com/rifleak74
作者：
楊超霆（臺灣行銷研究有限公司 資料科學研發工程師）
https://medium.com/pythonstock/%E8%82%A1%E7%A5%A8%E5%B0%8F%E7%A7%98%E6%9B%B8%E5%B9%AB%E4%BD%A0%E6%8E%8C%E6%8F%A1-%E5%85%AC%E5%8F%B8%E9%87%8D%E5%A4%A7%E8%A8%8A%E6%81%AF-%E7%AC%AC%E4%B8%80%E6%99%82%E9%96%93%E5%B0%B1%E5%85%88%E8%B7%91-%E9%99%84python%E7%A8%8B%E5%BC%8F%E7%A2%BC-ef9a4c63a2e2
"""

import requests
import datetime
import pandas as pd
from io import StringIO
from bs4 import BeautifulSoup
import json
###############################################################################
#                                 整合性選股範例                                #
#                                                                             #
#                         同時結合基本面、技術面、籌碼面                           #
###############################################################################

#你想要查詢的股票
yourstock = input('請輸入您想要查詢的股票代號：')


today=datetime.datetime.now()
lastmonth = today - datetime.timedelta(days=31) #一個月前的時間
#------------------------------先顯示目前價格----------------------------------
# 要抓取的網址
url = 'https://tw.stock.yahoo.com/q/q?s=' + yourstock 
#請求網站
list_req = requests.get(url)
#將整個網站的程式碼爬下來
soup = BeautifulSoup(list_req.content, "html.parser")
#找到b這個標籤
get_stock_price= soup.findAll('b')[1].text #裡面所有文字內容
print('該股票目前價格是：'+ get_stock_price)


#--------------------------------籌碼面選股------------------------------------
'''
查看外資有無連續買進
設定時間為6天
但會有假日，因此不會有完整六天
'''

sumstock=[]
for i in range(6,0,-1):
    date = datetime.datetime.strftime(datetime.datetime.now() - datetime.timedelta(days=i),'%Y%m%d') 
    r = requests.get('http://www.tse.com.tw/fund/T86?response=csv&date='+date+'&selectType=ALLBUT0999') 
    if r.text != '\r\n': #有可能會沒有爬到東西，有可能是六日
        get = pd.read_csv(StringIO(r.text), header=1).dropna(how='all', axis=1).dropna(how='any') 
        get=get[get['證券代號']==yourstock] # 找到我們要搜尋的股票
        if len(get) >0:
            get['三大法人買賣超股數'] = get['三大法人買賣超股數'].str.replace(',','').astype(float) 
            if get['三大法人買賣超股數'].values[0] >0:
                sumstock.append('買')
            else:
                sumstock.append('賣')
                
print('外資買賣狀況（遠～近期）:'+' '.join(sumstock))


#--------------------------------技術面選股------------------------------------
'''
查看是否有高過20日平均線
'''

avgprice=[]
url = 'http://www.twse.com.tw/exchangeReport/STOCK_DAY_AVG?response=json&date=' + today.strftime("%Y%m%d") + '&stockNo=' + yourstock
list_req = requests.get(url) #請求網站
soup = BeautifulSoup(list_req.content, "html.parser") #將整個網站的程式碼爬下來
jsonsoup=json.loads(str(soup))
for i in range(len(jsonsoup['data'])-1):
    avgprice.append(float(jsonsoup['data'][i][1]))

#如果不夠20日，就爬上個月的價格    
if len(avgprice) < 19:
    url = 'http://www.twse.com.tw/exchangeReport/STOCK_DAY_AVG?response=json&date=' + lastmonth.strftime("%Y%m%d") + '&stockNo=' + yourstock
    list_req = requests.get(url) #請求網站
    soup = BeautifulSoup(list_req.content, "html.parser") #將整個網站的程式碼爬下來
    jsonsoup=json.loads(str(soup))
    for i in range(len(jsonsoup['data'])-1,1,-1):
        avgprice.append(float(jsonsoup['data'][i][1]))        

#計算出平均並且進行判斷
avg=sum(avgprice[:20])/20
if avg < float(get_stock_price):
    print('該股價高於20日平均')
elif avg == float(get_stock_price):
    print('該股價正在20日平均上')
else:
    print('該股價在20日平均之下')
    

#--------------------------------基本面選股------------------------------------
data = {
        'encodeURIComponent':'1',
        'step':'1',
        'firstin':'1',
        'off':'1',
        'keyword4':'',
        'code1':'',
        'TYPEK2':'',
        'checkbtn':'',
        'queryName':'co_id',
        'inpuType':'co_id',
        'TYPEK':'all',
        'co_id':yourstock
                }

headers = {
        'Host': 'mops.twse.com.tw',
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'         
        }

url = 'http://mops.twse.com.tw/mops/web/t146sb05'
list_req = requests.post(url, data=data ,headers=headers)
soup = BeautifulSoup(list_req.content, "html.parser")
gettable=soup.findAll('table')[5].findAll('table')[8]
gettr = gettable.findAll('tr',{'class':'text_center'})
print('「營收」去年整年度與今年比較：'+ gettr[0].findAll('td')[2].text)