from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, DateTime
from datetime import datetime


db = create_engine('sqlite:///db_app.db', echo = True)

meta = MetaData(db)

table = Table(
   'users', meta, 
   Column('id', Integer, primary_key = True), 
   Column('role_id', Integer),
   Column('user_name', String), 
   Column('email', String),
   Column('first_name', String),
   Column('last_name', String),
   Column('phonenumber', String),
   Column('password_hash', String),
   Column('created', DateTime),
   Column('updated', DateTime)
)

users_table_data = [{'id': 1, 'user_name': 'admin', 'role_id': 1, 'email': 'admin_pars_job@gmail.com', 'password_hash': 'password', 'created': datetime.utcnow, 'updated': datetime.utcnow}]

meta.create_all(db)

conn = db.connect()

#conn.execute(table.insert(), users_table_data)
#conn.execute(table.delete(), users_table_data)
