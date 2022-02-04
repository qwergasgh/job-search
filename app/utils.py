from threading import Thread
import csv
from .models import Job
from app import db
import os
from flask_mail import Message
from app import mail
from flask import render_template
from app import app



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


                                         
