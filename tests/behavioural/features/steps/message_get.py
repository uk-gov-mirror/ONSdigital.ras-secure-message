import flask
from flask import json
import nose.tools
from behave import given, then, when
from app.application import app
import uuid
from app.authentication.jwt import encode
from app.authentication.jwe import Encrypter
from app import settings

url = "http://localhost:5050/message/"
token_data = {
            "user_urn": "000000000"
        }

headers = {'Content-Type': 'application/json', 'authentication': ''}

data = {'urn_to': 'test',
        'urn_from': 'test',
        'subject': 'Hello World',
        'body': 'Test',
        'thread_id': '',
        'collection_case': 'collection case1',
        'reporting_unit': 'reporting case1',
        'survey': 'survey'}


def update_encrypted_jwt():
    encrypter = Encrypter(_private_key=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY,
                          _private_key_password=settings.SM_USER_AUTHENTICATION_PRIVATE_KEY_PASSWORD,
                          _public_key=settings.SM_USER_AUTHENTICATION_PUBLIC_KEY)
    signed_jwt = encode(token_data)
    return encrypter.encrypt_token(signed_jwt)

headers['authentication'] = update_encrypted_jwt()


# Scenario: Retrieve a message with correct message ID
@given("there is a message to be retrieved")
def step_impl(context):
    data['urn_to'] = 'internal.12344'
    data['urn_from'] = 'respondent.122342'
    context.response = app.test_client().post("http://localhost:5050/message/send", data=flask.json.dumps(data),
                                              headers=headers)
    msg_resp = json.loads(context.response.data)
    context.msg_id = msg_resp['msg_id']


@when("the get request is made with a correct message id")
def step_impl(context):
    new_url = url+context.msg_id
    context.response = app.test_client().get(new_url, headers=headers)


@then("a 200 HTTP response is returned")
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 200)


# Scenario: Retrieve a message with incorrect message ID
@when("the get request has been made with an incorrect message id")
def step_impl(context):
    new_url = url+str(uuid.uuid4())
    context.response = app.test_client().get(new_url, headers=headers)


@then("a 404 HTTP response is returned")
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 404)


# Scenario: Respondent sends message and retrieves the same message with it's labels
@given("a respondent sends a message")
def step_impl(context):
    data['urn_to'] = 'internal.12344'
    data['urn_from'] = 'respondent.122342'
    context.response = app.test_client().post("http://localhost:5050/message/send",
                                                          data=flask.json.dumps(data), headers=headers)
    msg_resp = json.loads(context.response.data)
    context.msg_id = msg_resp['msg_id']


@when("the respondent wants to see the message")
def step_impl(context):
    token_data['user_urn'] = 'respondent.122342'
    headers['authentication'] = update_encrypted_jwt()
    new_url = url+context.msg_id
    context.response = app.test_client().get(new_url, headers=headers)


@then("the retrieved message should have the label SENT")
def step_impl(context):
    response = flask.json.loads(context.response.data)
    nose.tools.assert_equal(response['labels'], ['SENT'])


# Scenario: Internal user sends message and retrieves the same message with it's labels
@given("an internal user sends a message")
def step_impl(context):
    data['urn_to'] = 'respondent.122342'
    data['urn_from'] = 'internal.12344'
    context.response = app.test_client().post("http://localhost:5050/message/send",
                                                          data=flask.json.dumps(data), headers=headers)
    msg_resp = json.loads(context.response.data)
    context.msg_id = msg_resp['msg_id']


@when("the internal user wants to see the message")
def step_impl(context):
    token_data['user_urn'] = 'internal.12344'
    headers['authentication'] = update_encrypted_jwt()
    new_url = url+context.msg_id
    context.response = app.test_client().get(new_url, headers=headers)


#  Scenario: Internal user sends message and respondent retrieves the same message with it's labels
@then("the retrieved message should have the labels INBOX and UNREAD")
def step_impl(context):
    response = flask.json.loads(context.response.data)
    nose.tools.assert_true(len(response['labels']), 2)
    nose.tools.assert_true('INBOX' in response['labels'])
    nose.tools.assert_true('UNREAD' in response['labels'])
