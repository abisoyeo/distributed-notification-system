# Template microservice

This microservice is responsible for creating and storing templates for the email and push notification service, it stores the templates in a postgre sql database and renders it as a Jinja2 template, where placeholders can be replaced with actual values passed in.

# Setup instructions

- visit [text](https://docs.astral.sh/uv/getting-started/installation/) for instructions to install uv

- After installing uv, install the requirements using this command.

``` bash
uv sync

```

- Set the POSTGRE_DATABASE_URL environment variable in a dotenv file in the root director of your project.

``` python
POSTGRE_DATABASE_URL=somepostgreurl

```

- The run the application using uvicorn

``` bash
uvicorn main:app

```

- After running the application, you will be provided with a URL if you follow the instructions correctly.

For more instructions regarding the use of the application, visit the docs at ([text]{applicationurl}/docs) or [text](https://localhost:port/docs)