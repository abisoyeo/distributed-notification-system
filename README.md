# Distributed Notification System API

## Overview
A robust and scalable microservices-based system designed for managing and delivering various types of notifications, including email and push notifications. The architecture leverages NestJS (TypeScript) and FastAPI (Python) for service development, RabbitMQ for asynchronous message queuing, PostgreSQL for persistent data storage, and Redis for caching and idempotency, all orchestrated via Docker Compose.

## Features
- **Microservices Architecture**: Decoupled services for enhanced modularity, scalability, and maintainability.
- **Asynchronous Notification Delivery**: Utilizes RabbitMQ for reliable and fault-tolerant message queuing for email and push notifications.
- **Idempotent Processing**: Implements mechanisms in the Push Service to ensure messages are processed exactly once, preventing duplicate notifications.
- **Centralized Template Management**: A dedicated service for creating, storing, and rendering dynamic notification content using Jinja2 templates.
- **User Management & Preferences**: Includes a user service with authentication, user registration, and notification preference settings (email, push, SMS).
- **Circuit Breaker Pattern**: The Email Service incorporates a circuit breaker for resilient communication with external template fetching, enhancing stability.
- **Dockerized Deployment**: Simplifies local development and production deployment through containerization with Docker Compose.
- **Comprehensive API Gateway**: A central entry point for external clients to interact with the notification system, handling routing and initial request processing.

## Getting Started
### Installation
To set up and run the Distributed Notification System locally, follow these steps:

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/distributed-notification-system.git
    cd distributed-notification-system
    ```

2.  **Build and run services with Docker Compose**:
    Ensure Docker and Docker Compose are installed on your system.
    ```bash
    docker-compose up --build -d
    ```
    This command will build the Docker images for all services (gateway, user-service, email-service, push-service, template-service) and start them along with RabbitMQ, PostgreSQL, and Redis.

3.  **Verify service status**:
    You can check the status of running containers:
    ```bash
    docker-compose ps
    ```
    All services should show as `Up`.

### Environment Variables
The following environment variables are required for the services to function correctly. These are primarily configured within the `docker-compose.yml` file, but some can be overridden or supplemented by `.env` files within individual service directories.

| Variable Name                       | Service(s)                | Description                                                          | Example Value                                  |
| :---------------------------------- | :------------------------ | :------------------------------------------------------------------- | :--------------------------------------------- |
| `RABBITMQ_URL`                      | Gateway, Email, Push      | Connection string for RabbitMQ.                                      | `amqp://admin:admin123@rabbitmq:5672`          |
| `REDIS_HOST`                        | Gateway                   | Hostname for the Redis server.                                       | `redis`                                        |
| `REDIS_PORT`                        | Gateway                   | Port for the Redis server.                                           | `6379`                                         |
| `DATABASE_URL`                      | User, Template            | PostgreSQL connection string.                                        | `postgresql://user:pass@postgres/userdb`       |
| `SECRET_KEY`                        | User                      | Django secret key for security.                                      | `django-insecure-j$)4+l#5h=jy6k2c$x*pwv+#...`   |
| `DEBUG`                             | User                      | Django debug mode (True/False).                                      | `True`                                         |
| `ALLOWED_HOSTS`                     | User                      | Comma-separated list of allowed hosts for Django.                    | `localhost,127.0.0.1`                          |
| `USE_POSTGRES`                      | User                      | Enable PostgreSQL backend for Django (True/False).                   | `True`                                         |
| `TEMPLATE_SERVICE_URL`              | Email, Push               | URL of the Template Service.                                         | `http://template-service:8000`                 |
| `EMAIL_QUEUE`                       | Email                     | Name of the RabbitMQ queue for email messages.                       | `email.queue`                                  |
| `DLX_EXCHANGE`                      | Email                     | Name of the Dead Letter Exchange.                                    | `dlx.exchange`                                 |
| `FAILED_QUEUE`                      | Email                     | Name of the queue for permanently failed messages.                   | `email.failed`                                 |
| `MAX_RETRIES`                       | Email                     | Maximum number of retries for email messages.                        | `3`                                            |
| `SENDER_EMAIL`                      | Email                     | Sender email address for notifications.                              | `notifications@example.com`                    |
| `SMTP_HOST`                         | Email                     | SMTP server host for sending emails.                                 | `smtp.ethereal.email`                          |
| `SMTP_PORT`                         | Email                     | SMTP server port.                                                    | `587`                                          |
| `SMTP_USER`                         | Email                     | SMTP username.                                                       | `test_smtp_username`                           |
| `SMTP_PASS`                         | Email                     | SMTP password.                                                       | `test_smtp_password`                           |
| `GOOGLE_APPLICATION_CREDENTIALS`    | Push                      | JSON string of Google Service Account credentials for FCM.           | `{ "type": "service_account", ... }`           |
| `REDIS_URL`                         | Push                      | Redis connection URL for idempotency.                                | `redis://redis:6379/0`                         |
| `USER_SERVICE_URL`                  | Gateway                   | URL of the User Service (internal to Docker network).                | `http://user-service:8001`                     |
| `POSTGRE_DATABASE_URL`              | Template                  | PostgreSQL connection string for the Template service.               | `postgresql://user:pass@postgres/userdb`       |
| `PORT`                              | Gateway (optional)        | Port for the Gateway service to listen on.                           | `3000`                                         |

## API Documentation

The Distributed Notification System exposes several APIs through its microservices. Below is the detailed documentation for each service's endpoints.

### Gateway API
The Gateway service acts as the primary entry point for external clients, routing requests to appropriate downstream services and handling notification dispatch.

#### Base URL
`/api`

#### Endpoints

#### `POST /api/notifications/send-notification`
Initiates the sending of a notification (email or push) to a specified user.

**Request**:
```json
{
  "notification_type": "email" | "push",
  "user_id": "uuid",
  "template_code": "string",
  "variables": {
    "name": "string",
    "link": "string",
    "meta?": {}
  },
  "request_id": "string",
  "priority?": "integer",
  "metadata?": {}
}
```

**Response**:
```json
{
  "request_id": "string",
  "status": "pending",
  "type": "email" | "push",
  "user": "uuid",
  "result": {
    "success": true,
    "routingKey": "string"
  }
}
```

**Errors**:
- `400 Bad Request`: Invalid notification type or missing required fields.
- `404 Not Found`: User or template not found (if upstream validation is enabled).
- `500 Internal Server Error`: General server error or failure to process notification.

#### `POST /api/notifications/:notificationId/status`
Updates the status of a specific notification. This endpoint is primarily for internal communication between worker services and the gateway.

**Request**:
```json
{
  "notificationId": "string",
  "channel": "string",
  "status": "string",
  "messageId?": "string",
  "errorMessage?": "string"
}
```

**Response**:
```json
{
  "success": true,
  "result": {
    "notificationId": "string",
    "channel": "string",
    "status": "string",
    "messageId?": "string",
    "errorMessage?": "string",
    "createdAt": "date-time"
  }
}
```

**Errors**:
- `400 Bad Request`: Invalid input data.
- `500 Internal Server Error`: Failure to update status in the repository.

#### `GET /api/notifications/:notificationId/statuses`
Retrieves the current status of a specific notification.

**Request**:
(Path parameter `notificationId`)

**Response**:
```json
{
  "success": true,
  "statuses": {
    "notificationId": "string",
    "channel": "string",
    "status": "string",
    "messageId?": "string",
    "errorMessage?": "string",
    "createdAt": "date-time"
  }
}
```

**Errors**:
- `404 Not Found`: Notification status not found.

#### `POST /api/user/signup`
Registers a new user account.

**Request**:
```json
{
  "email": "string (email format)",
  "password": "string",
  "preferences?": {
    "email?": "boolean",
    "push?": "boolean",
    "sms?": "boolean"
  }
}
```

**Response**:
```json
{
  "id": "uuid",
  "email": "string (email format)",
  "token?": "string"
}
```

**Errors**:
- `400 Bad Request`: Invalid input or email already exists.
- `500 Internal Server Error`: Upstream user service error.

#### `POST /api/user/login`
Authenticates a user and issues access tokens.

**Request**:
```json
{
  "email": "string (email format)",
  "password": "string"
}
```

**Response**:
```json
{
  "id": "uuid",
  "email": "string (email format)",
  "token?": "string"
}
```

**Errors**:
- `401 Unauthorized`: Invalid credentials.
- `500 Internal Server Error`: Upstream user service error.

---

### User Service API
The User Service handles all user-related operations, including authentication, registration, and management of user preferences and push tokens.

#### Base URL
`/api/users`

#### Endpoints

#### `POST /api/users/register/`
Registers a new user in the system.

**Request**:
```json
{
  "email": "string (email format)",
  "full_name": "string",
  "password": "string"
}
```

**Response**:
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user_id": "uuid",
    "email": "string (email format)"
  },
  "error": null,
  "meta": {
    "total": 1,
    "limit": 1,
    "page": 1,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  }
}
```

**Errors**:
- `400 Bad Request`: Validation errors (e.g., invalid email, missing fields, email already exists).
- `500 Internal Server Error`: Server-side error during registration.

#### `POST /api/users/login/`
Authenticates a user and returns JWT access and refresh tokens.

**Request**:
```json
{
  "email": "string (email format)",
  "password": "string"
}
```

**Response**:
```json
{
  "refresh": "string (JWT)",
  "access": "string (JWT)",
  "user": {
    "id": "uuid",
    "email": "string (email format)",
    "full_name": "string"
  }
}
```

**Errors**:
- `401 Unauthorized`: Invalid email or password.

#### `POST /api/users/refresh/`
Refreshes an expired access token using a valid refresh token.

**Request**:
```json
{
  "refresh": "string (JWT)"
}
```

**Response**:
```json
{
  "access": "string (JWT)"
}
```

**Errors**:
- `401 Unauthorized`: Invalid or expired refresh token.

#### `GET /api/users/<uuid:pk>/`
Retrieves details for a specific user. Requires authentication.

**Request**:
(Path parameter `pk` representing user ID)

**Response**:
```json
{
  "id": "uuid",
  "email": "string (email format)",
  "full_name": "string"
}
```

**Errors**:
- `401 Unauthorized`: Missing or invalid authentication token.
- `403 Forbidden`: User does not have permission to access the requested resource.
- `404 Not Found`: User with the given ID does not exist.

#### `GET /api/users/<uuid:user_id>/preferences/`
Retrieves the notification preferences for a specific user. Requires authentication.

**Request**:
(Path parameter `user_id` representing user ID)

**Response**:
```json
{
  "email_notifications": "boolean",
  "push_notifications": "boolean",
  "sms_notifications": "boolean",
  "categories": []
}
```

**Errors**:
- `401 Unauthorized`: Missing or invalid authentication token.
- `403 Forbidden`: User does not have permission.
- `404 Not Found`: User with the given ID does not exist.

#### `PUT /api/users/<uuid:user_id>/preferences/`
Updates the notification preferences for a specific user. Requires authentication.

**Request**:
(Path parameter `user_id` representing user ID)
```json
{
  "email_notifications": "boolean",
  "push_notifications": "boolean",
  "sms_notifications": "boolean",
  "categories": [
    "string"
  ]
}
```

**Response**:
(Same as GET response)
```json
{
  "email_notifications": true,
  "push_notifications": true,
  "sms_notifications": false,
  "categories": []
}
```

**Errors**:
- `400 Bad Request`: Invalid input data.
- `401 Unauthorized`: Missing or invalid authentication token.
- `403 Forbidden`: User does not have permission.
- `404 Not Found`: User with the given ID does not exist.

#### `PATCH /api/users/<uuid:user_id>/preferences/`
Partially updates the notification preferences for a specific user. Requires authentication.

**Request**:
(Path parameter `user_id` representing user ID)
```json
{
  "push_notifications": false
}
```

**Response**:
(Same as GET response)
```json
{
  "email_notifications": true,
  "push_notifications": false,
  "sms_notifications": false,
  "categories": []
}
```

**Errors**:
- `400 Bad Request`: Invalid input data.
- `401 Unauthorized`: Missing or invalid authentication token.
- `403 Forbidden`: User does not have permission.
- `404 Not Found`: User with the given ID does not exist.

#### `POST /api/users/<uuid:user_id>/push-tokens/`
Registers a new FCM push token for a user's device. Requires authentication.

**Request**:
(Path parameter `user_id` representing user ID)
```json
{
  "fcm_token": "string",
  "platform": "android" | "ios" | "web" | "other",
  "device_id?": "string"
}
```

**Response**:
```json
{
  "id": "uuid",
  "device_id": "string",
  "fcm_token": "string",
  "platform": "string",
  "is_active": true,
  "created_at": "date-time"
}
```

**Errors**:
- `400 Bad Request`: Invalid input data.
- `401 Unauthorized`: Missing or invalid authentication token.
- `403 Forbidden`: User does not have permission.
- `404 Not Found`: User with the given ID does not exist.

---

### Template Service API
The Template Service provides endpoints for managing and rendering notification templates.

#### Base URL
(No explicit base prefix, endpoints are directly at the root of the service.)

#### Endpoints

#### `GET /health`
Performs a health check for the Template Service.

**Request**:
(No payload)

**Response**:
```json
{
  "status": "ok"
}
```

**Errors**:
- `500 Internal Server Error`: Service is unhealthy or unavailable.

#### `POST /templates/`
Creates a new notification template.

**Request**:
```json
{
  "code": "string (unique identifier for template)",
  "content": "string (Jinja2 template content)",
  "language?": "string (e.g., 'en')"
}
```

**Response**:
```json
{
  "id": "integer",
  "code": "string",
  "content": "string",
  "language": "string"
}
```

**Errors**:
- `400 Bad Request`: Template code already exists or invalid input.

#### `GET /templates/{code}`
Retrieves a notification template by its unique code.

**Request**:
(Path parameter `code`)

**Response**:
```json
{
  "id": "integer",
  "code": "string",
  "content": "string",
  "language": "string"
}
```

**Errors**:
- `400 Bad Request`: Template not found.

#### `POST /render/{code}`
Renders a template using provided variables.

**Request**:
(Path parameter `code`)
```json
{
  "variable_name_1": "value_1",
  "variable_name_2": "value_2"
}
```

**Response**:
```json
{
  "rendered": "string (rendered template content)"
}
```

**Errors**:
- `404 Not Found`: Template with the given code does not exist.
- `422 Unprocessable Entity`: Error during template rendering (e.g., missing variable).

---

### Push Service API
The Push Service is responsible for sending push notifications. It also provides a public endpoint for health checks and an internal endpoint for queueing push messages.

#### Base URL
(No explicit base prefix, endpoints are directly at the root of the service.)

#### Endpoints

#### `GET /health`
Performs a health check for the Push Service.

**Request**:
(No payload)

**Response**:
```json
{
  "status": "ok"
}
```

**Errors**:
- `500 Internal Server Error`: Service is unhealthy or unavailable.

#### `POST /send/`
Queues a push message for asynchronous processing and delivery.

**Request**:
```json
{
  "request_id": "string (unique ID for this request)",
  "user_id": "string (ID of the recipient user)",
  "template_code": "string (template to use for the message)",
  "variables": {
    "key": "value"
  },
  "priority?": "integer (e.g., 1-10, higher is more urgent)",
  "metadata?": {
    "title?": "string (notification title)",
    "push_token?": "string (FCM token if known by caller)",
    "any_other_data": "any"
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "queued"
}
```

**Errors**:
- `422 Unprocessable Entity`: Validation error for payload data.
- `500 Internal Server Error`: Failure to publish message to RabbitMQ.

#### `POST /{notification_reference}/status`
(This endpoint is defined but currently not implemented in the provided code, serving as a placeholder.)

## Technologies Used

| Technology         | Category           | Description                                                                                             |
| :----------------- | :----------------- | :------------------------------------------------------------------------------------------------------ |
| **NestJS**         | Backend Framework  | Progressive Node.js framework for building efficient, reliable, and scalable server-side applications. |
| **FastAPI**        | Backend Framework  | Modern, fast (high-performance) web framework for building APIs with Python 3.8+.                       |
| **Django REST Framework** | Backend Framework  | Powerful and flexible toolkit for building Web APIs in Django.                                          |
| **TypeScript**     | Language           | Statically typed superset of JavaScript that compiles to plain JavaScript.                              |
| **Python**         | Language           | High-level, interpreted programming language known for its readability and versatility.                 |
| **RabbitMQ**       | Message Broker     | Open-source message broker that implements the Advanced Message Queuing Protocol (AMQP).                |
| **PostgreSQL**     | Database           | Powerful, open-source object-relational database system.                                                |
| **Redis**          | Caching/DB         | Open-source, in-memory data structure store used as a database, cache, and message broker.            |
| **Docker**         | Containerization   | Platform to develop, ship, and run applications in containers.                                          |
| **Docker Compose** | Orchestration      | Tool for defining and running multi-container Docker applications.                                      |
| **Nodemailer**     | Email Library      | Module for Node.js applications to send emails.                                                         |
| **PyFCM**          | Push Notifications | Python client for Firebase Cloud Messaging (FCM).                                                       |
| **Jinja2**         | Templating Engine  | Fast, expressive, and extensible templating engine for Python.                                          |
| **SQLModel**       | ORM                | Library for interacting with SQL databases, designed for FastAPI and based on SQLAlchemy.               |
| **TypeORM**        | ORM                | ORM that can run in NodeJS, Browser, React Native, Expo, and Electron platforms.                        |

## License
This project is licensed under the [MIT License](LICENSE).

## Author Info
- **Abisoye Ogunmona**
  - LinkedIn: [Your LinkedIn Profile]
  - Twitter: [Your Twitter Handle]

[![Readme was generated by Dokugen](https://img.shields.io/badge/Readme%20was%20generated%20by-Dokugen-brightgreen)](https://www.npmjs.com/package/dokugen)