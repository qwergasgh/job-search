from bs4 import BeautifulSoup
from parsing import ParsingUtil

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
