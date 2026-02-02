# app/main.py
from fastapi import FastAPI, Depends, Header, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas, crud, database

# ----- Database setup -----
models.Base.metadata.create_all(bind=database.engine)

# ----- FastAPI app -----
app = FastAPI(title="Expense Tracker API")

# ----- CORS Setup -----
origins = [
    "http://localhost:5173",  
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- DB Dependency -----
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----- Routes -----
@app.post("/expenses", response_model=schemas.ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense: schemas.ExpenseCreate,
    db: Session = Depends(get_db),
    idempotency_key: Optional[str] = Header(None)
):
    # Prevent duplicate expense on retry
    if idempotency_key:
        existing = crud.get_expense_by_idempotency_key(db, idempotency_key)
        if existing:
            return existing
    return crud.create_expense(db, expense, idempotency_key)


@app.get("/expenses", response_model=List[schemas.ExpenseResponse])
def get_expenses(
    category: Optional[str] = Query(None),
    sort: Optional[str] = Query(None, description="Use 'date_desc' to sort newest first"),
    db: Session = Depends(get_db)
):
    sort_desc = sort == "date_desc"
    return crud.get_expenses(db, category, sort_desc)
