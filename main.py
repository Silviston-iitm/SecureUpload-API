from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pathlib import Path
import io

app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Constants
EXPECTED_TOKEN = "84y69useinziis0"
ALLOWED_EXTENSIONS = {".csv", ".json", ".txt"}
MAX_FILE_SIZE = 93 * 1024  # 93KB


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    x_upload_token_1848: str = Header(
        ...,  # Required header
        alias="X-Upload-Token-1848"  # Exact header name expected
    )
):
    # 🔐 1️⃣ Authentication
    if x_upload_token_1848 != EXPECTED_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 📄 2️⃣ Validate file extension
    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type")

    # 📦 3️⃣ Validate file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")

    # 📊 4️⃣ Process CSV
    if extension == ".csv":
        try:
            df = pd.read_csv(io.BytesIO(contents))

            required_columns = {"id", "name", "value", "category"}
            if not required_columns.issubset(set(df.columns)):
                raise HTTPException(status_code=400, detail="Missing required columns")

            total_value = float(df["value"].sum())
            category_counts = df["category"].value_counts().to_dict()

            return {
                "email": "24f1002710@ds.study.iitm.ac.in",
                "filename": file.filename,
                "rows": len(df),
                "columns": list(df.columns),
                "totalValue": total_value,
                "categoryCounts": category_counts,
            }

        except Exception:
            raise HTTPException(status_code=400, detail="Invalid CSV content")

    # For .json and .txt (just validate)
    return {"message": "File validated successfully"}