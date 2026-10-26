# Gym Manager

A deliberately small FastAPI and Streamlit application for managing gyms and their branches.

## Run locally

Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Start the API in one terminal:

```powershell
uvicorn main:app --reload
```

Start the Streamlit frontend in another terminal:

```powershell
streamlit run streamlit_app.py
```

Open Streamlit at `http://localhost:8501`. FastAPI documentation is available at `http://127.0.0.1:8000/docs`.

## Endpoints

- `POST /gyms` — register a gym
- `POST /branches` — register a branch for a gym
- `GET /gyms/{gym_id}` — get a gym and all its branches

