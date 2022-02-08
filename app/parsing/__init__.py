from threading import Thread, Lock
from app.models import TempJob
from app import db
from selenium.webdriver import Firefox
from bs4 import BeautifulSoup
from .utils import generate_dict_vacancy, get_fake_useragent, find_salary, get_location, ParsingProxyParametrs
import time


lock = Lock()


class Parsing():
    percentage = 0
    status_thread = False
    headhunter = False
    stackoverflow = False
    vacancies = []

    def __init__(self, headhunter, stackoverflow, query_parsing):
        Parsing.headhunter = headhunter
        Parsing.stackoverflow = stackoverflow
        self.query_parsing = query_parsing
        self.thread = None
        self._create_threading()

    @staticmethod
    def update_percentage(percentage):
        if Parsing.stackoverflow and Parsing.headhunter and percentage!=100:
            Parsing.percentage = percentage / 2
        else:
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

    @staticmethod
    def filling_database():
        try:
            if len(Parsing.vacancies) > 0:
                for vacancy in Parsing.vacancies:
                    temp_job = TempJob(title=vacancy['title'],
                                       company=vacancy['company'],
                                       salary=vacancy['salary'],
                                       # location=vacancy['location'],
                                       city=vacancy['city'],
                                       state=vacancy['state'],
                                       link=vacancy['link'],
                                       source=vacancy['source'])
                    db.session.add(temp_job)
                db.session.commit()
                Parsing.vacancies.clear()
        except:
            return

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
            Parsing.vacancies.extend(hh.get_vacancies())
            lock.release()
        if self.stackoverflow == 'y':
            so = StackOverflow(parsing_proxy_parametrs=parsing_proxy_parametrs,
                               url='https://stackoverflow.com/jobs?q=',
                               query_parsing=self.query_parsing,
                               str_page='&&pg=')
            so.parsing()
            lock.acquire()
            Parsing.vacancies.extend(so.get_vacancies())
            lock.release()
        if not Parsing.get_status_thread():
            return
        # lock.acquire()
        # if len(self.vacancies) > 0:
        #     self.filling_database()
        # lock.release()

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

        lock.acquire()
        Parsing.update_percentage(100)
        lock.release()
        ppp.close_tor()


class ParsingUtil():
    def __init__(self, parsing_proxy_parametrs, query_parsing, url, str_page):
        self.parametrs = parsing_proxy_parametrs
        self.query = query_parsing
        self.url = url
        self.str_page = str_page
        self.max_page = 0
        self.vacancies = []
        self._set_fake_useragent()

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
                    time.sleep(5)
                    driver.get(url=f'{self.url}{self.query}{self.str_page}{page}')
                    html = driver.page_source
                    if html is not None:
                        self._find_vacancies(html)
                        self._set_fake_useragent()
                        lock.acquire()
                        Parsing.update_percentage(page * 100 / self.max_page)
                        lock.release()
        except:
            lock.acquire()
            Parsing.update_percentage(100)
            Parsing.vacancies.clear()
            lock.release()

    def get_vacancies(self):
        return self.vacancies


class StackOverflow(ParsingUtil):
    def _get_max_page(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        paginator = soup.find('div', {'class': 's-pagination'}).find_all('a')
        max_page = int(paginator[-2].find('span').text)
        return max_page

    def _find_vacancies(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        results = soup.find_all('div', {'class': '-job'})
        for result in results:
            self.vacancies.append(self._create_vacancy(result))

    def _create_vacancy(self, html):
        title = html.find('h2').find('a').text.strip()
        company = html.find('h3').find_all('span')[0].text.strip()
        location = html.find('h3').find_all('span')[1].text.strip()
        if location is not 'No office location' or None:
            lock.acquire()
            city, state = get_location(location)
            lock.release()
        vacancy_id = html['data-jobid']
        link = f'https://stackoverflow.com/jobs/{vacancy_id}/'
        salary_list = html.find_all('li')
        salary = 0
        for item in salary_list:
            if str(item).find('title') > -1:
                find_item = item.text
                salary = find_salary(find_item)
            else:
                continue
        source = 'so'
        return generate_dict_vacancy(title, company, city, state, link, salary, source)


class HeadHunter(ParsingUtil):
    def _get_max_page(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        paginator = soup.find_all('span', {'class': 'pager-item-not-in-short-range'})
        max_page = int(paginator[-1].text)
        return max_page

    def _find_vacancies(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        results = soup.find_all('div', {'class': 'vacancy-serp-item'})
        for result in results:
            self.vacancies.append(self._create_vacancy(result))

    def _create_vacancy(self, html):
        title = html.find('div', {'class': 'vacancy-serp-item__info'}).find('a').text.strip()
        company = html.find('div', {'class': 'vacancy-serp-item__meta-info-company'}).find('a').text.strip()
        location = html.find('div', {'data-qa': 'vacancy-serp__vacancy-address'})
        if location is not None:
            location = location.text.strip()
            # metro = html.find('div', {'class': 'metro-point'})
            # if html.find('div', {'class': 'metro-point'}) is not None:
            #     metro.text.strip()
            #     location = location + ', ' + metro
            lock.acquire()
            city, state = get_location(location)
            lock.release()
        link = html.find('div', {'class': 'vacancy-serp-item__info'}).find('a')['href'].strip()
        salary_list = html.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
        if salary_list is None:
            salary = 0
        else:
            salary = find_salary(salary_list.text.strip())
        source = 'hh'
        return generate_dict_vacancy(title, company, city, state, link, salary, source)