from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .models import Client


class ClientRepository(Protocol):
    def list_clients(self) -> "list[Client]": ...

    def get_client(self, *, customer_id: int) -> Client: ...

    def create_client(
        self,
        *,
        customer_id: int,
        name: str,
        email: str,
        country: str,
        age: int | None,
    ) -> Client: ...

    def update_client(
        self,
        *,
        customer_id: int,
        name: str,
        email: str,
        country: str,
        age: int | None,
    ) -> Client: ...

    def delete_client(self, *, customer_id: int) -> None: ...

    def customer_id_exists(self, *, customer_id: int) -> bool: ...


@dataclass(frozen=True)
class DjangoORMClientRepository:
    def list_clients(self) -> list[Client]:
        return list(Client.objects.all().order_by("customer_id"))

    def get_client(self, *, customer_id: int) -> Client:
        return Client.objects.get(customer_id=customer_id)

    def create_client(
        self,
        *,
        customer_id: int,
        name: str,
        email: str,
        country: str,
        age: int | None,
    ) -> Client:
        return Client.objects.create(
            customer_id=customer_id,
            name=name,
            email=email,
            country=country,
            age=age,
        )

    def update_client(
        self,
        *,
        customer_id: int,
        name: str,
        email: str,
        country: str,
        age: int | None,
    ) -> Client:
        client = self.get_client(customer_id=customer_id)
        client.name = name
        client.email = email
        client.country = country
        client.age = age
        client.save(update_fields=["name", "email", "country", "age", "updated_at"])
        return client

    def delete_client(self, *, customer_id: int) -> None:
        client = self.get_client(customer_id=customer_id)
        client.delete()

    def customer_id_exists(self, *, customer_id: int) -> bool:
        return Client.objects.filter(customer_id=customer_id).exists()

