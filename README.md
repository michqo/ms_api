# MS API Project
This project is a Django REST Framework application designed to provide a robust and scalable API.

## Features

- Django REST Framework for API development
- Token-based authentication
- CRUD operations for various models

## Requirements

- Python 3.x
- Django 3.x
- Django REST Framework
- Poetry

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/michqo/ms_api.git
    cd ms_api
    ```

2. Install Poetry:
    ```bash
    pipx install poetry
    ```

3. Install the dependencies:
    ```bash
    poetry install
    ```

4. Apply migrations:
    ```bash
    poetry run python manage.py migrate
    ```

5. Run the development server:
    ```bash
    poetry run python manage.py runserver
    ```

## Usage

To use the API, navigate to `http://127.0.0.1:8000/` in your web browser or use a tool like Postman to interact with the endpoints.

### Swagger Documentation

You can also explore the API using the built-in Swagger documentation. Navigate to `http://127.0.0.1:8000/api/schema/swagger-ui/` in your web browser to view and interact with the API documentation.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
