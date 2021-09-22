import os
import time
import random
import pandas as pd
from param import *
from selenium import webdriver

class PostDocSpider():

    ''' 注意：driver打开之后，页面有个验证码，这个手动输入吧，没写代码。
            然后就不用管了，其它操作selenium会自动继续，直至完成。
    '''
    
    __version__ = '2021-09-18'
    def __init__(self):
        self._url = PARAMS['url']
        self._driver = webdriver.Chrome(<chromedriver_path>)
        self._driver.maximize_window()
        self._driver.get(self._url)
        self.provs = list(PARAMS['prov'].values())
        self.moes = list(PARAMS['moe'].values())
        print('provs===', self.provs)
        print('moes===', self.moes)
        time.sleep(5)
    
    def create_folder(self, folder):
        if not os.path.exists(folder):
            os.makedirs(folder)    
    
    def run(self):
        # 1. 找到省份
        for prov in self.provs:
            self.create_folder('trans/{}'.format(prov))
            if prov in ['其它']:
                continue
            x1 = '//*[@id="chaxun_shezhandanwei"]/div[2]/table[1]/tbody/tr/td[2]/select[1]'
            self._driver.find_element_by_xpath(x1).click()
            time.sleep(random.randint(1, 30)/10)
            self._driver.find_element_by_xpath('//option[contains(text(),"{}")]'.format(prov)).click()
            time.sleep(random.randint(1, 10)/10)
            self.spec_moe(prov)
    
    def spec_moe(self, prov):
        # 2. 每个一级学科
        for moe in self.moes:
            basename = 'trans/{0}/{0}_{1}'.format(prov, moe)
            excel_f = basename + '.xlsx'
            if os.path.exists(excel_f): continue
            x2 = '//*[@id="chaxun_shezhandanwei"]/div[2]/table[2]/tbody/tr/td[2]/select'
            self._driver.find_element_by_xpath(x2).click()
            time.sleep(random.randint(1, 30)/10)
            self._driver.find_element_by_xpath('//option[contains(text(),"{}")]'.format(moe)).click()
            time.sleep(random.randint(1, 10)/10)
            
            # 3. 防止流动站变化
            x3 = '//*[@id="chaxun_shezhandanwei"]/div[2]/table[1]/tbody/tr/td[3]/select'
            self._driver.find_element_by_xpath(x3).click()
            time.sleep(random.randint(1, 20)/10)        
            self._driver.find_element_by_xpath('//option[contains(text(),"{}")]'.format('流动站设站单位')).click()
            
            # 点查询
            search = '//*[@id="chaxun_shezhandanwei"]/div[2]/table[3]/tbody/tr/td/input'
            self._driver.find_element_by_xpath(search).click()
            time.sleep(random.randint(3, 4))
            
            l = []
            for i in range(1, 10000):
                try:
                    sch = self._driver.find_element_by_xpath(\
                        '//*[@id="chaxun_shezhandanwei"]/div[3]/table/tbody/tr[{}]/td[1]'.format(i)).text
                    dept = self._driver.find_element_by_xpath(\
                        '//*[@id="chaxun_shezhandanwei"]/div[3]/table/tbody/tr[{}]/td[2]'.format(i)).text
                    phone = self._driver.find_element_by_xpath(\
                        '//*[@id="chaxun_shezhandanwei"]/div[3]/table/tbody/tr[{}]/td[3]'.format(i)).text
                    fax = self._driver.find_element_by_xpath(\
                        '//*[@id="chaxun_shezhandanwei"]/div[3]/table/tbody/tr[{}]/td[4]'.format(i)).text
                    l.append({'单位名称': sch, '主管部门': dept, '电话': phone, '传真': fax})
                except:
                    break
            
            df = pd.DataFrame(l)
            if not df.empty:
                df['所在地区'] = prov
                df['一级学科'] = moe
                df = df[['所在地区', '一级学科', '单位名称', '主管部门', '电话', '传真']]
            with open(basename + '.html', 'w+', encoding='utf-8') as file:
                file.write(self._driver.page_source)
            df.to_excel(excel_f, index=False)
        
PostDocSpider().run()

