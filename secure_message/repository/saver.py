import logging

from sqlalchemy.exc import SQLAlchemyError
from structlog import wrap_logger
from secure_message.exception.exceptions import MessageSaveException
from secure_message.repository.database import db, SecureMessage, Status

logger = wrap_logger(logging.getLogger(__name__))


class Saver:
    """Created when saving a message"""

    @staticmethod
    def save_message(domain_message, session=db.session):
        """save message to database"""
        db_message = SecureMessage()
        db_message.set_from_domain_model(domain_message)

        try:
            session.add(db_message)
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            logger.exception('Secure message save failed')
            raise MessageSaveException('Message save failed')

    @staticmethod
    def save_msg_status(actor, msg_id, label, session=db.session):
        """save message status to database"""
        db_status_to = Status()
        db_status_to.set_from_domain_model(msg_id, actor, label)

        try:
            session.add(db_status_to)
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            logger.exception('Message status save failed')
            raise MessageSaveException('Message save failed')
