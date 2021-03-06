import unittest
import requests_mock
import datetime
import json
import gazu

from gazu import client
from gazu.exception import (
    RouteNotFoundException,
    AuthFailedException,
    MethodNotAllowedException,
    NotAuthenticatedException,
    NotAllowedException,
)


class ClientTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass


class BaseFuncTestCase(ClientTestCase):
    def test_host_is_up(self):
        with requests_mock.mock() as mock:
            mock.head(client.get_host())
            self.assertTrue(client.host_is_up())

    def test_get_host(self):
        self.assertEqual(client.get_host(), client.HOST)

    def test_set_host(self):
        client.set_host("newhost")
        self.assertEqual(client.get_host(), "newhost")
        client.set_host("http://gazu-server/")

    def test_set_tokens(self):
        pass

    def test_make_auth_header(self):
        pass

    def test_url_path_join(self):
        root = client.get_host()
        items = ["data", "persons"]
        expected_url = "{host}data/persons".format(host=client.get_host())

        self.assertEqual(client.url_path_join(root, *items), expected_url)

    def test_get_full_url(self):
        test_route = "test_route"
        expected_url = client.url_path_join(client.get_host(), test_route)

        self.assertEqual(client.get_full_url(test_route), expected_url)

    def test_get(self):
        with requests_mock.mock() as mock:
            mock.get(
                client.get_full_url("data/persons"),
                text='{"first_name": "John"}',
            )
            self.assertEqual(client.get("data/persons"), {"first_name": "John"})

    def test_post(self):
        with requests_mock.mock() as mock:
            mock.post(
                client.get_full_url("data/persons"),
                text='{"id": "person-01", "first_name": "John"}',
            )
            self.assertEqual(
                client.post("data/persons", "person-01"),
                {"id": "person-01", "first_name": "John"},
            )

    def test_post_with_a_date_field(self):
        now = datetime.datetime.now()
        with requests_mock.mock() as mock:
            mock.post(
                client.get_full_url("data/persons"),
                text='{"id": "person-01", "first_name": "John"}',
            )
            self.assertEqual(
                client.post("data/persons", {"birth_date": now}),
                {"id": "person-01", "first_name": "John"},
            )

    def test_put(self):
        with requests_mock.mock() as mock:
            mock.put(
                client.get_full_url("data/persons"),
                text='{"id": "person-01", "first_name": "John"}',
            )
            self.assertEqual(
                client.put("data/persons", "person-01"),
                {"id": "person-01", "first_name": "John"},
            )

    def test_delete(self):
        with requests_mock.mock() as mock:
            mock.delete(client.get_full_url("data/persons/person-01"), text="")
            self.assertEqual(client.delete("data/persons/person-01"), "")

    def test_fetch_all(self):
        with requests_mock.mock() as mock:
            mock.get(
                client.get_full_url("data/persons"),
                text='[{"first_name": "John"}]',
            )
            self.assertEqual(
                client.fetch_all("persons"), [{"first_name": "John"}]
            )

    def test_fetch_first(self):
        with requests_mock.mock() as mock:
            mock.get(
                client.get_full_url("data/persons"),
                text=json.dumps(
                    [{"first_name": "John"}, {"first_name": "Jane"}]
                ),
            )
            self.assertEqual(
                client.fetch_first("persons"), {"first_name": "John"}
            )

            mock.get(client.get_full_url("data/persons"), text=json.dumps([]))
            self.assertIsNone(client.fetch_first("persons"))

    def test_query_string(self):
        with requests_mock.mock() as mock:
            mock.get(
                client.get_full_url("data/projects?name=Test"),
                text=json.dumps([{"name": "Project"}]),
            )
            self.assertEqual(
                client.fetch_first("projects", {"name": "Test"}),
                {"name": "Project"},
            )

            mock.get(client.get_full_url("data/persons"), text=json.dumps([]))
            self.assertIsNone(client.fetch_first("persons"))

    def test_fetch_one(self):
        with requests_mock.mock() as mock:
            mock.get(
                client.get_full_url("data/persons/person-01"),
                text='{"id": "person-01", "first_name": "John"}',
            )
            self.assertEqual(
                client.fetch_one("persons", "person-01"),
                {"id": "person-01", "first_name": "John"},
            )

    def test_create(self):
        with requests_mock.mock() as mock:
            mock.post(
                client.get_full_url("data/persons"),
                text='{"id": "person-01", "first_name": "John"}',
            )
            self.assertEqual(
                client.create("persons", {"first_name": "John"}),
                {"id": "person-01", "first_name": "John"},
            )

    def test_version(self):
        with requests_mock.mock() as mock:
            mock.get(client.get_host(), text='{"version": "0.2.0"}')
            self.assertEqual(client.get_api_version(), "0.2.0")

    def test_make_auth_token(self):
        tokens = {"access_token": "token_test"}
        client.set_tokens(tokens)
        self.assertEqual(
            client.make_auth_header(), {"Authorization": "Bearer token_test"}
        )

    def test_upload(self):
        pass

    def test_check_status(self):
        class Request(object):
            def __init__(self, status_code):
                self.status_code = status_code

        self.assertRaises(
            NotAuthenticatedException, client.check_status, Request(401), "/"
        )
        self.assertRaises(
            NotAllowedException, client.check_status, Request(403), "/"
        )
        self.assertRaises(
            RouteNotFoundException, client.check_status, Request(404), "/"
        )
        self.assertRaises(
            MethodNotAllowedException, client.check_status, Request(405), "/"
        )

    def test_init_host(self):
        gazu.set_host("newhost")
        self.assertEqual(gazu.get_host(), "newhost")
        gazu.set_host("http://gazu-server/")
        self.assertEqual(gazu.get_host(), gazu.client.HOST)

    def test_init_log_in(self):
        with requests_mock.mock() as mock:
            mock.post(
                client.get_full_url("auth/login"),
                text=json.dumps(
                    {"login": True, "tokens": {"access_token": "tokentest"}}
                ),
            )
            gazu.log_in("frank", "test")
        self.assertEqual(client.tokens["tokens"]["access_token"], "tokentest")

    def test_init_log_in_fail(self):
        with requests_mock.mock() as mock:
            mock.post(
                client.get_full_url("auth/login"),
                text=json.dumps({"login": False}),
            )
            self.assertRaises(AuthFailedException, gazu.log_in, "frank", "test")

    def test_get_current_user(self):
        with requests_mock.mock() as mock:
            mock.get(
                client.get_full_url("auth/authenticated"),
                text=json.dumps({"user": {"id": "123"}}),
            )
            current_user = client.get_current_user()
            self.assertEqual(current_user["id"], "123")
