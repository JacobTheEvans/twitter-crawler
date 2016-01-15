from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData ,text, BigInteger, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql://jacob:jacob@localhost/jacob")
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class User(Base):
    __tablename__  = "users"
    id = Column(BigInteger, primary_key=True)
    screen_name = Column(String(1000), nullable=False)
    processed = Column(Boolean,nullable=False)

#User query functions
def add_user(id,name,processed):
    new_user = User(id=id,screen_name=name,processed=processed)

    session.add(new_user)
    session.commit()
    try:
        pass
    except:
        session.rollback()
        print "Error"

def get_users():
    result = []
    data = session.query(User).all()
    for item in data:
        result.extend([item.screen_name])
    return result

def get_user_from_id(id):
    result = session.query(User).filter_by(id=id).all()
    return result

def get_user_from_screen_name(screen_name):
         result = session.query(User).filter_by(screen_name=screen_name).all()
         return result

Base.metadata.create_all(engine)

#Friend functions
def make_new_friend_table(screen_name):
    metadata = MetaData(bind=engine)
    user_table = Table(
    screen_name + "_friends",
    metadata,
    Column("id", String(100), primary_key=True),
    Column("screen_name", String(100), nullable=False)
    )
    metadata.create_all()

def get_friends(screen_name):
    statement = text("select * from %s" % screen_name + "_friends")
    result = engine.execute(statement)
    data = []
    for row in result:
        data.append(row[1])
    return data

def add_friend(table,id,screen_name):
    statement = text("insert into %s VALUES ('%s','%s')" % (table + "_friends",id,screen_name))
    result = engine.execute(statement)

#Follower functions
def make_new_follower_table(screen_name):
    metadata = MetaData(bind=engine)
    user_table = Table(
    screen_name + "_followers",
    metadata,
    Column("id", String(100), primary_key=True),
    Column("screen_name", String(100), nullable=False)
    )
    metadata.create_all()

def get_followers(screen_name):
    statement = text("select * from %s" % screen_name + "_followers")
    result = engine.execute(statement)
    data = []
    for row in result:
        data.append(row[1])
    return data

def add_follower(table,id,screen_name):
    statement = text("insert into %s VALUES ('%s','%s')" % (table + "_followers",id,screen_name))
    result = engine.execute(statement)
