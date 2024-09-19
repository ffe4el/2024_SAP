import uvicorn
from fastapi import FastAPI
from markupsafe import escape
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 설정: 모든 출처 허용
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def index():
    return {"Hello": "World"}

@app.get("/hello/{name}")
def hello(name: str):
    return f"Hello, {escape(name)}!"

# 구구단 엔드포인트: 'dan' 파라미터를 받아서 구구단 결과 반환
@app.get("/gugudan/")
def gugudan(dan: int = 2):
    result = [f"{dan} x {i} = {dan * i}" for i in range(1, 10)]
    return {"구구단": result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
