from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, DateTime


db = create_engine('sqlite:///db_app.db', echo = True)
meta = MetaData(db)

table = Table(
   'favorites', meta, 
   Column('id', Integer, primary_key = True), 
   Column('id_user', Integer),
   Column('id_vacancy', Integer)
)

meta.create_all(db)
conn = db.connect()

#conn.execute(table.drop())