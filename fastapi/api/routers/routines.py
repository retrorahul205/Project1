from pydantic import BaseModel
from fastapi import APIRouter, Depends, status
from typing import Optional,List
from sqlalchemy.orm import joinedload
from api.models import Workout, Routine
from api.deps import db_dependency, user_dependency


router=APIRouter(
    prefix="/routines",
    tags=["routines"]
)

class RoutineBase(BaseModel):
    name: str
    discription: Optional[str] = None  # Comma-separated list of exercises  

class RoutineCreate(RoutineBase):
    workouts: List[int] = []

@router.get("/")
def get_routines(
    db: db_dependency,
    current_user: user_dependency
):
    return db.query(Routine).options(joinedload(Routine.workouts)).filter(Routine.user_id== current_user.id).all()

@router.post("/")
def create_routine(
    routine: RoutineCreate,
    db: db_dependency,
    current_user: user_dependency
):
    routine_model= Routine(
        name= routine.name,
        discription= routine.discription,
        user_id= current_user.get('id')
    )
    for workout_id in routine.workouts:
        workout_model= db.query(Workout).filter(Workout.id== workout_id, Workout.user_id== current_user.id).first()
        if workout_model:
            routine_model.workouts.append(workout_model)
    db.add(routine_model)
    db.commit()
    db.refresh(routine_model)
    routine_model = db.query(Routine).options(joinedload(Routine.workouts)).filter(Routine.id== routine_model.id).first()
    return routine_model

@router.delete("/")
def delete_routine(
    routine_id: int,
    db: db_dependency,  
    current_user: user_dependency
):
    routine_model= db.query(Routine).filter(Routine.id== routine_id, Routine.user_id== current_user.id).first()
    if routine_model:
        db.delete(routine_model)
        db.commit()
    return routine_model