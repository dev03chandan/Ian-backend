from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routers import contract_router, invoice_router, auth_router, document_router, contract_new_router, invoice_new_route
from routers.auth import get_current_user
from database import init_db
from routers.Contract import load_far_regulatory_data
from contextlib import asynccontextmanager

# Initialize FastAPI app
regulatory_data = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    global regulatory_data
    try:
        regulatory_data = load_far_regulatory_data()  # Load the data at startup
        init_db()  # Initialize database here
        yield
    except Exception as e:
        print(f"Error during startup: {e}")
        regulatory_data = {}  # Fallback to an empty dictionary
    finally:
        # Perform any necessary cleanup here if needed
        print("Application shutdown")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, tags=["Authentication"])
app.include_router(
    document_router,
    prefix="/documents",
    tags=["Documents"],
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    contract_router,
    tags=["Contracts"],
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    invoice_router,
    tags=["Invoices"],
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    contract_new_router, 
    tags=["Contracts"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    invoice_new_route,
    tags=["Invoices"],
    dependencies=[Depends(get_current_user)]
)