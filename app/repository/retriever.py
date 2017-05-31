import logging

from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, case
from app.validation.labels import Labels
from werkzeug.exceptions import InternalServerError, NotFound

from app.repository.database import SecureMessage, Status, Events
from app.validation.user import User


logger = logging.getLogger(__name__)


class Retriever:
    """Created when retrieving messages"""
    @staticmethod
    def retrieve_message_list(page, limit, user_urn, ru=None, survey=None, cc=None, label=None,
                              business=None, descend=True):
        """returns list of messages from db"""
        user = User(user_urn)
        conditions = []
        status_conditions = []

        if user.is_respondent:
            status_conditions.append(Status.actor == str(user_urn))
        else:
            #  default survey given this will change once integrated with party service which will provide survey types for internal user
            if survey is not None:
                status_conditions.append(Status.actor == str(survey))
            else:
                status_conditions.append(Status.actor == 'bres')

        if label is not None:
            status_conditions.append(Status.label == str(label))
        else:
            status_conditions.append(Status.label != Labels.DRAFT_INBOX.value)

        if ru is not None:
            conditions.append(SecureMessage.reporting_unit == str(ru))

        if business is not None:
            conditions.append(SecureMessage.business_name == str(business))

        if survey is not None:
            conditions.append(SecureMessage.survey == str(survey))

        if cc is not None:
            conditions.append(SecureMessage.collection_case == str(cc))

        try:
            if descend:
                result = SecureMessage.query.join(Events).join(Status)\
                    .filter(and_(*conditions))\
                    .filter(and_(*status_conditions))\
                    .order_by(case([(Events.event == 'Sent', Events.date_time),
                                    (Events.event == 'Draft_Saved', Events.date_time)],
                                   else_=0).desc(), Events.event.desc()).paginate(page, limit, False)
            else:
                result = SecureMessage.query.join(Events).join(Status)\
                    .filter(and_(*conditions)) \
                    .filter(and_(*status_conditions)) \
                    .order_by(case([(Events.event == 'Sent', Events.date_time),
                                    (Events.event == 'Draft_Saved', Events.date_time)],
                                   else_='z').asc(), Events.event.desc()).paginate(page, limit, False)

        except Exception as e:
            logger.error(e)
            raise(InternalServerError(description="Error retrieving messages from database"))

        return True, result

    @staticmethod
    def retrieve_message(message_id, user_urn):
        """returns single message from db"""
        db_model = SecureMessage()

        try:
            result = db_model.query.filter_by(msg_id=message_id).first()
            if result is None:
                raise (NotFound(description="Message with msg_id '{0}' does not exist".format(message_id)))
        except SQLAlchemyError as e:
            logger.error(e)
            raise(InternalServerError(description="Error retrieving message from database"))

        message = result.serialize(user_urn)

        return message

    @staticmethod
    def retrieve_draft(message_id, user_urn):
        """returns single draft from db"""

        try:
            result = SecureMessage.query.filter(SecureMessage.msg_id == message_id)\
                .filter(SecureMessage.statuses.any(Status.label == Labels.DRAFT.value)).first()
            if result is None:
                raise (NotFound(description="Draft with msg_id '{0}' does not exist".format(message_id)))
        except SQLAlchemyError as e:
            logger.error(e)
            raise (InternalServerError(description="Error retrieving message from database"))

        message = result.serialize(user_urn)

        return message

    @staticmethod
    def check_db_connection():
        """checks if db connection is working"""
        database_status = {"status": "healthy", "errors": "none"}
        resp = jsonify(database_status)
        resp.status_code = 200

        try:
            SecureMessage().query.limit(1).all()
        except Exception as e:
            database_status['status'] = "unhealthy"
            database_status['errors'] = str(e)
            resp = jsonify(database_status)
            resp.status_code = 500

        return resp

    @staticmethod
    def check_msg_id_is_a_draft(draft_id, user_urn):
        """Check msg_id is that of a valid draft and return true/false if no ID is present"""
        try:
            result = SecureMessage.query.filter(SecureMessage.msg_id == draft_id)\
                .filter(SecureMessage.statuses.any(Status.label == Labels.DRAFT.value)).first()
        except Exception as e:
            logger.error(e)
            raise (InternalServerError(description="Error retrieving message from database"))

        if result is None:
            return False, result
        else:
            return True, result.serialize(user_urn)
