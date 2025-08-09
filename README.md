# Job Portal REST API

![Django](https://img.shields.io/badge/Django-4.2-092E20?style=for-the-badge&logo=django)
![Django REST Framework](https://img.shields.io/badge/DRF-3.14-A30000?style=for-the-badge&logo=django-rest-framework)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python)

A robust RESTful API for a job portal platform built with Django and Django REST Framework. This project allows companies to sign up and manage job posts, and applicants to sign up, browse jobs, apply, and track their applications.

The API is designed following backend best practices, focusing on authentication, role-based authorization, ownership enforcement, search, pagination, and cloud-based file uploads.

## Key Features

*   **Role-Based User System**: Distinct roles for `applicant` and `company` with specific permissions.
*   **Secure Authentication**: JWT-based authentication (Login, Register).
*   **Email Verification**: New users must verify their email via a time-sensitive link before they can log in.
*   **Job Management (Companies)**: Create, read, update, and delete job postings. Ownership is strictly enforced.
*   **Job Browsing & Filtering (Applicants)**: Search and filter open jobs by title, location, or company name.
*   **Application System (Applicants)**: Apply for jobs with a resume (uploaded to Cloudinary) and a cover letter.
*   **Application Tracking**: Applicants can view their application history and status. Companies can view and manage applications for their jobs.
*   **Status Management**:
    *   Jobs follow a `Draft` → `Open` → `Closed` lifecycle.
    *   Applications follow a `Applied` → `Reviewed` → `Interview` → `Rejected` → `Hired` lifecycle.
*   **Email Notifications**: Automated emails for account verification, new job applications (to company), and application status updates (to applicant).
*   **Comprehensive API Documentation**: Includes interactive Swagger UI and a Postman collection.
*   **Pagination**: All list endpoints are paginated for efficient data retrieval.

## Tech Stack

*   **Backend**: Django, Django REST Framework
*   **Authentication**: djangorestframework-simplejwt
*   **Database**: SQLite3 (Development), PostgreSQL (Production-ready)
*   **File Storage**: Cloudinary for cloud-based resume uploads.
*   **API Schema & Docs**: drf-spectacular for OpenAPI 3 (Swagger UI).
*   **Environment Variables**: python-dotenv
*   **Filtering**: django-filter

## API Documentation

The API is fully documented and can be explored via the following links:

*   **Swagger / OpenAPI UI**: **[http://<YOUR_DEPLOYMENT_LINK>/api/docs/](http://<YOUR_DEPLOYMENT_LINK>/api/docs/)**
*   **Postman Collection**: **[<YOUR_PUBLIC_POSTMAN_LINK>](<YOUR_PUBLIC_POSTMAN_LINK>)**

## Getting Started

Follow these instructions to get the project up and running on your local machine for development and testing.

### Prerequisites

*   Python 3.8+
*   pip and venv
*   A Cloudinary account (for file uploads)

### Local Setup

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPO_NAME>.git
    cd <YOUR_REPO_NAME>
    ```

2.  **Create and activate a virtual environment:**
    *   On macOS/Linux:
        ```sh
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   On Windows:
        ```sh
        python -m venv venv
        .\venv\Scripts\activate
        ```

3.  **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    *   Create a `.env` file in the project root by copying the example file.
        ```sh
        cp .env.example .env
        ```
    *   Open the `.env` file and fill in your credentials. See the [Environment Variables](#environment-variables) section below for details.

5.  **Apply database migrations:**
    ```sh
    python manage.py migrate
    ```

6.  **Create a superuser (optional, for admin access):**
    ```sh
    python manage.py createsuperuser
    ```

7.  **Run the development server:**
    ```sh
    python manage.py runserver
    ```
    The API will be available at `http://127.0.0.1:8000/`.

## Environment Variables

To run this project, you will need to add the following environment variables to your `.env` file. Get your Cloudinary credentials from your Cloudinary dashboard.

| Variable | Description | Example |
| :--- | :--- | :--- |
| `SECRET_KEY` | Django's secret key for cryptographic signing. | `django-insecure-your-random-secret-key-here` |
| `DEBUG` | Toggles Django's debug mode. Set to `False` in production. | `True` |
| `CLOUDINARY_CLOUD_NAME`| Your Cloudinary cloud name. | `your-cloud-name` |
| `CLOUDINARY_API_KEY` | Your Cloudinary API key. | `123456789012345` |
| `CLOUDINARY_API_SECRET`| Your Cloudinary API secret. | `aBcDeFgHiJkLmNoPqRsTuVwXyZ` |
| `EMAIL_HOST_USER` | Your email service username (e.g., for SendGrid). | `apikey` |
| `EMAIL_HOST_PASSWORD` | Your email service password or API key. | `SG.your.sendgrid.api.key` |

*Note: The project is configured to use Django's console email backend by default for development, which prints emails to the console. To use a real email service, update the `EMAIL_...` variables and change `EMAIL_BACKEND` in `settings.py`.*

## API Endpoints Overview

The base URL for the API is `/api`.

### Authentication (`/auth/`)
| Endpoint | Method | Role | Description |
| :--- | :--- | :--- | :--- |
| `/register/` | `POST` | Public | Register as an `applicant` or `company`. |
| `/verify-email/` | `GET` | Public | Verify email using the token from the registration email. |
| `/login/` | `POST` | Public | Log in to get JWT access and refresh tokens. |
| `/token/refresh/` | `POST`| Public | Get a new access token using a refresh token. |

### Jobs (`/jobs/`)
| Endpoint | Method | Role | Description |
| :--- | :--- | :--- | :--- |
| `/` | `GET` | Authenticated | Browse and filter all `Open` jobs. |
| `/` | `POST` | Company | Create a new job post. |
| `/{job_id}/` | `GET` | Authenticated | View the details of a specific job. |
| `/{job_id}/` | `PUT/PATCH` | Company (Owner) | Update a job post they own. |
| `/{job_id}/` | `DELETE` | Company (Owner) | Delete a job post they own. |
| `/my-jobs/` | `GET` | Company | View all jobs posted by the authenticated company. |
