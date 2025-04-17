from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from db import init_db, create_token, revoke_token, renew_token, delete_token, get_db, get_token_by_value
from auth import validate_token
from asr import transcribe_audio
import shutil
import uuid

app = FastAPI()

# Initialize the database
init_db()

templates = Jinja2Templates(directory="templates")

# Home Admin Dashboard
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    # Fetch all tokens from DB
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tokens")
    tokens = cursor.fetchall()
    return templates.TemplateResponse("admin.html", {"request": request, "tokens": tokens})

# Create new token
@app.post("/token/create")
def create_token_endpoint(name: str = Form(...)):
    token = create_token(name)
    return {"token": token}

# Token Actions
@app.post("/token/{token_id}/revoke")
def revoke_token_endpoint(token_id: str):
    revoke_token(token_id)
    return {"message": "Token revoked successfully"}

@app.post("/token/{token_id}/renew")
def renew_token_endpoint(token_id: str):
    renew_token(token_id)
    return {"message": "Token renewed successfully"}

@app.post("/token/{token_id}/delete")
def delete_token_endpoint(token_id: str):
    delete_token(token_id)
    return {"message": "Token deleted successfully"}

# Transcribe Audio Route
@app.post("/transcribe/")
def transcribe_audio_endpoint(token: str = Form(...), file: UploadFile = File(...)):
    # Validate token
    token_data = validate_token(token)
    
    if not token_data:
        raise HTTPException(status_code=403, detail="Invalid or inactive token.")
    
    # Save the uploaded file temporarily
    filename = f"temp_{uuid.uuid4()}.wav"
    with open(filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Transcribe the audio
    transcription = transcribe_audio(filename)

    # Return transcription result
    return {"transcription": transcription}

@app.get("/test", response_class=HTMLResponse)
def test_page(request: Request):
    return templates.TemplateResponse("test.html", {"request": request})

@app.post("/transcribe/")
async def transcribe_audio_endpoint(
    request: Request,  # Move this argument before the others
    token: str = Form(...),
    file: UploadFile = File(...),
):
    # Validate the token
    token_data = validate_token(token)

    if not token_data:
        return templates.TemplateResponse("test.html", {
            "request": request, "error": "Invalid or inactive token."
        })

    # Save the audio file temporarily
    filename = f"temp_{uuid.uuid4()}.wav"
    with open(filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Call the ASR model to transcribe the audio
    transcription = transcribe_audio(filename)

    # Return the transcription result
    return templates.TemplateResponse("test.html", {
        "request": request, "transcription": transcription
    })
