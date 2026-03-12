from fastapi import FastAPI, HTTPException

from .models import initialize, register_model, get_model
from .models.dummy_model import DummyModel

app = FastAPI()


# Register models (you can add more registrations here or in separate modules)
register_model(DummyModel.name, DummyModel(delay=0.01))

@app.on_event("startup")
def startup_event():
    """Initialize all registered models and load them into memory."""
    initialize()


@app.get("/predict")
def predict():
    """Run prediction using a registered model.

    Expects a JSON body: {"model": "name", "prompt": "text"}
    """
    # Look up the model by name (raises KeyError if not found)
    try:
        model_name = 'dummy'
        prompt = 'some prompt'
        model = get_model(model_name)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")

    # Ensure the model finished loading during startup
    if not model.is_loaded:
        raise HTTPException(status_code=503, detail=f"Model '{model_name}' not loaded")

    result = model.predict(prompt)
    return {"model": model_name, "result": result}


@app.get("/")
async def root():
    return {"message": "Hello World"}