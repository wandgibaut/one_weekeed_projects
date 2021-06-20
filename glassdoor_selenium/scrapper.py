from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import json
import time
import getopt
import sys


class GlassdoorReviewScrapper:
    def __init__(self, user_creds, webdriver_path):
        self.user, self.pwd = self.get_keys(user_creds)
        self.webdriver = webdriver_path
        self.browser = webdriver.Chrome(executable_path=webdriver_path)
        self.browser.get('https://www.glassdoor.com')
        self.browser.implicitly_wait(2)
        pass

    def get_keys(self, filename):
        with open(filename) as sfile:
            secrets = json.load(sfile)
            return secrets['login'], secrets['password']


    def save_json(self, pros, cons, filename):
        answer = {'pros': pros, 'cons': cons}
        with open(filename, 'w') as outfile:
            json.dump(answer, outfile)
            return 0

    def reopen(self):
        self.browser = webdriver.Chrome(executable_path=self.webdriver)
        self.browser.get('https://www.glassdoor.com')
        self.browser.implicitly_wait(2)

    def close(self):
        self.browser.close()

    def glassdoor_login(self):
        self.browser.find_element_by_xpath('//*[@id="SiteNav"]/nav/div[1]/div[1]/button').click()

        login = self.browser.find_element_by_xpath('//*[@id="userEmail"]')
        login.send_keys(self.user)
        pswd = self.browser.find_element_by_xpath('//*[@id="userPassword"]')
        pswd.send_keys(self.pwd)
        pswd.send_keys(Keys.RETURN)


    def search_company(self, company):
        self.browser.find_element_by_xpath('//*[@id="SearchForm"]/div[1]/button').click()
    
        self.browser.find_element_by_xpath('//*[@id="sc"]/div[1]/span[2]').click()
        search_empresa = self.browser.find_element_by_xpath('//*[@id="scKeyword"]')
        search_empresa.send_keys(Keys.CONTROL + 'a')
        search_empresa.send_keys(Keys.BACKSPACE)
        search_empresa.send_keys(company)

        search_cidade = self.browser.find_element_by_xpath('//*[@id="scLocation"]')
        search_cidade.send_keys(Keys.CONTROL + 'a')
        search_cidade.send_keys(Keys.BACKSPACE)
        search_cidade.send_keys(Keys.RETURN)


    def collect_reviews(self):
        pros = []
        cons = []
        
        try:
            nxt_button = self.browser.find_element_by_xpath('//*[@id="NodeReplace"]/main/div/div/div[1]/div[3]/div/div[1]/button[2]')

            while nxt_button.is_enabled():
                raw = self.browser.find_element_by_xpath('//*[@id="ReviewsFeed"]/ol').find_elements_by_tag_name('span')

                self.browser.implicitly_wait(1)
                for element in raw:
                    if element.get_attribute('data-test'):
                        if element.get_attribute('data-test') == 'pros':
                            pros.append(element.text)
                        elif element.get_attribute('data-test') == 'cons':
                            cons.append(element.text)
        
                self.browser.implicitly_wait(3)
                nxt_button.click()
        
                time.sleep(2)
                nxt_button = self.browser.find_element_by_xpath('//*[@id="NodeReplace"]/main/div/div/div[1]/div[3]/div/div[1]/button[2]')
        except:
            try:
                raw = self.browser.find_element_by_xpath('//*[@id="ReviewsFeed"]/ol').find_elements_by_tag_name('span')

                self.browser.implicitly_wait(1)
                for element in raw:
                    if element.get_attribute('data-test'):
                        if element.get_attribute('data-test') == 'pros':
                            pros.append(element.text)
                        elif element.get_attribute('data-test') == 'cons':
                            cons.append(element.text)
            except Exception as e:
                print(e)

        return pros, cons

    def full_scrapping_process(self, company):
        self.search_company( company)

        try:
            self.browser.find_element_by_xpath('//*[@id="MainCol"]/div/div[1]/div/div[1]/div/div[2]/h2/a').click()
            self.browser.find_element_by_xpath('//*[@id="EIProductHeaders"]/div/a[2]').click()
        except Exception as e:
            reviews = self.browser.find_element_by_xpath('//*[@id="EIProductHeaders"]/div/a[2]')
            if 'Avaliações' not in reviews.text :
                reviews = self.browser.find_element_by_xpath('//*[@id="EIProductHeaders"]/div/a[1]')
            
            reviews.click()
            
        pros, cons = self.collect_reviews()
        #print(cons)
        
        self.save_json(pros, cons, 'data/' + company + '.json')
        return pros, cons


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hm:c:", ["help=", "companies="])
    except getopt.GetoptError:
        print('call with -h or --help to see options')
        sys.exit(2)

    companies = []

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print('help')
        elif opt in ('-c', '--companies'):
            companies = arg.split(',')
  
    
    
    creds = './secrets.json'
    webdriverpath = './chromedriver'
    scrapper = GlassdoorReviewScrapper(creds, webdriverpath)
    scrapper.glassdoor_login() #login 1x so

    print(companies)
    for company in companies:
        scrapper.full_scrapping_process(company)
    
    scrapper.close()
