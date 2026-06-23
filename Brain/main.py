from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "you are in the brain module"}