import json
import os

import requests

from dotenv import load_dotenv
from lorem_text import lorem

from definitions import ROOT_DIR
from utils.tools import write_to_file, read_from_file

load_dotenv()
BASE_URL = os.getenv("BASE_URL")
data_file = f'{ROOT_DIR}/utils/token.json'


class TestBookstoreAPI:

    def test_request_status(self) -> None:
        response = requests.get(url=BASE_URL)
        assert response.status_code == 200
        response_content = json.loads(response.content)
        response_time = response.elapsed.total_seconds()
        assert response_content["message"] == "Welcome to the Simple Books API."
        assert response_time <= 1.5, f"The response time {response_time}sec > 1sec"

    def test_request_list_of_all_books(self) -> None:
        display_limit = 10
        response = requests.get(url=f"{BASE_URL}/books?limit={display_limit}")
        assert response.status_code == 200
        response_content = json.loads(response.content)
        assert type(response_content) is list and response_content is not []
        for book in response_content:
            assert type(book) is dict
            assert type(book['id']) is int
            assert type(book['name']) is str
            assert type(book['type']) is str
            assert type(book['available']) is bool

    def test_request_list_of_non_fiction_books(self) -> None:
        books_type = "non-fiction"  # accepted values "fiction" and "non-fiction"
        display_limit = 10
        response = requests.get(url=f"{BASE_URL}/books?type={books_type}&limit={display_limit}")
        assert response.status_code == 200
        response_content = json.loads(response.content)
        assert type(response_content) is list and response_content is not []
        for book in response_content:
            assert type(book['id']) is int
            assert type(book['name']) is str
            assert book['type'] == 'non-fiction'
            assert type(book['available']) is bool

    def test_request_list_of_fiction_books(self) -> None:
        books_type = "fiction" # accepted values "fiction" and "non-fiction"
        display_limit = 10
        response = requests.get(url=f"{BASE_URL}/books?type={books_type}&limit={display_limit}")
        assert response.status_code == 200
        response_content = json.loads(response.content)
        assert type(response_content) is list and response_content is not []
        for book in response_content:
            assert type(book['id']) is int
            assert type(book['name']) is str
            assert book['type'] == 'fiction'
            assert type(book['available']) is bool

    def test_request_non_existent_book_type(self) -> None:
        books_type = "sport"
        display_limit = 10
        response = requests.get(url=f"{BASE_URL}/books?type={books_type}&limit={display_limit}")
        assert response.status_code == 400
        response_content = json.loads(response.content)
        assert response_content["error"] == \
               "Invalid value for query parameter 'type'. Must be one of: fiction, non-fiction."

    def test_request_single_book(self) -> None:
        response = requests.get(url=f"{BASE_URL}/books/1")
        response_content = json.loads(response.content)
        assert response_content is not {}
        assert response_content['id'] == 1
        assert response_content['name'] == 'The Russian'
        assert response_content['author'] == 'James Patterson and James O. Born'
        assert response_content['type'] == 'fiction'
        assert response_content['price'] == 12.98
        assert response_content['current-stock'] is not 0
        assert response_content['available'] is True

    def test_request_non_existent_book(self) -> None:
        book_id = 999
        response = requests.get(url=f"{BASE_URL}/books/{book_id}")
        assert response.status_code == 404
        response_content = json.loads(response.content)
        assert response_content["error"] == f"No book with id {book_id}"

    def test_register_new_user(self) -> None:
        body = {
            "clientName": lorem.words(2),
            "clientEmail": f"{lorem.words(1)}@gmail.com"
        }
        response = requests.post(url=f"{BASE_URL}/api-clients", json=body)
        assert response.status_code == 201
        response_content = json.loads(response.content)
        write_to_file(data_file, "customer_name", body["clientName"])
        write_to_file(data_file, "access_token", response_content["accessToken"])

    def test_submit_new_book_order(self) -> None:
        token = read_from_file(data_file, "access_token")
        book_id = 1
        body = {
            "bookId": book_id,
            "customerName": read_from_file(data_file, "customer_name")
        }
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.post(url=f"{BASE_URL}/orders", json=body, headers=headers)
        assert response.status_code == 201
        response_content = json.loads(response.content)
        assert response_content["created"] is True
        assert response_content["orderId"] is not None
        write_to_file(data_file, "order_id", response_content["orderId"])

    def test_submit_unauthorised_order(self) -> None:
        book_id = 1
        body = {
            "bookId": book_id,
            "customerName": read_from_file(data_file, "customer_name")
        }
        response = requests.post(url=f"{BASE_URL}/orders", json=body)
        assert response.status_code == 401
        response_content = json.loads(response.content)
        assert response_content["error"] == "Missing Authorization header."

    def test_submit_order_with_invalid_or_non_existent_id(self) -> None:
        token = read_from_file(data_file, "access_token")
        book_id = "asd"
        body = {
            "bookId": book_id,
            "customerName": read_from_file(data_file, "customer_name")
        }
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.post(url=f"{BASE_URL}/orders", json=body, headers=headers)
        assert response.status_code == 400
        response_content = json.loads(response.content)
        assert response_content["error"] == "Invalid or missing bookId."

    def test_request_all_book_orders(self) -> None:
        token = read_from_file(data_file, "access_token")
        customer_name = read_from_file(data_file, "customer_name")
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.get(url=f"{BASE_URL}/orders", headers=headers)
        assert response.status_code == 200
        response_content = json.loads(response.content)
        for order in response_content:
            assert type(order['id']) is str
            assert type(order['bookId']) is int
            assert order['customerName'] == customer_name
            assert type(order['createdBy']) is str
            assert type(order['quantity']) is int
            assert type(order['timestamp']) is int

    def test_unauthorised_request_all_book_orders(self) -> None:
        response = requests.get(url=f"{BASE_URL}/orders")
        assert response.status_code == 401
        response_content = json.loads(response.content)
        assert response_content["error"] == "Missing Authorization header."

    def test_request_order_by_id(self) -> None:
        token = read_from_file(data_file, "access_token")
        customer_name = read_from_file(data_file, "customer_name")
        order_id = read_from_file(data_file, "order_id")
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.get(url=f"{BASE_URL}/orders/{order_id}", headers=headers)
        assert response.status_code == 200
        response_content = json.loads(response.content)
        assert type(response_content['id']) is str
        assert type(response_content['bookId']) is int
        assert response_content['customerName'] == customer_name
        assert type(response_content['createdBy']) is str
        assert type(response_content['quantity']) is int
        assert type(response_content['timestamp']) is int

    def test_unauthorised_request_order_by_id(self) -> None:
        order_id = read_from_file(data_file, "order_id")
        response = requests.get(url=f"{BASE_URL}/orders/{order_id}")
        assert response.status_code == 401
        response_content = json.loads(response.content)
        assert response_content["error"] == "Missing Authorization header."

    def test_request_order_by_invalid_id(self) -> None:
        order_id = "qwert123"
        token = read_from_file(data_file, "access_token")
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.get(url=f"{BASE_URL}/orders/{order_id}", headers=headers)
        assert response.status_code == 404
        response_content = json.loads(response.content)
        assert response_content["error"] == f"No order with id {order_id}."

    def test_updating_existing_order(self) -> None:
        token = read_from_file(data_file, "access_token")
        new_customer_name = "new_customer_name"
        order_id = read_from_file(data_file, "order_id")
        headers = {
            "Authorization": f"Bearer {token}"
        }
        body = {
            "customerName": new_customer_name
        }
        response = requests.patch(url=f"{BASE_URL}/orders/{order_id}", json=body, headers=headers)
        assert response.status_code == 204
        response = requests.get(url=f"{BASE_URL}/orders/{order_id}", headers=headers)
        response_content = json.loads(response.content)
        assert response.status_code == 200
        assert response_content['customerName'] == new_customer_name

    def test_unauthorized_updating_existing_order(self) -> None:
        new_customer_name = "new_customer_name"
        order_id = read_from_file(data_file, "order_id")
        body = {
            "customerName": new_customer_name
        }
        response = requests.patch(url=f"{BASE_URL}/orders/{order_id}", json=body)
        assert response.status_code == 401
        response_content = json.loads(response.content)
        assert response_content["error"] == "Missing Authorization header."

    def test_updating_invalid_order(self) -> None:
        token = read_from_file(data_file, "access_token")
        new_customer_name = "new_customer_name"
        order_id = 'abc'
        headers = {
            "Authorization": f"Bearer {token}"
        }
        body = {
            "customerName": new_customer_name
        }
        response = requests.patch(url=f"{BASE_URL}/orders/{order_id}", json=body, headers=headers)
        assert response.status_code == 404
        response_content = json.loads(response.content)
        assert response_content["error"] == f"No order with id {order_id}."

    def test_delete_existing_order(self) -> None:
        token = read_from_file(data_file, "access_token")
        order_id = read_from_file(data_file, "order_id")
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.delete(url=f"{BASE_URL}/orders/{order_id}", headers=headers)
        assert response.status_code == 204
        response = requests.get(url=f"{BASE_URL}/orders/{order_id}", headers=headers)
        assert response.status_code == 404
        response_content = json.loads(response.content)
        assert response_content["error"] == f"No order with id {order_id}."
