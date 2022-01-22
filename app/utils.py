from flask import redirect, url_for
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
        time.sleep(1)
        PERCENTAGE += 1

def update_persentage():
    global PERCENTAGE
    PERCENTAGE = 0

def get_percentage():
    return PERCENTAGE