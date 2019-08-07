from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime 
import pandas as pd
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome('C:/Users/dngus/Desktop/CONCAT_INTERN/LinaCrawling/CONCAT/chromedriver_win32/chromedriver.exe')
wait = WebDriverWait(driver,20)

def main() :
    url = 'https://direct.samsungfire.com/ria/pc/product/dental/?state=Front3'

    now_year = datetime.now().year
    
    young = 3 
    old   = 65
    
    contents = list()

    for age in range(young,old,5) : 

        for sxCd in range(2) : 
            
            driver.get(url)
            
            try : 
                wait.until(EC.invisibility_of_element_located((By.CLASS_NAME,'loading-progress')))
                wait.until(EC.invisibility_of_element_located((By.ID,'loading-transparent')))
                wait.until(EC.invisibility_of_element_located((By.CLASS_NAME,'loading-contents')))
            except : 
                driver.get(url)
                wait.until(EC.invisibility_of_element_located((By.CLASS_NAME,'loading-progress')))
                wait.until(EC.invisibility_of_element_located((By.ID,'loading-transparent')))
                wait.until(EC.invisibility_of_element_located((By.CLASS_NAME,'loading-contents')))
            
            client_age = str(now_year - age) + '1231'
            driver.find_element_by_id('birthS-input').clear()
            driver.find_element_by_id('birthS-input').send_keys(client_age)

            # 성별 선택 박스, 0번은 남자 1번은 여자 
            genderList = driver.find_element_by_class_name('btn-group').find_elements_by_class_name('btn')
            genderList[sxCd].click()
            
            selectJob(age)

            # 보험료 계산하기
            driver.find_element_by_class_name('ne-bts-nextprev').find_element_by_id('btn-next-step').click()
            wait.until(EC.invisibility_of_element((By.CLASS_NAME,"loading")))
            
            # 이벤트 팝업창 뜰 때까지 기다리고 
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME,'modal-dialog')))

            dialog = driver.find_elements_by_class_name('modal-dialog')
            
            if len(dialog) > 0 :
                dialog[0].find_element_by_id('btn-confirm').click()
            
            content = getContents(client_age,sxCd)
            contents += content
    
    # dataframe, excel 화 
    kids = list()
    adults = list()

    for element in contents : 
        if '어린이 치아치료보장(보철)' in element : 
            kids.append(element)
        else : 
            adults.append(element)
    
    kid_len = 0
    kid_max = dict()
    adult_len = 0
    adult_max = dict()

    for kid in kids: 
        if len(kid) > kid_len : 
            kid_len = len(kid)
            kid_max = kid 
    
    for adult in adults :
        if len(adult) > adult_len :
            adult_len = len(adult)
            adult_max = adult 
    
    kid_df = pd.DataFrame(kids, columns = kid_max.keys())
    adult_df = pd.DataFrame(adults, columns = adult_max.keys())

    kid_df.to_excel('Samsung_direct_kid.xlsx')
    adult_df.to_excel('Samsung_direct_adult.xlsx')


def selectJob(age) :

    global driver

    # 직업 선택
    driver.find_element_by_id('job-button').click()
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME,'modal-content-slide')))
    
    time.sleep(2)


    search_tabs = driver.find_element_by_class_name('nav-tabs').find_elements_by_tag_name('li')
    search_tabs[0].find_element_by_tag_name('a').click()

    if age < 8 : 
        job = '미취학아동'
    elif age < 14 : 
        job = '초등학생'
    elif age < 17 : 
        job = '중학생'
    elif age < 20 :
        job = '고등학생'
    else : 
        job = '공무원(기술직/특수직제외)'
    
    driver.find_element_by_id('sjob-search-text').send_keys(job)
    time.sleep(0.5)

    search_results = driver.find_element_by_id('sjob-search-result').find_elements_by_tag_name('li')
    search_results[0].click()

    driver.find_element_by_class_name("ne-agree-box").find_element_by_class_name('btn').click()
    driver.find_element_by_class_name('modal-footer').find_element_by_class_name('btn-next-step').click()
    time.sleep(0.5)


# 순수 보장형 선택, 플랜이 몇개 있는지 파악, 보험기간 선택, 보장내역 긁기, 보험료 긁기

def getContents(client_age,sxCd) : 

    global driver
    global wait
    
    plan_type = driver.find_element_by_class_name('bts-select').find_elements_by_name('refundCls')
    
    for types in plan_type : 
        if types.text == "순수보장형" : 
            types.click()
            wait.until(EC.invisibility_of_element((By.CLASS_NAME,"loading")))

    contents = list()

    # 보험기간 변경하기 
    terms = driver.find_element_by_id('insured-term').find_elements_by_tag_name('label')

    for index,term in enumerate(terms) : 
        term.click() 
        wait.until(EC.invisibility_of_element((By.CLASS_NAME,"loading")))

        # 플랜이 몇개 있는지 파악하기 
        plan_names = driver.find_element_by_id('coverage-header').find_elements_by_class_name('btn-radio')
        plan_numbers = len(plan_names)
        
        plan_codes = list()
        for plan in plan_names : 
            plan_codes.append(plan.get_attribute('for').replace('pla',''))
        
        # 보장내역 테이블 긁기 
        basic = {
            '생년월일' : client_age,
            '성별' : '남자' if sxCd == 0 else '여자',
            '보험기간' : term.text,
            '유형' : "미정"
        }
        
        plans = [basic.copy() for i in range(plan_numbers)]
        
        page = driver.page_source 
        soup = BeautifulSoup(page,'html.parser')

        coverage_list = soup.find(class_='content-table').find(id = 'coverage-list').find_all('tr')

        for element in coverage_list : 
    
            check = element.find_all(class_="ne-fb")
            
            # 대분류는 제외 
            if len(check) > 0 : 
                continue
            
            # 플랜 , 더보기 텍스트 제외 
            element.find(class_='ne-hidden').extract()
            element.find(class_='ne-bt-more').extract()
            
            name = element.find(scope ='row').text
            
            prices = element.find_all('td')
            
            for index,price in enumerate(prices) : 
                price.find(class_='ne-hidden').extract()
                plans[index][name] = price.text.replace('지급','')
        
        # 보험료 긁기
        # 모든 플랜을 한번 씩 클릭
        for i in range(plan_numbers) : 
            plan_names = driver.find_element_by_id('coverage-header').find_elements_by_class_name('btn-radio')
            plan_names[i].click()
            wait.until(EC.invisibility_of_element((By.CLASS_NAME,"loading")))
        
        # 보험료 긁고
        for i in range(plan_numbers - 1) : 
            plans[i]['보험료'] = driver.find_element_by_id('coverage-premium').find_element_by_class_name(plan_codes[i]).find_element_by_tag_name('strong').text
        
        # 첫번째 플랜 클릭
        plan_names = driver.find_element_by_id('coverage-header').find_elements_by_class_name('btn-radio')
        plan_names[0].click()
        wait.until(EC.invisibility_of_element((By.CLASS_NAME,"loading")))
        
        # 마지막 플랜 보험료 긁기 
        plans[plan_numbers-1]['보험료'] = driver.find_element_by_id('coverage-premium').find_element_by_class_name(plan_codes[plan_numbers-1]).find_element_by_tag_name('strong').text
        
        types = ['실속 플랜','표준 플랜','고급 플랜']
        
        for index, code in enumerate(plan_codes) : 
            types_index = int(code.replace('n','')) - 1
            plans[index]['유형'] = types[types_index]
        
            
        contents += plans
    
    return contents 
