from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import json
from datetime import datetime
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
import openpyxl
import re
import pandas as pd 

driver = webdriver.Chrome('C:/Users/concat/Desktop/LinaCrawling/CONCAT/chromedriver_win32/chromedriver.exe')
wait = WebDriverWait(driver,20)


def main() : 
    # 나이, 성별 설정 
    # 함수를 이용해서 각 정보를 받아옴
    
    global driver
    global wait

    url = 'https://www.directdb.co.kr/product/ltm/custInfoLtm.do?searchPdcCd=30581&searchPdcTrtHistCd=00&pdcDvcd=l_tooth' 
    driver.get(url)
    
    now_year = datetime.now().year
    
    years = ['07','15','20']
    
    contents_kids = list()
    
    # 자녀 입력 
    # 2세 ~ 18세 
    kid_young = int(str((now_year - 2))  + '1231')
    kid_old   = int(str((now_year - 18)) + '1231')
    
    for age in range(kid_old, kid_young, 50000) : 
        
        for sxCd in range(2) : 
            
            driver.get(url)
            
            inputChild(age,sxCd)
            
            for index,year in enumerate(years) :
                
                driver.find_element_by_class_name('year0' + str(index+1)).click()
                wait.until(EC.invisibility_of_element((By.CLASS_NAME,'loading')))
                wait.until(EC.invisibility_of_element((By.CLASS_NAME,'loadmask')))
                
                contents_kids += getContent(year,0,age,sxCd)
    
    
    # 성인 입력 
    # 19세 ~ 70세
    adult_young = int(str(now_year - 19) + '1231')
    adult_old   = int(str(now_year - 70) + '1231')
    
    contents_adult = list()
    
    for age in range(adult_old,adult_young,50000) : 
        
        for sxCd in range(2) : 
            
            driver.get(url)
            
            inputAdult(age,sxCd)
            
            for index,year in enumerate(years) :
                
                # 보장은 80세까지
                # 70세의 고객은 15년형, 20년형 상품을 가입할 수 없음.
                if age - (int(year)*10000) > 19381231 : 
                    driver.find_element_by_class_name('year0' + str(index+1)).click()
                    wait.until(EC.invisibility_of_element((By.CLASS_NAME,'loading')))
                    wait.until(EC.invisibility_of_element((By.CLASS_NAME,'loadmask')))

                    contents_adult += getContent(year,1,age,sxCd)
    
    # 가장 긴 항목을 이용해 dataframe의 column 구성
    kid_len = 0
    kid_max = dict()

    for kid in contents_kids : 
        if kid_len < len(kid) : 
            kid_len = len(kid)
            kid_max = kid

    adult_len = 0
    adult_max = dict()

    for adult in contents_adults : 
        if adult_len < len(adult) : 
            adult_len = len(adult)
            adult_max = adult

    kid_df   = pd.DataFrame(contents_kids, columns = kid_max.keys())
    adult_df = pd.DataFrame(contents_adults, columns = adult_max.keys())

    kid_df.to_excel('DB_Direct_kid.xlsx')
    adult_df.to_excel('DB_Direct_adult.xlsx')


# 자녀형 고객 정보 입력 함수
def inputChild(age, sxCd) : 
    
    global driver
    global wait
    
    driver.find_element_by_class_name("li01").click()
    
    driver.find_element_by_id('birthday').clear()
    driver.find_element_by_id('birthday').send_keys(age)
    
    sexes = driver.find_element_by_class_name('ico_sex').find_elements_by_class_name('input_radio')
    
    sexes[sxCd-1].find_element_by_tag_name('span').click()
    
    jobkids = driver.find_element_by_class_name('label_horizental').find_elements_by_tag_name('li')
    jobkids[0].find_element_by_tag_name('span').click()

    driver.find_element_by_class_name('btn_foot').click()
    wait.until(EC.invisibility_of_element((By.CLASS_NAME,'loading')))



# 성인형 고객 정보 입력 함수

def inputAdult(age, sxCd) : 
    
    global driver
    global wait
    
    driver.find_element_by_class_name("li02").click()
    
    driver.find_element_by_id('birthday').clear()
    driver.find_element_by_id('birthday').send_keys(age)
    
    sexes = driver.find_element_by_class_name('ico_sex').find_elements_by_class_name('input_radio')
    sexes[sxCd-1].find_element_by_tag_name('span').click()
    
    driver.find_element_by_class_name('btn_foot').click()
    wait.until(EC.invisibility_of_element((By.CLASS_NAME,'loading')))


# request를 통해 보장 내역 및 보험료 크롤링

def getContent(year,typecode,age,sxCd) :
    
   
    global driver
    
    CMKSESSIONID= driver.get_cookie('CMKSESSIONID')['value']
    
    _csrf = driver.find_element_by_name('_csrf').get_attribute('value')
    
    page = driver.page_source
    
    soup = BeautifulSoup(page,'html.parser')
    
    # cvrList 얻기 (보장 내역 코드 리스트)
    cvrlist = soup.find(class_ = 'plan_select').find(class_ = 'plan_name').find_all('dd')
    
    cvr_ = str()
    
    for cvr_e in cvrlist : 
        cvr_t = cvr_e.find(class_='ico_pop').get('name')
        cvr_t = cvr_t.replace('cvrPop_','')
        
        if cvr_ != "" :
            cvr_ += "%2C"
        
        cvr_ += cvr_t
    
    # SlPanCd 값에 따라 유형이 바뀐다. 
    SlPanCd = int(soup.find(id = "searchSlPanCd").get('value'))
    
    # 실속 , 기본, 고급 
    plan_slpanCd = [10,0,-10]
    
    contents = list()
    
    # 유형에 따라 반복
    for sl in plan_slpanCd : 
        
        planCd = SlPanCd + sl
        print(planCd)
        
        
        calc_data = ("searchPdcCd=30581&searchSlPanCd=" + str(planCd) + "&searchPymMtdCd=01" +
            "&searchCvrCds=" + cvr_ + "&searchCalcType=default&pdcDvcd=l_tooth" +
            "&arcTrmCd=Y0"+year+"&pymTrmCd=Y0"+year+"&pymMtdCd=01&_csrf=" + _csrf)
    
        calc_header = {
            'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With' : 'XMLHttpRequest',
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            'Referer' : 'https://www.directdb.co.kr/product/ltmSimple/getLtmPlan.do'
        }
        
        calc_cookie = {
             'CMKSESSIONID' : CMKSESSIONID
        }
        
        url = 'https://www.directdb.co.kr/product/ltm/ajaxLtmCalc.do'
        
        response = requests.post(url, headers = calc_header, cookies = calc_cookie, data = calc_data)
        
        # 읽어온 데이터를 json으로 파싱
        data = json.loads(response.text)
        
        # 내가 입력한 year과 읽어온 데이터의 year이 다르면 경고문 출력
        if ('Y0' + year) != data['arcTrmCd'] : 
            print('waring! \n year : ',year , '\n data["arcTrmCd"] : ', data['arcTrmCd'] )
        
        
        plan = data['cvrList']
        
        content = dict()

        content['생년월일'] = age
        content['성별'] = '남자' if sxCd == 1 else '여자'
        content['보험기간'] = year

        content['유형'] = data['pdcPanNm']

        for element in plan : 

            name = element['cvrNm']
            inam = element['cvrInam']
            eta = element['etaCn']
            prm = element['cvrPrm']

            if name != None :
                content[name]  = inam

            if eta != None : 
                eta_prices = re.findall(r':([0-9]+)',eta)
                eta_names  = re.findall(r'-([^0-9]+):',eta)

                for i in range(len(eta_names)) : 
                    content[eta_names[i].strip()] = eta_prices[i]
        
        content['보험료'] = data['fstiPrm']

        contents.append(content)
    
    
    return contents


if __name__ == "__main__" : 
    main()