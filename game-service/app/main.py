from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, database
from app.models import Game
from pydantic import BaseModel
from typing import Optional
from datetime import date

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

class GameCreate(BaseModel):
    title: str
    genre: str
    price: float
    released_date:date

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Game Service API is running."}

# GET endpoint - all
@app.get("/games")
def get_games(db: Session = Depends(get_db)):
    return db.query(Game).all()

# GET endpoint - by id 
@app.get("/games/{game_id}")
def get_game_by_id(game_id: int, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game

# POST endpoint
@app.post("/games")
def create_game(game: GameCreate, db: Session = Depends(get_db)):
    db_game = Game(title=game.title, genre=game.genre, price=game.price, released_date=game.released_date)
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game

# DELETE endpoint
@app.delete("/games/{game_id}")
def delete_game(game_id: int, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    db.delete(game)
    db.commit()
    return {"message": f"Game with id {game_id} deleted"}

# UPDATE endpoint
@app.put("/games/{game_id}")
def update_game(game_id: int, updated_game: GameCreate, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    game.title = updated_game.title
    game.genre = updated_game.genre
    game.price = updated_game.price
    game.released_date = updated_game.released_date

    db.commit()
    db.refresh(game)
    return game
