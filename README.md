# Client Import API (Django + DRF)

Microservicio para importar clientes desde Excel, validarlos y guardarlos en SQLite.

## Requisitos

- Python 3.10+
- pip

## Instalacion y ejecucion local

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Endpoints requeridos

- `POST /clients/import`
  - `multipart/form-data`, campo `file`
  - espera un `.xlsx` con hoja `Clientes`
- `GET /clients`
- `GET /clients/{id}`
- `PUT /clients/{id}`
- `DELETE /clients/{id}`

## Formato esperado del Excel

Hoja: `Clientes`  
Columnas exactas y en este orden:

1. `customer_id` (entero, obligatorio, unico)
2. `name` (string, obligatorio)
3. `email` (string, obligatorio, email valido)
4. `country` (string, obligatorio)
5. `age` (entero, opcional, >= 18)

## Respuesta de importacion

```json
{
  "summary": {
    "total_records": 10,
    "inserted": 8,
    "errors": 2
  },
  "error_details": [
    {
      "customer_id": 5,
      "errors": ["Invalid email format"]
    }
  ]
}
```

## Tests

```bash
python manage.py test
```

