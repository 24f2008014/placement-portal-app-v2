# placement-portal-app-v2
MAD-2 Project for T1 2026 (Placement Portal Application).

## Student Info
- **Name:** Manoranjan Kumar
- **Roll Number:** 24f2008014

## Installing/Running
- Clone the repo.
- Install the frontend requirements by running `npm install` from the `/client` directory.
- Install the backend requirements by running `uv sync` from the `/server` directory.
- Setup `/server/config.py` as needed.
- If `app.db` (the DB instance) is not present in `/server/instance`, run these commands sequentially from the `/server` directory:
    - `uv run flask db check`
    - `uv run flask db upgrade`
    - `uv run flask setup-db`
- To run the project, run each of these commands in separate terminals:
    - From the `/server` directory:
        - `uv run flask run`
        - `celery -A make_celery worker --loglevel INFO`
        - `celery -A make_celery beat --loglevel INFO`
    - From the `/client` directory:
        - `npm run dev`
    - Anywhere:
        - `mailhog`
    - Note: If you don't have a Redis server running, you will also need to spin one up.
- Finally, navigate to `http://localhost:5173/` to view the application.