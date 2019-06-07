from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import csv

# 獲取物件網址,output 網址 type=list
def getUrl():
    #存放網址list
    room_url_list=[]
    #利用chrome模擬器開啟
    browser = webdriver.Chrome()
    browser.get("https://rent.591.com.tw/?kind=0&region=1")
    #關閉選取地區pop-up 否則無法點選下一頁
    browser.find_element_by_id('area-box-close').click()
    time.sleep(5)
    #輸入 ESC 關閉google 提示，否則無法點選
    browser.find_element_by_class_name('pageNext').send_keys(Keys.ESCAPE)
    # range 為執行次數，可以看有幾頁就輸入多少，開始在每頁的H3撈出網址
    for i in range(351):
        bs = BeautifulSoup(browser.page_source, 'html.parser')
        titles=bs.findAll('h3')
        for title in titles:
            room_url=title.find('a').get('href')
            room_url_list.append(room_url)
        time.sleep(5)
        #若偵測到無法點選最後一頁則跳出
        if bs.find('a',{'class':'last'}):
            pass
        else:
            #撈取完資料後點選下一頁，並等待5秒載入新頁面
            browser.find_element_by_class_name('pageNext').send_keys(Keys.ESCAPE)
            browser.find_element_by_class_name('pageNext').click()
            time.sleep(5)
    return room_url_list
# input 網址 list 撈取網頁資料 ouput :output.csv 檔案
def getData(url_list):
    #創建 output.csv 檔案
    with open('output.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for url in url_list:
            request_url='https:'+str(url).strip()
            res=requests.get(request_url)
            bs=BeautifulSoup(res.text,"html5lib")
            #先宣告變數為NULL 若無撈到資料則寫入NULL
            addr='NULL'
            price='NULL'
            size='NULL'
            floor='NULL'
            room_type='NULL'
            form='NULL'
            # 利用 beautfiulsoup 的 find function 利用 css selector 定位 並撈出指定資料
            addr=bs.find('span',{'class':'addr'}).text
            price=bs.find('div',{'class':'price'}).text.strip().split(' ')[0]
            price_perDay=bs.find('div',{'class':'price'}).text.strip().split(' ')[1]
            room_attrs=bs.find('ul',{'class':'attr'}).findAll('li')
            for attr in room_attrs:
                if attr.text.split('\xa0:\xa0\xa0')[0]=='坪數':
                    size=attr.text.split('\xa0:\xa0\xa0')[1]
                elif attr.text.split('\xa0:\xa0\xa0')[0]=='樓層':
                    floor=attr.text.split('\xa0:\xa0\xa0')[1]
                elif attr.text.split('\xa0:\xa0\xa0')[0]=='型態':
                    room_type=attr.text.split('\xa0:\xa0\xa0')[1]
            room_descriptions=bs.find('ul',{'class':'labelList-1'}).findAll('li')
            for description in room_descriptions:
                if description.text.split('：')[0]=='格局':
                    form=description.text.split('：')[1]
            # 將需要資料撈出寫入 csv 檔案
            writer.writerow([addr,price,price_perDay,size,floor,room_type,form])

if __name__ == '__main__':
    urls = getUrl()
    getData(urls)
    print('finish')