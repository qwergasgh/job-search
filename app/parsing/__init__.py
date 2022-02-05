from threading import Thread, Lock
from app.models import TempJob
from app import db
from selenium.webdriver import Firefox
from bs4 import BeautifulSoup
from .utils import generate_dict_vacancy, get_fake_useragent, find_salary, ParsingProxyParametrs


lock = Lock()


class Parsing():
    percentage = 0
    status_thread = False

    def __init__(self, headhunter, stackoverflow, query_parsing):
        self.headhunter = headhunter
        self.stackoverflow = stackoverflow
        self.query_parsing = query_parsing
        self.thread = None
        self.vacancies = []
        self._create_threading()

    @staticmethod
    def update_percentage(percentage):
        Parsing.percentage = percentage

    @staticmethod
    def get_percentage():
        return Parsing.percentage

    @staticmethod
    def get_status_thread():
        return Parsing.status_thread

    @staticmethod
    def set_status_thread(status=False):
        Parsing.status_thread = status

    def _create_threading(self):
        self.thread = Thread(target=self._start)

    def parsing_vacancies(self):
        Parsing.set_status_thread(True)
        self.thread.start()

    def filling_database(self):
        try:
            for vacancy in self.vacancies:
                temp_job = TempJob(title=vacancy.title, 
                                   company=vacancy.company, 
                                   salary=vacancy.salary, 
                                   location=vacancy.location, 
                                   link=vacancy.link,
                                   source=vacancy.source)
                db.session.add(temp_job)
                db.session.commit()
            return True
        except:
            return False

    def _start(self):
        ppp = ParsingProxyParametrs()
        parsing_proxy_parametrs = ppp.get_parametrs_for_parsing()
        if self.headhunter == 'y':
            hh = HeadHunter(parsing_proxy_parametrs=parsing_proxy_parametrs,
                            url='https://hh.ru/search/vacancy?search_field=name&'
                                'search_field=company_name&search_field=description&text=',
                            query_parsing=self.query_parsing,
                            str_page='&page=')
            hh.parsing()
            lock.acquire()
            self.vacancies.append(hh.get_vacancies())
            lock.release()
        if self.stackoverflow == 'y':
            so = StackOverflow(parsing_proxy_parametrs=parsing_proxy_parametrs,
                            url='https://stackoverflow.com/jobs?q=',
                            query_parsing=self.query_parsing,
                            str_page='&&pg=')
            so.parsing()
            lock.acquire()
            self.vacancies.append(so.get_vacancies())
            lock.release()
        if not Parsing.get_status_thread():
            return
        lock.acquire()
        if len(self.vacancies) > 0:
            self.filling_database()
        lock.release()

        # for tests
        # while Parsing.get_percentage() < 100:
        #     if not Parsing.get_status_thread():
        #         return
        #     # time.sleep(2)
        #     count = Parsing.get_percentage() + 1
        #     lock.acquire()
        #     Parsing.update_percentage(count)
        #     print(count)
        #     lock.release()

        ppp.close_tor()
        lock.acquire()
        self.percentage = 100
        lock.release()


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
                                                 get_fake_useragent())

    def _get_max_page(self, html):
        pass

    def _find_vacancies(self, html):
        pass

    def _create_vacancy(self, html):
        pass

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
                    if html is not None:
                        self._find_vacancies(html)
                        self._set_fake_useragent()
                        # testing !!!
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


class StackOverflow(ParsingUtil):
    def _get_max_page(self, html):
        # testing not soup !!!
        soup = BeautifulSoup(html, 'html.parser')
        paginator = soup.find('div', {'class': 's-pagination'}).find_all('a')
        max_page = int(paginator[-2].find('span').text)
        return max_page

    def _find_vacancies(self, html):
        # testing not soup !!!
        soup = BeautifulSoup(html, 'html.parser')
        results = soup.find_all('div', {'class': '-job'})
        for result in results:
            self.vacancies.append(self._create_vacancy(result))

    def _create_vacancy(self, html):
        title = html.find('h2').find('a').text.strip()
        company = html.find('h3').find_all('span')[0].text.strip()
        location = html.find('h3').find_all('span')[1].text.strip()
        vacancy_id = html['data-jobid']
        link = f'https://stackoverflow.com/jobs/{vacancy_id}/'
        salary_list = html.find_all('li')
        for item in salary_list:
            salary = find_salary(str(item))
            if salary is None:
                continue
        print(salary)
        source = 'so'
        return generate_dict_vacancy(title, company, location, link, salary, source)


class HeadHunter(ParsingUtil):
    # testing not soup !!!
    def _get_max_page(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        paginator = soup.find_all('span', {'class': 'pager-item-not-in-short-range'})
        max_page = int(paginator[-1].text)
        return max_page

    def _find_vacancies(self, html):
        # testing not soup !!!
        soup = BeautifulSoup(html, 'html.parser')
        results = soup.find_all('div', {'class': 'vacancy-serp-item'})
        for result in results:
            self.vacancies.append(self._create_vacancy(result))

    def _create_vacancy(self, html):
        title = html.find('div', {'class': 'vacancy-serp-item__info'}).find('a').text.strip()
        company = html.find('div', {'class': 'vacancy-serp-item__meta-info-company'}).find('a').text.strip()
        location = html.find('span', {'data-qa': 'vacancy-serp__vacancy-address'})
        if location is not None:
            location = location.text.strip().partition('и еще')[0]
        link = html.find('div', {'class': 'vacancy-serp-item__info'}).find('a')['href'].strip()
        salary = find_salary(html.find('span', {'class': 'bloko-header-section-3 bloko-header-section-3_lite'}))
        print(salary)
        source = 'hh'
        return generate_dict_vacancy(title, company, location, link, salary, source)