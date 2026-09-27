# LinkPulse Architecture

## Overview

LinkPulse is a full-stack URL shortener and analytics platform. The backend is built with FastAPI and SQLAlchemy. The frontend is static HTML/CSS/JavaScript served locally.

## System architecture

The flow is simple:

1. User opens the frontend.
2. Frontend sends HTTP requests to the FastAPI backend.
3. FastAPI validates input with Pydantic.
4. FastAPI uses dependencies to authenticate requests.
5. SQLAlchemy reads and writes to PostgreSQL.
6. Analytics are computed from the clicks table.

## Database relationships

The important relationships are:

- User has many URLs.
- URL belongs to one User.
- URL has many Click records.

This is represented in SQLAlchemy with `relationship()` and `ForeignKey` declarations.

## Authentication flow

1. User submits registration form.
2. Server validates data.
3. Password is hashed and saved.
4. User logs in with email and password.
5. Server verifies credentials.
6. Server returns access and refresh JWT tokens.
7. Frontend stores the access token for later API requests.

## URL shortening flow

1. User enters a long URL.
2. FastAPI validates the URL.
3. Application generates a unique short code.
4. URL is saved in the database.
5. Short code becomes part of the public URL.
6. Redirect endpoint opens the long URL and stores a click record.

## Analytics flow

When a short URL is visited:

- system looks up the URL by short code
- checks if it is active and unexpired
- creates a click record
- aggregates data for device, browser, dates, and referrers
- returns statistics to the frontend dashboard

## Authorization flow

The app uses `Depends(get_current_user)` and `Depends(require_admin)`.

- `get_current_user` verifies the JWT and loads the user
- `require_admin` ensures the user role is ADMIN
- normal users can manage only their own URLs
- admins can view all data and manage users

This keeps the API secure and easy to understand.
