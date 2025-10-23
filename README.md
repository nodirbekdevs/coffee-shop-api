# ☕ Coffee Shop API

A clean, containerized backend service for managing **User** and **Verification** APIs in the Coffee Shop system.  
This project is built for scalability and follows modern backend practices with environment-based configuration, database migrations, and Dockerized deployment.

---

## 📚 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)

---

## 🧩 Overview

The **Coffee Shop API** currently includes:
- **User API** — manages registration, login, and user information  
- **Verification API** — handles verification logic (e.g., email/SMS code validation)  

The project is fully containerized using **Docker Compose**, simplifying setup for all environments.

---

## 🚀 Features

- RESTful APIs for **User** and **Verification**
- PostgreSQL integration with Alembic migrations
- Docker-based local and production environments
- Environment configuration via `.env` files
- Code linting and pre-commit hooks
- Scalable and modular architecture for future expansion

---

## 🛠️ Tech Stack

- **Language:** Python 3.x  
- **Framework:** (FastAPI)  
- **Database:** PostgreSQL  
- **Migrations:** Alembic  
- **Containerization:** Docker & Docker Compose  
- **Code Quality:** Flake8, Pylint, Pre-commit  

---

## ⚡ Quick Start

Clone the repository and start the API with **one command**:

```bash
git clone https://github.com/nodirbekdevs/coffee-shop-api.git
cd coffee-shop-api
docker compose up --build
```

That’s it! 🥳
After a few seconds, your API will be running at:

👉 http://localhost:8000


---

🧪 API Endpoints

After running the container, visit:

📘 Swagger Docs:
http://localhost:8000/docs

📗 ReDoc Docs:
http://localhost:8000/redoc
