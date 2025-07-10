# Payment Receipts App

A simple Flask-based web application that lets users register, log in, and manage their payment receipts. Users can create, view, search, edit, delete receipts, export individual receipts as PDF, and back up all their receipts as a JSON file.

---

## Table of Contents

1. [Features](#features)  
2. [Tech Stack](#tech-stack)  
3. [Prerequisites](#prerequisites)  
4. [Installation](#installation)  
5. [Configuration](#configuration)  
6. [Database Initialization](#database-initialization)  
7. [Running the App](#running-the-app)  
8. [Usage Guide](#usage-guide)  
9. [Project Structure](#project-structure)  
10. [Deployment](#deployment)  
11. [Contributing](#contributing)  
12. [License](#license)  
13. [Acknowledgments](#acknowledgments)  

---

## Features

- User registration & authentication  
- Create, read, update, delete (CRUD) payment receipts  
- Search receipts by date or description  
- Export individual receipts to PDF (via ReportLab)  
- Backup all user receipts as a JSON file  
- SQLite for data storage  
- Clean, responsive UI using Flask & Jinja2  

## Tech Stack

- Python 3.7–3.11  
- Flask 2.2.5  
- Flask-Login 0.6.2  
- Flask-WTF 1.1.1  
- Flask-SQLAlchemy 3.0.5  
- ReportLab 3.6.12 (PDF generation)  
- SQLite  

> **Note:** ReportLab’s C extensions do not support Python 3.12+. If you see build errors, install a prebuilt wheel or switch to Python 3.11:
>
> ```bash
> pip install --only-binary :all: reportlab==3.6.12
> ```

## Prerequisites

- Git  
- Python (3.7–3.11)  
- (Optional) `virtualenv` or `venv`  

## Installation

1. **Clone the repo**  
   ```bash
   git clone https://github.com/your-username/payment-receipts-app.git
   cd payment-receipts-app
   ```

2. **Create & activate a virtual environment**  
   ```bash
   python -m venv venv
   # Windows PowerShell
   .\venv\Scripts\Activate.ps1
   # Windows CMD
   venv\Scripts\activate.bat
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**  
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Configuration

Edit `app.py` (or use a `.env` file) to set:

```python
app.config['SECRET_KEY'] = 'replace_with_a_random_string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
```

- **SECRET_KEY** – Flask session secret (change from default!)  
- **SQLALCHEMY_DATABASE_URI** – Defaults to SQLite; you can point to PostgreSQL/MySQL in production.

## Database Initialization

On first run, tables are created automatically:

```bash
python app.py
```

Alternatively, in a Python shell:

```python
from app import db
db.create_all()
```

## Running the App

```bash
python app.py
```

- Default: debug mode on http://127.0.0.1:5000  
- **Warning:** The built-in server is for development only. Use Gunicorn/uWSGI in production.

## Usage Guide

1. **Register** at `/register`  
2. **Log in** at `/login`  
3. **View receipts** at `/` or `/receipts`  
   - If empty: prompt to add a new receipt  
4. **Create** a receipt via **New Receipt**  
5. **Search** by date/description on `/receipts`  
6. **Edit/Delete** links next to each receipt  
7. **Export to PDF** via the PDF link  
8. **Backup JSON** at `/backup`  
9. **Logout** via the navigation bar  

## Project Structure

```
payment_receipts_app/
├── app.py
├── requirements.txt
├── db.sqlite         # created at runtime
├── static/           # optional: CSS, JS, images
└── templates/
    ├── base.html
    ├── login.html
    ├── register.html
    ├── form.html     # create/edit receipt form
    └── receipts.html
```

## Deployment

1. Remove or disable `debug=True`.  
2. Serve via WSGI (e.g., Gunicorn):  
   ```bash
   gunicorn -w 4 app:app
   ```  
3. Configure a reverse proxy (nginx, Apache) to forward requests.

## Contributing

1. Fork this repo  
2. Create a branch:  
   ```bash
   git checkout -b feature/YourFeature
   ```  
3. Commit & push:  
   ```bash
   git commit -m "Add new feature"
   git push origin feature/YourFeature
   ```  
4. Open a Pull Request.  
   - Follow PEP 8  
   - Include tests for new features

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/)  
- [Flask-Login](https://flask-login.readthedocs.io/)  
- [Flask-WTF](https://flask-wtf.readthedocs.io/)  
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)  
- [ReportLab](https://www.reportlab.com/)  
- GeeksforGeeks Python tutorials for inspiration  
