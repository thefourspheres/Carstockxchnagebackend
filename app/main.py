from fastapi import FastAPI
from app.core.database import check_db_connection, engine, Base
from app.core.startup_notifier import startup_health_check
from app.core.startup_notifier import startup_health_check
from app.modules.admin.employee.employee_routes import router as employee_router
from app.modules.admin.auth.auth_routes import router as auth_router
from app.modules.admin.role.role_routes import router as role_router
from app.modules.admin.organization.organization_routes import router as organization_router
from app.modules.superadmin_routes import router as superadmin_router
from app.modules.admin.cars.car_routes import router as car_router
from app.modules.public.Car.public_car_routes import router as public_car_router

from app.modules.admin.cars.car_routes import router as car_router
from app.modules.admin.leads.admin_lead_routes import router as admin_lead_router

from app.modules.public.Car.public_car_routes import router as public_car_router
from app.modules.public.leads.public_lead_routes import router as public_lead_router

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os


# Create FastAPI app
app = FastAPI(
    title="Car Stock Exchange API",
    description="API for managing cars and their images",
    version="1.0.0"
)

# Create uploads directory if it doesn't exist
uploads_dir = "uploads"
os.makedirs(uploads_dir, exist_ok=True)

# Serve static files from uploads directory
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(car_router)

@app.get("/")
async def root():
    return {
        "message": "Car Stock Exchange API",
        "version": "1.0.0",
        "docs": "/docs",
        "storage_type": "local",
        "uploads_endpoint": "/uploads"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "storage": {
            "type": "local",
            "path": uploads_dir,
            "exists": os.path.exists(uploads_dir)
        }
    }

app.include_router(auth_router)
app.include_router(employee_router)
app.include_router(car_router)
app.include_router(role_router)
app.include_router(organization_router)
app.include_router(superadmin_router)

app.include_router(public_car_router)






# Admin (secured)
app.include_router(car_router)
app.include_router(admin_lead_router)

# Public (open)
app.include_router(public_car_router)
app.include_router(public_lead_router)



@app.on_event("startup")
async def startup_event():
    await check_db_connection()

    from app.core.startup_notifier import startup_health_check

@app.on_event("startup")
async def notify_on_startup():
    await startup_health_check()

#6839825c-1e94-40ad-b409-977f519106ed


