import requests
from assertpy import assert_that, soft_assertions

from cerberus import Validator
from config import BASE_URI
from json import loads

schema = {
    "fname": {"type": "string"},
    "lname": {"type": "string"},
    "person_id": {"type": "integer"},
    "timestamp": {"type": "string"}
}


def test_read_one_operation_has_expected_schema():
    response = requests.get(f'{BASE_URI}/1')
    person = loads(response.text)

    validator = Validator(schema, required=True)
    is_valid = validator.validate(person)

    assert_that(is_valid, description=validator.errors).is_true()


def test_read_all_has_expected_schema():
    response = requests.get(f'{BASE_URI}')
    all_person = loads(response.text)

    validator = Validator(schema, required=True)

    with soft_assertions():
        for person in all_person:
            is_valid = validator.validate(person)
            assert_that(is_valid, description=validator.errors).is_true()
