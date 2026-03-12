# FastAPI with Model Inference

A minimal FastAPI template for serving machine learning model predictions.

## Setup

1. **Create a virtual environment**  
   ```bash
   python3 -m venv env
   ```

2. **Activate the environment**  
   - On macOS / Linux:  
     ```bash
     source env/bin/activate
     ```
   - On Windows:  
     ```bash
     env\Scripts\activate
     ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

## Running the API

Start the FastAPI development server:

```bash
python3 -m fastapi dev main.py
```

The API will be available at `http://127.0.0.1:8000`.

## Testing

Once the server is running, test the prediction endpoint:

```bash
curl http://127.0.0.1:8000/predict
```

You should receive a JSON response with the model inference result.

---

For more details, refer to the code in `main.py` and the model loading logic.