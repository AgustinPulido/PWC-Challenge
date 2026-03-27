from django.urls import path

from .views import ClientDetailView, ClientImportView, ClientListView

urlpatterns = [
    path("clients/import", ClientImportView.as_view(), name="clients-import"),
    path("clients", ClientListView.as_view(), name="clients-list"),
    path("clients/<int:customer_id>", ClientDetailView.as_view(), name="clients-detail"),
]

