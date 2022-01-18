from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from subprocess import Popen, PIPE
from bs4 import BeautifulSoup
import fake_useragent
import csv
import os



def save_to_csv(vacancies, file='vacancies'):
    with open(f'{file}.csv', mode='w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'Company', 'Salary', 'Location', 'Link'])
        for vacancy in vacancies:
            writer.writerow([vacancy.title, vacancy.company, vacancy.salary, 
                             vacancy.location, vacancy.link])

def parsing_vacancies(parametrs):
    print("parsing")
