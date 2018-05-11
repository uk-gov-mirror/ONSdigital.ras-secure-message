import logging

from flask import g, jsonify, request
from flask_restful import Resource
from structlog import wrap_logger

from secure_message.common.utilities import get_options, process_paginated_list, add_users_and_business_details
from secure_message.constants import THREAD_LIST_ENDPOINT
from secure_message.repository.retriever import Retriever

logger = wrap_logger(logging.getLogger(__name__))


class ThreadById(Resource):
    """Return list of messages in a thread for user"""

    @staticmethod
    def get(thread_id):
        """Get messages by thread id"""
        logger.info("Getting messages from thread", thread_id=thread_id, user_uuid=g.user.user_uuid)

        conversation = Retriever().retrieve_thread(thread_id, g.user)

        logger.info("Successfully retrieved messages from thread", thread_id=thread_id, user_uuid=g.user.user_uuid)
        messages = []
        for message in conversation.all():
            msg = message.serialize(g.user, body_summary=False)
            messages.append(msg)
        return jsonify({"messages": add_users_and_business_details(messages)})

    def patch(thread_id):
        """Modify every message in a thread with a status"""

        # TODO, will probably change, but validating upfront (permissions, label, etc) here is
        # a good idea
        request_data = request.get_json()
        action, label = MessageModifyById._validate_request(request_data)

        logger.info("Getting messages from thread", thread_id=thread_id, user_uuid=g.user.user_uuid)
        conversation = Retriever().retrieve_thread(thread_id, g.user)
        # Need new function to update them all at once, so we can roll back all at once
        response = Modifier.add_label_to_all_messages_in_thread(conversation, user, action, label)

        if resp:
            logger.info("Thread label update successful", thread_id=thread_id, user_uuid=g.user.user_uuid)
            return ('', 204)
        else:
            logger.error('Error updating message', msg_id=message_id, status_code=400)
            abort(400)
        return res

    @staticmethod
    def _validate_request(request_data):
        """Used to validate data within request body for ModifyById"""
        if not g.user.is_internal:
            logger.info("Thread modification is forbidden")
            abort(403)
        if 'label' not in request_data:
            logger.error('No label provided')
            raise BadRequest(description="No label provided")
        if request_data['label'] not in ['CLOSED']:
            logger.error('Invalid label provided')
            raise BadRequest(description="Invalid label provided")
        if 'action' not in request_data:
            logger.error('No action provided')
            raise BadRequest(description="No action provided")
        if request_data['action'] not in ['ADD', 'REMOVE']:
            logger.error('Invalid action provided')
            raise BadRequest(description="Invalid action provided")


class ThreadList(Resource):
    """Return a list of threads for the user"""

    @staticmethod
    def get():
        """Get thread list"""
        logger.info("Getting list of threads for user", user_uuid=g.user.user_uuid)
        message_args = get_options(request.args)
        result = Retriever().retrieve_thread_list(g.user, message_args)

        logger.info("Successfully retrieved threads for user", user_uuid=g.user.user_uuid)
        messages, links = process_paginated_list(result, request.host_url, g.user, message_args, THREAD_LIST_ENDPOINT)
        messages = add_users_and_business_details(messages)
        return jsonify({"messages": messages, "_links": links})
