import uvicorn
from fastapi import FastAPI
from src.routes import contacts

app = FastAPI(title="Contacts API")

app.include_router(contacts.router, prefix='/api')

@app.get("/")
def read_root():
    return {"message": "Welcome to Contacts API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)