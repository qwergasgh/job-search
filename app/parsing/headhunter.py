from bs4 import BeautifulSoup
from parsing import ParsingUtil

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