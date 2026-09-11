# Recipes Web App

Simple Django recipe sharing web app, server-rendered.

## Features

- User registration, login, logout
- Create, edit, delete recipes, owner-only
- Recipe title, description, ingredients, and image URL
- Public recipe list and recipe detail pages
- Add, edit, delete comments, comment author only
- Ingredient-based filtering, recipes must contain all selected ingredients

## Demo account

- username: demo
- password: demo12345

## Quick start (Windows PowerShell)

Create and activate a virtual environment, install requirements, run migrations and seed demo data:

python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver 127.0.0.1:8000

Then open http://127.0.0.1:8000/ in your browser.
