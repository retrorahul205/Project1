from pydantic import BaseModel
from typing import Optional
from fastapi import APIrouter, Depends, HTTPException, status

from api.models import Workout
from api.deps import db_dependency,user_dependency

router =APIrouter(
    prefix="/workouts",
    tags=["workouts"]
)

class WorkoutBase(BaseModel):
    name: str
    description: Optional[str] = None

class WorkoutCreate(WorkoutBase):
    pass


@router.get("/")
def get_workout(db: db_dependency, current_user: user_dependency,workout_id:int):
    return db.query(Workout).filter(Workout.id== workout_id, Workout.user_id== current_user.id).first()

@router.get("/workouts")
def get_workouts(db: db_dependency, current_user: user_dependency):
    return db.query(Workout).filter(Workout.user_id== current_user.id).all()

@rotuer.post("/", status_code=status.HTTP_201_CREATED)
def create_workout(
    workout: WorkoutCreate,
    db: db_dependency,
    current_user: user_dependency
):
    workout_model= Workout(
        name= workout.name,
        description= workout.description,
        user_id= current_user.id
    )
    db.add(workout_model)
    db.commit()
    db.refresh(workout_model)
    return workout_model


@router.delete("/")
def delete_workout(
    workout_id: int,
    db: db_dependency,
    current_user: user_dependency
):
    workout_model= db.query(Workout).filter(Workout.id== workout_id, Workout.user_id== current_user.id).first()
    if workout_model:
        db.delete(workout_model)
        db.commit()
    return workout_model

