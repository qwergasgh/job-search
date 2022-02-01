from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from subprocess import Popen, PIPE
from bs4 import BeautifulSoup
import fake_useragent
from threading import Thread, Lock
import csv
import time
from .models import TempJob, Job
from app import db
import os
from flask_mail import Message
from app import mail
from flask import render_template
from app import app
from app import search

lock = Lock()

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


def clear_tmp(user_name):
    list_str = ['vacancies', 'favorites_vacancies']
    for name in list_str:
        try:
            file = os.path.abspath(os.path.dirname(__file__)) + f'/tmp/{name}_for_{user_name}.csv'
            os.remove(file)
        except:
            continue


def get_jobs(query_parametrs):
    jobs_filter = Job.query.whoosh_search(query_parametrs.query).all()
    for job in jobs_filter:
        print(job.title)
    if query_parametrs.headhunter:
        # jobs = jobs_filter.filter(city=)
        pass


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_email_start, args=(app, msg)).start()


def send_email_start(app, msg):
    with app.app_context():
        mail.send(msg)


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('Reset Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reser_password_email.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password_email.html',
                                         user=user, token=token))


                                         
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
        # ppp = ParsingProxyParametrs()
        # parsing_proxy_parametrs = ppp.get_parametrs_for_parsing()
        # if self.headhunter == 'y':
        #     hh = HeadHunter(parsing_proxy_parametrs=parsing_proxy_parametrs,
        #                     url='https://hh.ru/search/vacancy?area=1&fromSearchLine=true&text=',
        #                     query_parsing=self.query_parsing, 
        #                     str_page='&page=')
        #     hh.parsing()
        #     lock.acquire()
        #     self.vacancies.append(hh.get_vacancies())
        #     lock.release()
        # if self.stackoverflow == 'y':
        #     so = StackOverflow(parsing_proxy_parametrs=parsing_proxy_parametrs,
        #                     url='https://stackoverflow.com/jobs?q=',
        #                     query_parsing=self.query_parsing,
        #                     str_page='&&pg=')
        #     so.parsing()
        #     lock.acquire()
        #     self.vacancies.append(so.get_vacancies())
        #     lock.release()
        # if not Parsing.get_status_thread():
        #         return
        # lock.acquire()
        # if len(self.vacancies) > 0:
        #     self.filling_database()
        # lock.release()

        # for tests
        while Parsing.get_percentage() < 100:
            if not Parsing.get_status_thread():
                return
            # time.sleep(2)
            count = Parsing.get_percentage() + 1
            lock.acquire()
            Parsing.update_percentage(count)
            print(count)
            lock.release()

        # ppp.close_tor()
        lock.acquire()
        self.percentage = 100
        lock.release()


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
        salary = 666
        source = 'hh'
        return self._generate_dict_vacancy(title, company, location, link, salary, source)


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
        salary = 666
        source = 'so'
        return self._generate_dict_vacancy(title, company, location, link, salary, source)

