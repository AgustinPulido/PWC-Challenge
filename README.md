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

## Ejecucion con Docker

### Build de la imagen

```bash
docker build -t client-import-api .
```

### Ejecutar el contenedor

```bash
docker run --rm -p 8000:8000 client-import-api sh -c "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"
```

La API quedara disponible en `http://localhost:8000`.

### Persistir SQLite entre ejecuciones (opcional)

Si quieres mantener la base de datos entre reinicios, monta un volumen en `/app/db.sqlite3`:

```bash
docker run --rm -p 8000:8000 -v ${PWD}/db.sqlite3:/app/db.sqlite3 client-import-api sh -c "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"
```

Sin volumen, la base SQLite se pierde cuando termina el contenedor.

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

