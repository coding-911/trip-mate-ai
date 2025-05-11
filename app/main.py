from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.core.config import settings
from app.api.v1.routers import users, auth, locations, recommendations, user_events, bookmarks

app = FastAPI()  


app.include_router(auth.router)
app.include_router(bookmarks.router)
app.include_router(locations.router)
app.include_router(recommendations.router)
app.include_router(users.router)
app.include_router(user_events.router)


@app.get("/")  
def root():  
    return {"message": "TripMateAI starting"}  

@app.get("/db-health")
def db_health_check(db: Session = Depends(get_db)):
    try:
        # 간단히 SELECT 1 실행
        db.execute(text("SELECT 1"))
        return {"db": "ok"}
    except Exception as e:
        # 에러가 나면 500으로 돌려줌
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/config-test")
def config_test():
    return {"db_url": settings.DATABASE_URL}

