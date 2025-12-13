from fastapi import FastAPI
from collector.app.api.routes import routes_collect

app = FastAPI(title="Log Collector Service")

app.include_router(routes_collect.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
