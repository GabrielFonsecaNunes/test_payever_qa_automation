This is a Project reference about payever test QA Automation

# FastAPI REST Application

This is a simple Python REST application built with FastAPI. It communicates with the ReqRes.in API and uses SQLite as the database.

## Prerequisites

- Python 3.9 and above
- Uvicorn 0.21.0 and above
- FastAPI framework
- SQLite
- Docker & Docker Compose

## Installation

1. Clone the repository:

   ```shell
   https://github.com/GabrielFonsecaNunes/test_payever_qa_automation.git
   ```

2. Change to the project directory:

   ```shell
   cd test_payever_qa_automation
   ```

3. Install the required packages:

   ```shell
   pip install -r requirements.txt
   ```

## Usage

1. Start the application using Docker Compose:

   ```shell
   docker-compose up
   ```

   The API will be accessible at `http://localhost:8000`.

2. Use the following endpoints:

   - `POST /api/users`: Creates a new user in the SQLite database and makes a request to `https://reqres.in/api/users`. The user entry is stored in SQLite, and the response from ReqRes.in is returned.
   - `GET /api/user/{userId}`: Retrieves user data from `https://reqres.in/api/users/{userId}` and returns the user in JSON representation.
   - `DELETE /api/user/{userId}`: Deletes a user entry from the SQLite database and makes a request to `https://reqres.in/api/users/{userId}`.

## Testing

The project includes unit tests for the API endpoints. To run the tests, execute the following command:

```shell
python test_app.py
```

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvement, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

---

Feel free to customize the README.md file according to your project's specific details, such as repository URLs, project structure, and additional information.