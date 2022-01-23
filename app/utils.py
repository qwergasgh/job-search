from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from subprocess import Popen, PIPE
from bs4 import BeautifulSoup
import fake_useragent
import os
import csv
import time
import requests


PERCENTAGE = 0

def save_to_csv(vacancies, file):
    try:
        with open(file, mode='w', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Title', 'Company', 'Salary', 'Location', 'Link'])
            for vacancy in vacancies:
                writer.writerow([vacancy.title, vacancy.company, vacancy.salary, 
                                vacancy.location, vacancy.link])
        return True
    except:
        return False

def parsing_vacancies(parametrs):
    global PERCENTAGE
    while PERCENTAGE < 100:
        # time.sleep(1)
        PERCENTAGE += 1

def update_persentage():
    global PERCENTAGE
    PERCENTAGE = 0

def get_percentage():
    return PERCENTAGE


class ParsingQuery():
    def __init__(self):
        self.percentage = 0
        self.gecko_path = os.path.abspath(os.path.dirname(__file__)) + '/geckodriver'
        self.binary_path = '/usr/bin/firefox'
        self.tor_path = '/usr/bin/tor'
        self.tor = self.create_tor()
        self.options = self.create_options()
        self.service = Service(executable_path=self.gecko_path)

    def update_persentage(self):
        self.percentage = 0

    def get_percentage(self):
        return self.percentage

    def create_tor(self):
        print('tor start')
        tor = Popen(self.tor_path, shell=True, stdout=PIPE, bufsize=-1)
        if tor.poll() is not None:
            raise Exception('No connection to tor :^(')
        result_code = str(tor.stdout.readlines()[-1]).lower()
        if 'failed' in result_code:
            print('tor process is already running or port is in use')
        if 'done' in result_code:
            print('tor process created')
        print('tor works')
        return tor

    def create_options(self):
        options = Options()
        options.binary_location = self.binary_path
        options.set_preference('network.proxy.type', 1)
        options.set_preference('network.proxy.socks', '127.0.0.1')
        options.set_preference('network.proxy.socks_port', 9050)
        options.set_preference("network.proxy.socks_remote_dns", True)
        fake_user = fake_useragent.UserAgent().random
        options.set_preference('general.useragent.override', fake_user)
        return options

    def close_tor(self):
        if self.tor is not None:
            self.tor.kill()
            print('tor closed\ntor exit code = ' + str(self.tor.poll()))

    def get_parametrs_for_parsing(self):
        parametrs_for_parsing = {'options': self.options,
                                 'service': self.service}
        return parametrs_for_parsing

# with Firefox(options=options, service=service) as driver:
#    driver.get(url=URL_IP)
#    soup = BeautifulSoup(driver.page_source, 'html.parser')
#    print(soup.find('div', {'class': 'ip'}).text.strip())
#    print(soup.find_all('div', {'class': 'ip-icon-label'}))

class HeadHunter:
    def __init__(self):
        fake_user = fake_useragent.UserAgent().random
        self.__FAKE_HEADER = {'user-agent': fake_user}
        self.__HH_URL = 'https://hh.ru/search/vacancy?area=1&fromSearchLine=true&text=python'
        self.__STR_PAGE = '&page='

    def __get_max_page(self):
        request = requests.get(self.__HH_URL, headers=self.__FAKE_HEADER)
        if request.status_code != 200:
            raise Exception('FAILED URL')

        soup = BeautifulSoup(request.text, 'html.parser')
        paginator = soup.find_all('span', {'class': 'pager-item-not-in-short-range'})
        max_page = int(paginator[-1].text)

        return max_page

    def __create_vacancy(self, html):
        title = html.find('div', {'class': 'vacancy-serp-item__info'}).find('a').text.strip()
        company = html.find('div', {'class': 'vacancy-serp-item__meta-info-company'}).find('a').text.strip()
        tmp_location = html.find('span', {'data-qa': 'vacancy-serp__vacancy-address'})
        location = ''
        if tmp_location is None:
            location = 'Empty'
        else:
            location = html.find('span', {'data-qa': 'vacancy-serp__vacancy-address'}).text.strip().partition('и еще')[0]
        link = html.find('div', {'class': 'vacancy-serp-item__info'}).find('a')['href']

        vacancy = Vacancy(title=title, company=company, location=location, link=link)
        return vacancy

    def get_vacancies(self):
        vacancies = []
        # for page in range(self.__get_max_page()):
        #     request = requests.get(f'{self.__HH_URL}{self.__STR_PAGE}{page}', headers=self.__FAKE_HEADER)
        #     if request.status_code != 200:
        #         continue
        #
        #     soup = BeautifulSoup(request.text, 'html.parser')
        #     results = soup.find_all('div', {'class': 'vacancy-serp-item'})
        #     for result in results:
        #         vacancies.append(self.__create_vacancy(result))
        request = requests.get(f'{self.__HH_URL}{self.__STR_PAGE}{0}', headers=self.__FAKE_HEADER)
        soup = BeautifulSoup(request.text, 'html.parser')
        stop = soup.find_all('div', {'class': 'serp-special serp-special_under-results'})
        print(stop)
        results = soup.find_all('div', {'class': 'vacancy-serp-item'})
        for result in results:
            vacancies.append(self.__create_vacancy(result))

        return vacancies


