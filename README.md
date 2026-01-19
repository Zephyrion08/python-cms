# Python CMS

A modern, lightweight Content Management System built with **Django 6.0** and **Python 3.14.2**.

---

## 🚀 Quick Start Guide

Follow these steps to get your development environment up and running.

### 1. Prerequisites
Ensure you have **Python 3.14.2** installed. 
* **Download here:** [Python 3.14.2 Official Release](https://www.python.org/downloads/release/python-3142/)

### 2. Setup and Installation
Copy and paste the following commands into your terminal to clone the repo, set up your environment, and launch the server:

```bash
# Clone the repository
git clone [https://github.com/Zephyrion08/python-cms.git](https://github.com/Zephyrion08/python-cms.git)
cd python-cms

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install Django 6.0 and dependencies
pip install django==6.0
# pip install -r requirements.txt # Uncomment if you have a requirements file

# Initialize the database and create admin access
python manage.py migrate
python manage.py createsuperuser

# Start the development server
python manage.py runserver
