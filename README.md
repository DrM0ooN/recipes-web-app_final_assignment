# Recipes Web App — Final Assignment

Simple Django recipe sharing web app (server-rendered). Features:

- User registration, login, logout
- Create / edit / delete recipes (owner-only)
- Recipe title, description, ingredients, and image URL
- Public recipe list and recipe detail pages
- Add, edit, delete comments (comment author only)
- Ingredient-based filtering (recipes must contain all selected ingredients)

Demo account (seeded):

- username: `demo`
- password: `demo12345`

Quick start (Windows PowerShell):

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install requirements and run migrations:

```powershell
pip install -r requirements.txt
.venv\Scripts\python.exe manage.py migrate
.venv\Scripts\python.exe manage.py seed_demo_data
```

3. Run the development server:

```powershell
.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Open http://127.0.0.1:8000/ in your browser.

Pushing to GitHub

Option A — using the GitHub CLI (`gh`) (recommended):

```bash
git init
git add .
git commit -m "Initial commit: Recipes web app"
# create repo and push
gh repo create recipes-web-app_final_assignment --public --source=. --remote=origin --push
```

Option B — using GitHub web (manual remote):

1. Create a new public repo named `recipes-web-app_final_assignment` on GitHub under your account.
2. Run locally:

```bash
git init
git add .
git commit -m "Initial commit: Recipes web app"
git branch -M main
# replace <USERNAME> with your GitHub username
git remote add origin git@github.com:<USERNAME>/recipes-web-app_final_assignment.git
git push -u origin main
```

If you prefer HTTPS remotes, use the `https://github.com/<USERNAME>/...` URL and authenticate with a personal access token if prompted.

If you want, I can create a small GitHub Actions workflow or add a CONTRIBUTING guide — tell me which you prefer.
