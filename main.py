from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

import models
import schemas
from database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gym Manager API", version="1.0.0")

# Allows the Streamlit app (and local development tools) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/gyms", response_model=schemas.GymResponse, status_code=status.HTTP_201_CREATED)
def register_gym(gym: schemas.GymCreate, db: Session = Depends(get_db)):
    """Register one gym."""
    existing_gym = db.scalar(select(models.Gym).where(models.Gym.name == gym.name))
    if existing_gym:
        raise HTTPException(status_code=400, detail="A gym with this name already exists.")

    new_gym = models.Gym(**gym.model_dump())
    db.add(new_gym)
    db.commit()
    db.refresh(new_gym)
    return new_gym


@app.post("/branches", response_model=schemas.BranchResponse, status_code=status.HTTP_201_CREATED)
def register_branch(branch: schemas.BranchCreate, db: Session = Depends(get_db)):
    """Add a branch to an existing gym."""
    gym = db.get(models.Gym, branch.gym_id)
    if not gym:
        raise HTTPException(status_code=404, detail="Gym not found.")

    new_branch = models.Branch(**branch.model_dump())
    db.add(new_branch)
    db.commit()
    db.refresh(new_branch)
    return new_branch


@app.get("/gyms", response_model=list[schemas.GymResponse])
def list_gyms(db: Session = Depends(get_db)):
    """Fetch all registered gyms."""
    statement = (
        select(models.Gym)
        .options(selectinload(models.Gym.branches))
        .order_by(models.Gym.name)
    )
    return list(db.scalars(statement))


@app.get("/gyms/{gym_id}", response_model=schemas.GymResponse)
def get_gym_details(gym_id: int, db: Session = Depends(get_db)):
    """Fetch a gym and all of its branches."""
    statement = (
        select(models.Gym)
        .options(selectinload(models.Gym.branches))
        .where(models.Gym.id == gym_id)
    )
    gym = db.scalar(statement)
    if not gym:
        raise HTTPException(status_code=404, detail="Gym not found.")
    return gym
