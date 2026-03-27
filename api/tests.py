from io import BytesIO

from django.test import TestCase
from openpyxl import Workbook
from rest_framework.test import APIClient

from .models import Client


def build_excel(rows: list[list[object]]) -> BytesIO:
    wb = Workbook()
    ws = wb.active
    ws.title = "Clientes"
    ws.append(["customer_id", "name", "email", "country", "age"])
    for row in rows:
        ws.append(row)
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    output.name = "clientes.xlsx"
    return output


class ClientApiTests(TestCase):
    def setUp(self):
        self.api = APIClient()

    def test_import_clients_returns_summary_and_errors(self):
        payload = build_excel(
            [
                [1, "Alice", "alice@example.com", "AR", 20],
                [2, "", "invalid-email", "AR", 17],
            ]
        )
        response = self.api.post("/clients/import", {"file": payload}, format="multipart")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["summary"]["total_records"], 2)
        self.assertEqual(response.data["summary"]["inserted"], 1)
        self.assertEqual(response.data["summary"]["errors"], 1)
        self.assertEqual(Client.objects.count(), 1)

    def test_crud_clients(self):
        Client.objects.create(
            customer_id=10,
            name="Bob",
            email="bob@example.com",
            country="UY",
            age=30,
        )

        list_response = self.api.get("/clients")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.data), 1)

        get_response = self.api.get("/clients/10")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.data["name"], "Bob")

        put_response = self.api.put(
            "/clients/10",
            {
                "customer_id": 10,
                "name": "Bobby",
                "email": "bobby@example.com",
                "country": "UY",
                "age": 31,
            },
            format="json",
        )
        self.assertEqual(put_response.status_code, 200)
        self.assertEqual(put_response.data["name"], "Bobby")

        delete_response = self.api.delete("/clients/10")
        self.assertEqual(delete_response.status_code, 204)
        self.assertEqual(Client.objects.count(), 0)
