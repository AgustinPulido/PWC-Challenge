from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.core.validators import validate_email
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from rest_framework.exceptions import NotFound

from .models import Client
from .repositories import ClientRepository


@dataclass(frozen=True)
class ClientService:
    repo: ClientRepository

    EXPECTED_COLUMNS = ["customer_id", "name", "email", "country", "age"]

    def list_clients(self) -> list[Client]:
        return self.repo.list_clients()

    def get_client(self, *, customer_id: int) -> Client:
        try:
            return self.repo.get_client(customer_id=customer_id)
        except ObjectDoesNotExist as exc:
            raise NotFound(detail="Client not found") from exc

    def update_client(
        self,
        *,
        customer_id: int,
        name: str,
        email: str,
        country: str,
        age: int | None,
    ) -> Client:
        self.get_client(customer_id=customer_id)
        return self.repo.update_client(
            customer_id=customer_id,
            name=name,
            email=email,
            country=country,
            age=age,
        )

    def delete_client(self, *, customer_id: int) -> None:
        self.get_client(customer_id=customer_id)
        self.repo.delete_client(customer_id=customer_id)

    def import_clients(self, *, rows: list[dict[str, Any]], columns: list[str]) -> dict[str, Any]:
        if columns != self.EXPECTED_COLUMNS:
            return {
                "summary": {"total_records": 0, "inserted": 0, "errors": 1},
                "error_details": [
                    {
                        "customer_id": None,
                        "errors": [
                            f"Invalid columns. Expected exactly: {', '.join(self.EXPECTED_COLUMNS)}"
                        ],
                    }
                ],
            }

        file_customer_ids: set[int] = set()
        inserted = 0
        error_details: list[dict[str, Any]] = []

        for row in rows:
            customer_id = row.get("customer_id")
            row_errors: list[str] = []

            try:
                customer_id = int(customer_id)
            except (TypeError, ValueError):
                row_errors.append("customer_id must be an integer")

            name = (row.get("name") or "").strip()
            if not name:
                row_errors.append("Name cannot be empty")

            email = (row.get("email") or "").strip()
            if not email:
                row_errors.append("Email is required")
            else:
                try:
                    validate_email(email)
                except DjangoValidationError:
                    row_errors.append("Invalid email format")

            country = (row.get("country") or "").strip()
            if not country:
                row_errors.append("Country is required")

            age_raw = row.get("age")
            age: int | None = None
            if age_raw not in (None, ""):
                try:
                    age = int(age_raw)
                    if age < 18:
                        row_errors.append("Age must be greater than or equal to 18")
                except (TypeError, ValueError):
                    row_errors.append("Age must be an integer")

            if isinstance(customer_id, int):
                if customer_id in file_customer_ids:
                    row_errors.append("Duplicated customer_id in file")
                elif self.repo.customer_id_exists(customer_id=customer_id):
                    row_errors.append("customer_id already exists in database")
                else:
                    file_customer_ids.add(customer_id)

            if row_errors:
                error_details.append({"customer_id": customer_id, "errors": row_errors})
                continue

            try:
                self.repo.create_client(
                    customer_id=customer_id,
                    name=name,
                    email=email,
                    country=country,
                    age=age,
                )
                inserted += 1
            except IntegrityError:
                # Handles race conditions where another request inserted the same ID.
                error_details.append(
                    {
                        "customer_id": customer_id,
                        "errors": ["customer_id already exists in database"],
                    }
                )

        total = len(rows)
        return {
            "summary": {
                "total_records": total,
                "inserted": inserted,
                "errors": total - inserted,
            },
            "error_details": error_details,
        }

