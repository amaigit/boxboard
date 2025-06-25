from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="BoxBoard API", version="1.0.0")

@app.get("/health", tags=["Health"])
def healthcheck():
    """Verifica che l'API sia attiva"""
    return JSONResponse(content={"status": "ok"})

# --- Qui verranno aggiunti gli endpoint di autenticazione, utenti, ecc. ---

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 