from fastapi import FastAPI
import uvicorn
from routes import base , data

def main():
    app = FastAPI()
    app.include_router(base.router)
    app.include_router(data.router)

    uvicorn.run(app, host="127.0.0.1", port=8000) 

if __name__ == "__main__":
    main()
