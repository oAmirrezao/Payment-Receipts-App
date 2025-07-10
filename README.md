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
> ```bash
> pip install --only-binary :all: reportlab==3.6.12
> ```

## Prerequisites

- Git  
- Python (3.7–3.11)  
- (Optional) virtualenv or venv  

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
