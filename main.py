from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import csv
import io
import os

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

VALID_TOKEN = "6johsr3kr8z9t3tq"
MAX_SIZE = 52 * 1024  # 52KB
ALLOWED_EXTENSIONS = {".csv", ".json", ".txt"}


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    x_upload_token_7844: str = Header(None),
):
    # 1️⃣ Authentication
    if not x_upload_token_7844 or x_upload_token_7844 != VALID_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 2️⃣ File type validation
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type")

    # 3️⃣ File size validation
    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large")

    # 4️⃣ Process CSV only
    if ext == ".csv":
        text = contents.decode("utf-8")
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)

        columns = list(rows[0].keys()) if rows else []
        total_value = 0.0
        category_counts = {}

        for row in rows:
            if "value" in row:
                total_value += float(row["value"])
            if "category" in row:
                cat = row["category"]
                category_counts[cat] = category_counts.get(cat, 0) + 1

        return JSONResponse({
            "filename": filename,
            "rows": len(rows),
            "columns": columns,
            "totalValue": round(total_value, 2),
            "categoryCounts": category_counts,
        })

    # For json/txt (just accept)
    return JSONResponse({
        "filename": filename,
        "message": "File validated successfully"
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)