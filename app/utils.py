from flask import render_template
from flask_mail import Message
from app import db, mail, app
from threading import Thread
from sqlalchemy import and_
from .models import Job
import csv
import os



def save_to_csv(vacancies, file_name):
    try:
        with open(file_name, mode='w', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Title', 'Company', 'Salary', 'City', 'State', 'Link'])
            for vacancy in vacancies:
                writer.writerow([vacancy.title, vacancy.company, vacancy.salary, 
                                vacancy.city, vacancy.state, vacancy.link])
        return True
    except:
        return False


def clear_tmp(user_name):
    list_str = ('vacancies', 'favorites_vacancies')
    for name in list_str:
        try:
            file = os.path.join(os.path.abspath(os.path.dirname(__file__)), \
                   f'/tmp/{name}_for_{user_name}.csv')
            os.remove(file)
        except:
            continue


def get_jobs(query_parametrs):
    salary = 0 if query_parametrs['salary'] == '' else query_parametrs['salary']
    jobs_filter = Job.query.search(query_parametrs['query']).filter(Job.salary >= salary)
    if query_parametrs['city'].strip() != '':
        jobs_filter = jobs_filter.filter(Job.city == query_parametrs['city'])
    if query_parametrs['state'] != '':
        jobs_filter = jobs_filter.filter(Job.state == query_parametrs['state'])
    return jobs_filter.order_by(Job.id.desc())


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


                                         
