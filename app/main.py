from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.user import User

app = FastAPI(title="Modern FastAPI Stack")


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    # Simple async query to verify DB connection
    result = await db.execute(select(User).limit(1))
    return {"status": "online", "db_connected": True}
