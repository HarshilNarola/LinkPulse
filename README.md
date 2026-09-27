# LinkPulse

LinkPulse is a beginner-friendly, production-style URL shortening and analytics platform built with FastAPI, SQLAlchemy, PostgreSQL, and vanilla HTML/CSS/JavaScript.

## Project overview

This project lets users:

- register and log in
- create shortened URLs
- manage their links
- redirect through shortened codes
- view click analytics
- access admin tools

The app is designed for learning and local development. It includes authentication, authorization, database persistence, analytics, and a simple frontend.

## Access from another device on the same network

`127.0.0.1` and `localhost` only refer to the device where the server is running. To share the app on a local network:

1. Find the host computer's LAN IP address with `ipconfig` (for example, `192.168.1.25`).
2. Start the backend from `backend/`:

  ```text
  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```

3. Start the frontend from `frontend/`:

  ```text
  python -m http.server 5500 --bind 0.0.0.0
  ```

4. Open `http://192.168.1.25:5500/index.html` on the host computer and other devices. Generated short links will then use that LAN hostname instead of `127.0.0.1`.

The devices must be on the same network, and Windows Firewall must allow inbound access to ports `5500` and `8000`. Internet-wide access requires deploying the app to a public host or using a secure tunnel.

For a universal link that works outside your local network, deploy the FastAPI backend to a public HTTPS address and set `window.LINKPULSE_PUBLIC_API_URL` before loading `js/api.js` in the frontend. For example:

```html
<script>
  window.LINKPULSE_PUBLIC_API_URL = "https://links.example.com";
</script>
<script src="js/api.js"></script>
```

The generated links will then use `https://links.example.com/<short-code>`. A local `127.0.0.1` or LAN address cannot be universal because it is only reachable from the local device or network.

## Deploy with Docker on Render

This repository includes `backend/Dockerfile`, `backend/.dockerignore`, `frontend/js/config.js`, and `render.yaml`.

1. Push the project to GitHub.
2. In Render, choose **New > Blueprint**, connect the repository, and apply `render.yaml`.
3. Render creates the Docker FastAPI service, static frontend, and PostgreSQL database.
4. Copy the backend URL from Render, such as `https://linkpulse-api.onrender.com`.
5. Open `frontend/js/config.js` and set:

  ```javascript
  window.LINKPULSE_PUBLIC_API_URL = 'https://linkpulse-api.onrender.com';
  ```

6. Push that change to GitHub so Render redeploys the static frontend.
7. Confirm `BACKEND_CORS_ORIGINS` contains the exact frontend URL shown by Render, then redeploy the backend if the URL has a suffix.

New links will use the public Render backend URL and work from any internet-connected device. The Docker service listens on Render's `$PORT`, and the database uses Render PostgreSQL rather than temporary local SQLite storage.

## Features

- User registration and login
- JWT access and refresh tokens
- Password hashing with bcrypt
- User and admin roles
- URL shortening with short codes
- URL expiration and enable/disable toggling
- Click tracking for each shortened URL
- Analytics dashboard with counts and breakdowns
- Admin dashboard with global statistics
- Swagger API docs via FastAPI
- Automated pytest coverage for core flows

## Technologies

Backend:

- Python 3.13+
- FastAPI
- Uvicorn
- SQLAlchemy 2.x
- PostgreSQL
- Pydantic v2
- pydantic-settings
- python-jose
- passlib + bcrypt
- pytest and httpx

Frontend:

- HTML5
- CSS3
- Vanilla JavaScript
- Chart.js from CDN

## Architecture

Frontend
  |
  | REST API
  v
FastAPI
  |
  +-- API routers
  +-- Authentication
  +-- Services
  +-- Schemas
  v
SQLAlchemy
  v
PostgreSQL

## Folder structure

```text
LinkPulse/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── admin.py
│   │   │   ├── analytics.py
│   │   │   ├── auth.py
│   │   │   ├── urls.py
│   │   │   └── __init__.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── __init__.py
│   │   ├── db/
│   │   │   ├── database.py
│   │   │   └── __init__.py
│   │   ├── models/
│   │   │   ├── click.py
│   │   │   ├── url.py
│   │   │   ├── user.py
│   │   │   └── __init__.py
│   │   ├── schemas/
│   │   │   ├── analytics.py
│   │   │   ├── auth.py
│   │   │   ├── url.py
│   │   │   ├── user.py
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   ├── analytics_service.py
│   │   │   ├── url_service.py
│   │   │   └── __init__.py
│   │   ├── utils/
│   │   │   ├── short_code.py
│   │   │   ├── user_agent.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   └── main.py
│   ├── tests/
│   │   ├── test_analytics.py
│   │   ├── test_auth.py
│   │   ├── test_urls.py
│   │   └── __init__.py
│   ├── .env.example
│   ├── .gitignore
│   └── requirements.txt
├── frontend/
│   ├── admin.html
│   ├── analytics.html
│   ├── create-url.html
│   ├── dashboard.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── css/
│   │   ├── auth.css
│   │   ├── dashboard.css
│   │   └── style.css
│   └── js/
│       ├── admin.js
│       ├── analytics.js
│       ├── api.js
│       ├── auth.js
│       └── dashboard.js
├── docs/
│   └── architecture.md
├── .gitignore
├── requirements.txt
├── README.md
└── .
```

## Database design

The application uses PostgreSQL with SQLAlchemy ORM.

### users

- id: primary key
- name: display name
- email: unique
- password_hash: hashed password
- role: USER or ADMIN
- is_active: active status
- created_at: timestamp

### urls

- id: primary key
- user_id: foreign key to users.id
- original_url: destination URL
- short_code: unique generated code
- created_at: timestamp
- expires_at: optional expiration
- is_active: active flag

### clicks

- id: primary key
- url_id: foreign key to urls.id
- clicked_at: timestamp
- ip_address: visitor IP
- user_agent: browser metadata
- referrer: source page
- device_type: mobile/desktop/tablet
- browser: browser family
- country: optional

User to URL is a one-to-many relationship. One user can have many URLs. Each URL can have many click records. The click table stores every redirect event.

## API list

Authentication:

- POST /api/auth/register
- POST /api/auth/login

URLs:

- POST /api/urls
- GET /api/urls
- GET /api/urls/{url_id}
- PUT /api/urls/{url_id}
- DELETE /api/urls/{url_id}
- PATCH /api/urls/{url_id}/status

Redirect:

- GET /{short_code}

Analytics:

- GET /api/analytics/{url_id}

Admin:

- GET /api/admin/users
- GET /api/admin/urls
- GET /api/admin/statistics
- PATCH /api/admin/users/{user_id}/status

## Authentication explanation

The app uses JWT for authentication.

- Access token: short-lived, used for protected API endpoints
- Refresh token: longer-lived, used to renew access tokens
- Passwords are hashed before being stored in the database
- Authentication is checked with a dependency that reads the token and finds the current user
- Only admins can access admin endpoints

## Environment setup

1. Open a terminal in the backend folder.
2. Create a virtual environment.
3. Install dependencies from requirements.txt.
4. Copy .env.example to .env.
5. Add the correct PostgreSQL connection string and JWT secret.

Do not commit the real .env file.

## PostgreSQL setup

1. Install PostgreSQL.
2. Start the local PostgreSQL service.
3. Create a database named linkpulse.
4. Update DATABASE_URL in backend/.env.

Example:

```env
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/linkpulse
```

Replace YOUR_PASSWORD with your actual local PostgreSQL password.

## Backend setup

From PowerShell or Git Bash:

```bash
cd backend
python -m venv venv
```

Activate the environment:

PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Git Bash:

```bash
source venv/Scripts/activate
```

Then install:

```bash
pip install -r requirements.txt
```

Create backend/.env based on .env.example, then run:

```bash
uvicorn app.main:app --reload
```

The API docs are available at:

- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/redoc

## Frontend setup

The frontend is served as static HTML files. You can use VS Code Live Server or any simple local HTTP server.

Example with Python:

```bash
cd frontend
python -m http.server 5500
```

Open:

- http://127.0.0.1:5500/index.html

The frontend communicates with the API at:

```text
http://127.0.0.1:8000
```

## Running the project

Start PostgreSQL and ensure the database exists.

Then run the backend:

```bash
cd backend
uvicorn app.main:app --reload
```

Then run the frontend server:

```bash
cd frontend
python -m http.server 5500
```

## Running tests

```bash
cd backend
pytest -q
```

## Swagger documentation

FastAPI automatically exposes interactive docs at:

- /docs
- /redoc

## Example API requests

### Register

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Harshil","email":"harshil@example.com","password":"password123"}'
```

### Login

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"harshil@example.com","password":"password123"}'
```

### Create URL

```bash
curl -X POST http://127.0.0.1:8000/api/urls \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"original_url":"https://www.example.com","expires_at":null}'
```

## Security notes

This project follows basic security practices:

- passwords are hashed
- JWT secret is kept in environment variables
- environment files are not committed
- API access is checked with dependencies
- users can only manage their own URLs

This is designed for learning and local development. For production use, you would add stronger hardening such as rate limiting, secure cookies, HTTPS, monitoring, and more careful deployment controls.

## Future improvements

- Add refresh-token endpoint
- Add email verification
- Add rate limiting
- Add QR codes for shortened links
- Add geolocation enrichment
- Add better user dashboards and charts
- Add pagination and search
- Add Alembic migrations

## Project status

The project is a working learning project with a full CRUD flow, authentication, analytics, and admin features.
