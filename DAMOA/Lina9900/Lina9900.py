from selenium import webdriver
import pandas as pd
import numpy as np
import re
import openpyxl
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import time


driver = webdriver.Chrome("C:\\Users\\dngus\\dev\\2019Summer\\CONCAT\\LinaCrwaling\\chromdriver_win32\\chromedriver.exe")
url = 'https://direct.lina.co.kr/product/dtc005?utm_source=lina.co.kr&utm_medium=referral&utm_campaign=conversion&utm_content=menu_dental'

driver.get(url)

# DataFrame 만들기
Lina9900_df = pd.DataFrame(columns = ['생년월일', '성별', '구분', '치료 소재', '보장 금액'])

# 가입 나이 찾기
driver.find_element_by_link_text('가입 시 꼭 알아두세요').click()

join_age = driver.find_element_by_css_selector('#tabcont_0103 > div > ul:nth-child(9) > li:nth-child(2) > table > tbody > tr > td:nth-child(4)')

join_regex = re.compile(r'[0-9]+')
age_range  = join_regex.findall(join_age.text)

young_age = 2019 - int(age_range[0]) # 1999
old_age   = 2019 - int(age_range[1]) # 1980

loc_number = 0

wait = WebDriverWait(driver,10)

# 나이 입력하기
for age in range(old_age,young_age,5) :
    # 5살 단위로 검색합니다.
    age = str(age)[2:4] + '0703'

    driver.find_element_by_id('birthday').clear()
    driver.find_element_by_id('birthday').send_keys(age)

    # 성별 입력하기
    for sex_i in range(0,2) :
        sextable = driver.find_element_by_class_name('g_btn_sel_n')

        btn_man   = sextable.find_element_by_link_text('남')
        btn_woman = sextable.find_element_by_link_text('여')

        if sex_i == 0 :
            sex = '남'
            btn_man.click()
        else :
            sex = '여'
            btn_woman.click()

        time.sleep(0.1)

        driver.find_element_by_id('btnD01').click()
        wait.until(EC.invisibility_of_element((By.ID,'divProgress')))
        time.sleep(10)



        # '구분' 테이블
        table  = driver.find_element_by_class_name('vtb_itemInfo')
        thlist = table.find_element_by_tag_name('tbody').find_elements_by_tag_name('th')

        categorylist = list()

        for th in thlist:
            th = th.text
            categorylist.append(th.replace('\n',' '))

        # '구분' 테이블 2
        sublist = list()
        for sub in thlist:
            sublist.append(sub.find_element_by_tag_name('span'))

        categorylist2 = list()
        for i in range(0,len(sublist)) :
            cate2 = thlist[i].text.replace(sublist[i].text, '')
            cate2 = cate2.replace('\n','')
            categorylist2.append(cate2)

        # 치료 소재, 보장 금액 크롤링
        tdlist = table.find_element_by_tag_name('tbody').find_elements_by_tag_name('td')

        material  = list()
        guarantee = list()

        for i in range(0,len(tdlist)) :
            if i%3 == 0:
                material.append(tdlist[i].text)
            elif i%3 == 2:
                guarantee.append(tdlist[i].text)

        for j in range(0,4):
            c_num = 0

            if j == 3:
                c_num = 1

            Lina9900_df.loc[loc_number] = [age,sex,categorylist2[c_num],material[j],guarantee[j]]
            loc_number += 1



writer = pd.ExcelWriter('Lina9900.xlsx')
Lina9900_df.to_excel(writer,'Sheet1')
writer.save()
