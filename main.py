from fastapi import FastAPI

# Create FastAPI app instance
app = FastAPI()

@app.get("/")
def read_root():
    """
    Root endpoint for health check.
    Returns a welcome message.
    """
    return {"message": "Welcome to the Gen AI Inference APIs!"}
