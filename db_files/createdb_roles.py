from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer
from sqlalchemy.sql.sqltypes import Boolean

db = create_engine('sqlite:///db_app.db', echo = True)

meta = MetaData(db)

table = Table(
   'roles', meta, 
   Column('id', Integer, primary_key = True), 
   Column('name', String),
   Column('privilege', Boolean)
)

roles = [{'name': 'User', 'privilege': False}, {'name': 'Administrator', 'privilege': True }]

meta.create_all(db)
conn = db.connect()

#conn.execute(table.drop())
#conn.execute(table.delete(), roles)
conn.execute(table.insert(), roles)
