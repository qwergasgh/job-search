from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer
from reader_vacancies import VacanciesReader

db = create_engine('sqlite:///db_app.db', echo = True)

vr = VacanciesReader('vacancies.csv')
meta = MetaData(db)

vacancies = Table(
   'vacancies', meta, 
   Column('id', Integer, primary_key = True), 
   Column('title', String), 
   Column('company', String),
   Column('location', String),
   Column('salary', Integer),
   Column('link', String),
)
meta.create_all(db)

conn = db.connect()
conn.execute(vacancies.insert(), vr.get_vacancies)

# sel = vacancies.select()
# result = conn.execute(sel)

# for row in result:
#    print (row)
