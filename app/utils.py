from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from subprocess import Popen, PIPE
from bs4 import BeautifulSoup
import fake_useragent
import os
import csv
import time

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
    def __init__(self, query):
        self.query = query
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



# with Firefox(options=options, service=service) as driver:
#    driver.get(url=URL_IP)
#    soup = BeautifulSoup(driver.page_source, 'html.parser')
#    print(soup.find('div', {'class': 'ip'}).text.strip())
#    print(soup.find_all('div', {'class': 'ip-icon-label'}))


