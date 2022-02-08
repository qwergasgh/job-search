from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from subprocess import Popen, PIPE
import fake_useragent
import re
from sys import platform
from translate import Translator
from langdetect import detect
from geopy.geocoders import Nominatim



geolocator = Nominatim(user_agent="app")
translator= Translator(to_lang="Russian")



class ParsingProxyParametrs():
    def __init__(self):
        if platform == 'linux':
            self.gecko_path = '/usr/bin/geckodriver'
            self.binary_path = '/usr/bin/firefox'
            self.tor_path = '/usr/bin/tor'
        if platform.index('win') > -1:
            self.gecko_path = r'C:\Program Files\Mozilla Firefox\geckodriver.exe'
            self.binary_path = r'C:\Program Files\Mozilla Firefox\firefox.exe'
            self.tor_path = r'C:\Program Files\TorBrowser\Bundle\Tor\tor.exe'
        self.tor = self._create_tor()
        self.options = self._create_options()
        self.service = Service(executable_path=self.gecko_path)

    def _create_tor(self):
        try:
            tor = Popen(self.tor_path, shell=True, stdout=PIPE, bufsize=-1)
            if tor.poll() is not None:
                raise Exception('No connection to tor :^(')
            # in logging
            # result_code = str(tor.stdout.readlines()[-1]).lower()
            return tor
        except:
            return None

    def _create_options(self):
        options = Options()
        options.binary_location = self.binary_path
        # options.set_preference('network.proxy.type', 1)
        # options.set_preference('network.proxy.socks', '127.0.0.1')
        # options.set_preference('network.proxy.socks_port', 9050)
        # options.set_preference("network.proxy.socks_remote_dns", True)
        return options

    def close_tor(self):
        if self.tor is not None:
            self.tor.kill()
            # in logging
            # result_code = str(self.tor.poll())

    def get_parametrs_for_parsing(self):
        return {'options': self.options,
                'service': self.service}


def get_fake_useragent():
    try:
        return fake_useragent.UserAgent().random
    except:
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0'


#def generate_dict_vacancy(title, company, location, link, salary, source):
def generate_dict_vacancy(title, company, city, state, link, salary, source):
    if company is None:
        company = 'No company'
    # if location is None:
    #     location = 'No office location'
    if city is None:
        city = 'No office city'
    if state is None:
        state = 'No office state'
    return {'title': title,
            'company': company,
            # 'location': location,
            'city': city,
            'state': state,
            'link': link,
            'salary': salary,
            'source': source}


def find_salary(salary_result):
    if salary_result is not None:
        salary_result_values = re.findall('[0-9]+', salary_result)
        if salary_result.find('от') or salary_result.find('до'):
            return int((salary_result_values[0] + '000'))
        if len(salary_result_values) > 2:
            return int((str(int((int(salary_result_values[0]) + int(salary_result_values[2])) / 2)) + '000'))
        if len(salary_result_values) == 1:
            return int((salary_result_values[0] + '000'))
        if len(salary_result_values) == 2:
            return int((str(int((int(salary_result_values[0]) + int(salary_result_values[1])) / 2)) + '000'))
        return 0
    else:
        return 0


def get_location(location):
    lang_text = detect(location)
    if lang_text is not 'ru':
        location = translator.translate(location)
    location = geolocator.geocode(location, language="ru")
    try:
        list_location = location.split(', ')
        count = len(list_location)
        city = list_location[0]
        state = list_location[count - 1]
        print(city, state)
        return city, state      
    except:
        print('ERROR - ', location)
        return None, None
    
    