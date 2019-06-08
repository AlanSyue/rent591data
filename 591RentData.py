from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import csv
import requests

# input 物件網址 撈取網頁資料 return 欄位 
def getData(url):
    
    request_url='https:'+str(url).strip()
    res=requests.get(request_url)
    
    if res.status_code == 200:
        bs=BeautifulSoup(res.text,'html.parser')
        #先宣告變數為NULL 若無撈到資料則寫入NULL
        addr='NULL'
        price='NULL'
        size='NULL'
        floor='NULL'
        room_type='NULL'
        form='NULL'
        car='NULL'

        # 利用 beautfiulsoup 的 find function 利用 css selector 定位 並撈出指定資料
        addr=bs.find('span',{'class':'addr'}).text
        price=bs.find('div',{'class':'price'}).text.strip().split(' ')[0]
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
            if description.text.split('：')[0]=='車 位':
                car=description.text.split('：')[1]
                
        return addr,price,size,floor,room_type,form,car
    else:
        print('link expired:', url)
        return 404, 404, 404, 404, 404, 404, 404
    
def main(outputfile):
    #利用chrome模擬器開啟
    browser = webdriver.Chrome()
    browser.get("https://rent.591.com.tw/?kind=0&region=1")
    #關閉選取地區pop-up 否則無法點選下一頁
    browser.find_element_by_id('area-box-close').click()
    time.sleep(3)
    #輸入 ESC 關閉google 提示，否則無法點選
    browser.find_element_by_class_name('pageNext').send_keys(Keys.ESCAPE) #ECS鍵

    with open(outputfile, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        bs = BeautifulSoup(browser.page_source, 'html.parser')
        totalpages = int(bs.find('span', {'class':'TotalRecord'}).text.split(' ')[-2])/30 + 1
        print('Total pages: ', totalpages)

        for i in range(totalpages):
            room_url_list=[] #存放網址list
            bs = BeautifulSoup(browser.page_source, 'html.parser')
            titles=bs.findAll('h3') # h3 放置物件的區塊
            for title in titles:
                room_url=title.find('a').get('href') # 每個物件的 url
                room_url_list.append(room_url)
            time.sleep(3)

            # ------------- write into csv ------------- #
            for url in room_url_list:
                addr,price,size,floor,room_type,form,car = getData(url)
                writer.writerow([addr,price,size,floor,room_type,form,car])
            # ------------------------------------------ #
            print(i/totalpages*100, '%',end='\r') # print out 完成 %數

            #若偵測到無法點選最後一頁則跳出
            if bs.find('a',{'class':'last'}):
                pass
            else:
                #撈取完資料後點選下一頁，並等待 3 秒載入新頁面
                browser.find_element_by_class_name('pageNext').send_keys(Keys.ESCAPE)
                browser.find_element_by_class_name('pageNext').click()
                time.sleep(3)
                
if __name__ == '__main__':
    # -------- configurable parameter -------- #
    output_file_name = 'tpe_rent_output.csv'
    # ---------------------------------------- #
    main(output_file_name)
    print('\nfinish!')
