from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from collector.app.api.routes import routes_collect

app = FastAPI(title="Log Collector Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_collect.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
