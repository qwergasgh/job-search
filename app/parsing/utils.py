from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from subprocess import Popen, PIPE
from bs4 import BeautifulSoup
import fake_useragent
from parsing import Parsing
from threading import Lock

lock = Lock()

class ParsingProxyParametrs():
    def __init__(self):
        #self.gecko_path = os.path.abspath(os.path.dirname(__file__)) + '/geckodriver'
        self.gecko_path = '/usr/bin/geckodriver'
        self.binary_path = '/usr/bin/firefox'
        self.tor_path = '/usr/bin/tor'
        self.tor = self._create_tor()
        self.options = self._create_options()
        self.service = Service(executable_path=self.gecko_path)

    def _create_tor(self):
        try:
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
        except:
            return None

    def _create_options(self):
        options = Options()
        options.binary_location = self.binary_path
        options.set_preference('network.proxy.type', 1)
        options.set_preference('network.proxy.socks', '127.0.0.1')
        options.set_preference('network.proxy.socks_port', 9050)
        options.set_preference("network.proxy.socks_remote_dns", True)
        return options

    def close_tor(self):
        if self.tor is not None:
            self.tor.kill()
            print('tor closed\ntor exit code = ' + str(self.tor.poll()))

    def get_parametrs_for_parsing(self):
        return {'options': self.options,
                'service': self.service}


class ParsingUtil():
    def __init__(self, parsing_proxy_parametrs, query_parsing, url, str_page):
        self.parametrs = parsing_proxy_parametrs
        self.query = query_parsing
        self.url = url
        self.str_page = str_page
        self.max_page = 0
        self.vacancies = []
        self._set_fake_useragent()

    # testing !!!
    def _set_fake_useragent(self):
        self.parametrs['options'].set_preference('general.useragent.override', 
                                                 self._get_fake_useragent())

    def _get_fake_useragent(self):
        try:
            return fake_useragent.UserAgent().random
        except:
            # add useragent !!!
            return ''

    def _get_max_page(self, html):
        pass

    def _find_vacancies(self, html):
        pass

    def _create_vacancy(self, html):
        pass

    def _generate_dict_vacancy(self, title, company, location, link, salary, source):
        return {'title': title, 
                'company': company, 
                'location': location, 
                'link': link,
                'salary': salary,
                'source': source}

    def parsing(self):
        try:
            with Firefox(options=self.parametrs['options'], service=self.parametrs['service']) as driver:
                driver.get(url=f'{self.url}{self.query}')
                self.max_page = self._get_max_page(driver.page_source)
                for page in range(self.max_page):

                    if not Parsing.get_status_thread:
                        return

                    # number page testing !!!
                    driver.get(url=f'{self.url}{self.query}{self.str_page}{page}')
                    html = driver.page_source
                    if  html is not None:
                        self._find_vacancies(html)
                        self._set_fake_useragent()
                        # tesiting !!!
                        lock.acquire()
                        Parsing.update_percentage(int(page))
                        lock.release()
        except:
            lock.acquire()
            Parsing.update_percentage(100)
            print('error parsing')
            lock.release()

    def get_vacancies(self):
        return self.vacancies

    def percentage(self, number):
        return number / self.max_page / 2

