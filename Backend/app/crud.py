from sqlalchemy.orm import Session
from . import models, schemas

def get_expense_by_idempotency_key(db: Session, key: str):
    expense = db.query(models.Expense).filter(
        models.Expense.idempotency_key == key
    ).first()
    if not expense:
        return None
    return schemas.ExpenseResponse(
        id=expense.id,
        amount=expense.amount_cents / 100,  # convert cents -> float
        category=expense.category,
        description=expense.description,
        date=expense.expense_date,
        created_at=expense.created_at
    )

def create_expense(db: Session, expense: schemas.ExpenseCreate, idempotency_key: str | None):
    amount_cents = int(round(expense.amount * 100))

    db_expense = models.Expense(
        amount_cents=amount_cents,
        category=expense.category,
        description=expense.description,
        expense_date=expense.date,
        idempotency_key=idempotency_key
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)

    # Return converted schema
    return schemas.ExpenseResponse(
        id=db_expense.id,
        amount=db_expense.amount_cents / 100,
        category=db_expense.category,
        description=db_expense.description,
        date=db_expense.expense_date,
        created_at=db_expense.created_at
    )

def get_expenses(db: Session, category: str | None, sort_desc: bool):
    query = db.query(models.Expense)

    if category:
        query = query.filter(models.Expense.category == category)

    if sort_desc:
        query = query.order_by(models.Expense.expense_date.desc(), models.Expense.created_at.desc())

    results = query.all()

    # Convert each to ExpenseResponse
    return [
        schemas.ExpenseResponse(
            id=e.id,
            amount=e.amount_cents / 100,
            category=e.category,
            description=e.description,
            date=e.expense_date,
            created_at=e.created_at
        )
        for e in results
    ]
