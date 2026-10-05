from fastapi import FastAPI
from app.reviewer import review_repository

app = FastAPI(
    title="AI CI/CD Reviewer",
    version="1.0"
)


@app.get("/")
def root():
    return {
        "message": "AI CI/CD Reviewer is running"
    }

@app.post("/review")
def review():

    result = review_repository("test-data")

    return result

# @app.post("/review")
# def review():
#     return review_code("test-data/ai_test.py")