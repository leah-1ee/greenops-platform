from fastapi import FastAPI
from api.routes import health, intensity, recommendation, report
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="Carbon Aware Scheduler", redirect_slashes=False)

app.include_router(health.router)
app.include_router(intensity.router, prefix="/intensity")
app.include_router(recommendation.router, prefix="/recommendation")
app.include_router(report.router, prefix="/recommendation/report")
