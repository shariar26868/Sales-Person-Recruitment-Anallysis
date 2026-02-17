
from app.main import app

# root `main.py` left as a thin wrapper so both
# `uvicorn main:app` and `uvicorn app.main:app` continue to work.
