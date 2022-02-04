from threading import Thread
from app.models import TempJob
from app import db
from .utils import lock, ParsingProxyParametrs
from .headhunter import HeadHunter
from .stackoverflow import StackOverflow


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


