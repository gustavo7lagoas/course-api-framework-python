import pytest
import requests

from assertpy.assertpy import assert_that

from jsonpath_ng import parse
from json import dumps, loads
from config import BASE_URI
from utils.print_helpers import pretty_print
from uuid import uuid4
from utils.file_reader import read_file


@pytest.fixture
def create_data():
    payload = read_file('create_person.json')

    last_name = f'Olabini {str(uuid4())}'

    payload['lname'] = last_name
    yield payload


def test_list_all():
    all_users, response = get_users()

    all_person_fname = [person['fname'] for person in all_users]

    assert_that(response.status_code).is_equal_to(requests.codes.ok)
    assert_that(all_person_fname).contains('Kent')


def test_list_one():
    response = requests.get(f'{BASE_URI}/1')
    response_text = response.json()
    person = {'fname': 'Doug', 'lname': 'Farrell', 'person_id': 1}
    assert_that(response_text).is_equal_to(person, ignore='timestamp')


def test_create_person():
    unique_lname = create_unique_user()

    person = get_user_by_lname(unique_lname)

    assert_that(person).is_not_empty()


def test_delete_user():
    unique_lname = create_unique_user()
    person = get_user_by_lname(unique_lname)[0]

    response = requests.delete(f'{BASE_URI}/{person["person_id"]}')

    assert_that(response.status_code).is_equal_to(requests.codes.ok)
    assert_that(response.text).contains(f'Person with id {person["person_id"]} successfully deleted')


def test_create_user_from_file(create_data):
    unique_lname = create_unique_user(create_data)

    response = requests.get(BASE_URI)
    persons = loads(response.text)

    jsonpath_expr = parse("$.[*].lname")
    result = [match.value for match in jsonpath_expr.find(persons)]
    assert_that(result).contains(unique_lname)


def get_user_by_lname(unique_lname):
    all_users, _ = get_users()
    person = [person for person in all_users if person['lname'] == unique_lname]
    return person


def get_users():
    response = requests.get(BASE_URI)
    all_users = response.json()
    return all_users, response


def create_unique_user(body=None):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    if body:
        unique_lname = body["lname"]
        payload = dumps(body)
    else:
        unique_lname = f'User {str(uuid4())}'
        payload = dumps({
            "fname": "Test ",
            "lname": unique_lname
        })
    response = requests.post(BASE_URI, headers=headers, data=payload)
    assert_that(response.status_code).is_equal_to(requests.codes.no_content)

    return unique_lname
