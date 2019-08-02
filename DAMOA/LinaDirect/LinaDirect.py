from selenium import webdriver
from bs4 import BeautifulSoup as bs
import pandas as pd 
from datetime import datetime
import time
import openpyxl
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 


driver = webdriver.Chrome('C:/Users/concat/Desktop/LinaCrawling/CONCAT/chromedriver_win32/chromedriver.exe')
url = 'https://direct.lina.co.kr/product/dtc001'
driver.get(url)

age_range = driver.find_element_by_css_selector('#tabcont_0101 > div > div.inner.newToothTab > div:nth-child(6) > table > tbody > tr:nth-child(2) > td:nth-child(2)').text
young = int(age_range[:2])
old   = int(age_range[3:5])

year = datetime.now().year

# 가장 어린 나이는 1월 ~ 12월 가능
# 가장 늙은 나이는 1월에서 현재 날짜 이후만 가능 ( ex. 7월 25일이라면 690126 이후만 가입 가능)
# 그러므로 생년 월일은 임의로 0725로 정하고 진행

young = int(str(year - young)[2:] + '0725') 
old   = int(str(year - old)[2:] + '0725')

df_index = 0

wait = WebDriverWait(driver,20)

first = True

for age in range(old,young,50000) : 
    
    for i in range(0,2) : 
        man = driver.find_element_by_id('main_btn_male')
        woman = driver.find_element_by_id('main_btn_female')

        if i == 0 :
            woman.click()
            time.sleep(2)
            sex = '여자'
        else : 
            man.click()
            time.sleep(2)
            sex = '남자'

        driver.find_element_by_class_name('g_input_01').clear()
            
        time.sleep(1)

        driver.find_element_by_class_name('g_input_01').send_keys(age)
        time.sleep(0.1)
        driver.find_element_by_class_name('btn_premium_sum').click()
        time.sleep(1)

        wait.until(EC.invisibility_of_element((By.CLASS_NAME,'l_loading')))
        #time.sleep(5)

        page = driver.page_source
        soup = bs(page,'html.parser')
        
        basic  = soup.find(class_='basicTbody')
        detail = soup.find(class_='detailTbody')

        premium = basic.find_all(class_='inNum')

        tr_list = detail.find_all('tr')

        details_ = list()

        for tr in tr_list : 
            test = tr.find(class_='inTbl')
            if test != None : 
                continue
            title = tr.find('th').get_text()
            prices = list()
            
            td = tr.find_all('td')
            for price in td :
                prices.append(price.get_text())
            
            if prices[0] == '\xa0' and prices[1] == '\xa0' : 
                continue
            
            contents = {
                'title' : title,
                'basic' : prices[0],
                'concen': prices[1]
            }
            
            details_.append(contents)

        if first == True :
            column_list = ['생년월일','성별','종류']

            for de in details_ : 
                column_list.append(de['title'])
            
            column_list.append('보험료')

            df = pd.DataFrame(columns = column_list)
            first = False

        basic_list = [age,sex,'기본보장']
        concen_list = [age,sex,'집중보장']

        for de in details_ : 
            basic_list.append(de['basic'])
            concen_list.append(de['concen'])

        basic_list.append(premium[0].get_text())
        concen_list.append(premium[1].get_text())

        df.loc[df_index] = basic_list
        df.loc[df_index+1] = concen_list

        df_index += 2

writer = pd.ExcelWriter('LinaDirect.xlsx')
df.to_excel(writer,'Sheet1')
writer.save()
