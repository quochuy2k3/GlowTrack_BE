import asyncio

from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, Depends

from config.jwt_bearer import JWTBearer
from config.config import initiate_database
from routes.admin import router as AdminRouter
from routes.auth import router as AuthRouter
from routes.media import router as MediaRouter
from routes.routine import router as RoutineRouter
from routes.user import router as UserRouter
from service.routine_service import cron_job
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from routes.predict import router as PredictRouter
from routes.tracker import router as TrackerRouter
app = FastAPI()
token_listener = JWTBearer()

def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(cron_job, CronTrigger(second=0))
    scheduler.start()

@app.on_event("startup")
async def on_startup():
    start_scheduler()
    await initiate_database()

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app."}

# Routes
app.include_router(MediaRouter, tags=["Media"], prefix="/media")
app.include_router(AuthRouter, tags=["Authentication"], prefix="/auth")
app.include_router(AdminRouter, tags=["Administrator"], prefix="/admin")
app.include_router(RoutineRouter, tags=["Routines"], prefix="/routine")
app.include_router(UserRouter, tags=["Users"], prefix="/user", dependencies=[Depends(token_listener)])
app.include_router(PredictRouter, tags=["Predict"], prefix="/predict",dependencies=[Depends(token_listener)])
app.include_router(TrackerRouter, tags=["Tracker"], prefix="/tracker", dependencies=[Depends(token_listener)])