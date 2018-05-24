from sqlalchemy import create_engine
from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from secure_message import constants


db = create_engine('postgresql://postgres:postgres@localhost:6432')
base = declarative_base()


class SecureMessage(base):
    __tablename__ = 'secure_message'
    __table_args__ = {'schema': 'securemessage'}

    id = Column("id", Integer(), primary_key=True)
    msg_id = Column("msg_id", String(constants.MAX_MSG_ID_LEN), unique=True, index=True)
    subject = Column("subject", String(constants.MAX_SUBJECT_LEN + 1))
    body = Column("body", String(constants.MAX_BODY_LEN + 1))
    thread_id = Column("thread_id", String(constants.MAX_THREAD_LEN + 1), index=True)
    collection_case = Column("collection_case", String(constants.MAX_COLLECTION_CASE_LEN + 1))
    ru_id = Column("ru_id", String(constants.MAX_RU_ID_LEN + 1))
    collection_exercise = Column("collection_exercise", String(constants.MAX_COLLECTION_EXERCISE_LEN + 1))
    survey = Column("survey", String(constants.MAX_SURVEY_LEN + 1))
    from_internal = Column('from_internal', Boolean())
    sent_datetime = Column('sent_datetime', DateTime())
    read_datetime = Column('read_datetime', DateTime())


class Events(base):
    """Events table model"""
    __tablename__ = "events"
    __table_args__ = {'schema': 'securemessage'}

    id = Column('id', Integer(), primary_key=True)
    event = Column('event', String(constants.MAX_EVENT_LEN + 1))
    msg_id = Column('msg_id', String(constants.MAX_MSG_ID_LEN + 1), ForeignKey('secure_message.msg_id'), index=True)
    date_time = Column('date_time', DateTime())


Session = sessionmaker(db)
session = Session()

messages = session.query(SecureMessage)
print(messages.all())

# events = session.query(Events)
# for message in messages:
#     print(message.msg_id)
