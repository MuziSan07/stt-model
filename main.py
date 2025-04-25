from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from db import init_db, create_token, revoke_token, renew_token, delete_token, get_db, get_token_by_value
from auth import validate_token
from asr import transcribe_audio
import shutil
import uuid
import db  # assuming your file is db.py

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
async def create_token(name: str = Form(...), rate_limit: int = Form(...)):
    db.create_token(name, rate_limit)
    return RedirectResponse(url="/admin", status_code=303)


# Token Actions
@app.post("/token/{token_id}/revoke")
def revoke_token_endpoint(token_id: str):
    revoke_token(token_id)
    return {"message": "Token revoked successfully"}

@app.post("/token/{token_id}/restore")
def restore_token_endpoint(token_id: str):
    from token_manager import restore_token
    restore_token(token_id)
    return {"message": "Token restored successfully"}

@app.post("/token/{token_id}/renew")
def renew_token_endpoint(token_id: str):
    renew_token(token_id)
    return {"message": "Token renewed successfully"}

@app.post("/token/{token_id}/delete")
def delete_token_endpoint(token_id: str):
    delete_token(token_id)
    return {"message": "Token deleted successfully"}

# Transcribe Audio Route
# @app.post("/transcribe/")
# def transcribe_audio_endpoint(token: str = Form(...), file: UploadFile = File(...)):
#     # Validate token
#     token_data = validate_token(token)
    
#     if not token_data:
#         raise HTTPException(status_code=403, detail="Invalid or inactive token.")
    
#     # Save the uploaded file temporarily
#     filename = f"temp_{uuid.uuid4()}.wav"
#     with open(filename, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     # Transcribe the audio
#     transcription = transcribe_audio(filename)

#     # Return transcription result
#     return {"transcription": transcription}

@app.get("/test", response_class=HTMLResponse)
def test_page(request: Request):
    return templates.TemplateResponse("test.html", {"request": request})

# @app.post("/transcribe/")
# async def transcribe_audio_endpoint(
#     request: Request,  # Move this argument before the others
#     token: str = Form(...),
#     file: UploadFile = File(...),
# ):
#     # Validate the token
#     token_data = validate_token(token)

#     if not token_data:
#         return templates.TemplateResponse("test.html", {
#             "request": request, "error": "Invalid or inactive token."
#         })

#     # Save the audio file temporarily
#     filename = f"temp_{uuid.uuid4()}.wav"
#     with open(filename, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     # Call the ASR model to transcribe the audio
#     transcription = transcribe_audio(filename)

#     # Return the transcription result
#     return templates.TemplateResponse("test.html", {
#         "request": request, "transcription": transcription
#     })
from token_manager import increment_call_count, update_token_usage, log_token_usage, is_token_rate_limited

# @app.post("/transcribe/")
# async def transcribe_audio_endpoint(
#     request: Request,
#     token: str = Form(...),
#     file: UploadFile = File(...),
# ):
#     token_data = validate_token(token)

#     if not token_data:
#         return templates.TemplateResponse("test.html", {
#             "request": request, "error": "Invalid or inactive token."
#         })

#     if is_token_rate_limited(token):
#         return templates.TemplateResponse("test.html", {
#             "request": request, "error": "Rate limit exceeded. Max 200 requests/hour."
#         })

#     filename = f"temp_{uuid.uuid4()}.wav"
#     with open(filename, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     transcription = transcribe_audio(filename)

#     # ✅ Update usage tracking
#     increment_call_count(token)
#     update_token_usage(token_data["id"])
#     log_token_usage(token)

#     return templates.TemplateResponse("test.html", {
#         "request": request, "transcription": transcription
#     })
# from fastapi.responses import JSONResponse
# @app.post("/transcribe/")
# async def transcribe_audio_endpoint(
#     token: str = Form(...),
#     file: UploadFile = File(...),
# ):
#     # 🔒 Token validation
#     token_data = validate_token(token)
#     if token_data is None:
#         return JSONResponse({"detail": "Invalid or inactive token."}, status_code=401)

#     # 🚫 Rate limit check
#     if is_token_rate_limited(token):
#         return JSONResponse({"detail": "Rate limit exceeded. Max 200 requests/hour."}, status_code=429)

#     # 💾 Save uploaded file temporarily
#     filename = f"temp_{uuid.uuid4()}.wav"
#     with open(filename, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     # 🧠 Run transcription
#     transcription = transcribe_audio(filename)

#     # 📊 Update usage tracking
#     increment_call_count(token)
#     update_token_usage(token_data["id"])
#     log_token_usage(token)

#     # ✅ Return JSON response
#     return JSONResponse({"transcription": transcription})


@app.post("/transcribe/")
async def transcribe_audio_endpoint(
    token: str = Form(...),
    file: UploadFile = File(...),
):
    # 🔒 Token validation (example, adjust validate_token logic as per your implementation)
    token_data = validate_token(token)
    if token_data is None:
        return {"detail": "Invalid or inactive token."}, 401

    # 🚫 Rate limit check (example, adjust rate limit check logic as per your implementation)
    if is_token_rate_limited(token):
        return {"detail": "Rate limit exceeded. Max 200 requests/hour."}, 429

    # 💾 Save uploaded file temporarily
    filename = f"temp_{uuid.uuid4()}.wav"
    with open(filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 🧠 Run transcription (example, replace with your actual transcription logic)
    transcription = transcribe_audio(filename)

    # 📊 Update usage tracking (example, update your token usage logic as needed)
    increment_call_count(token)
    update_token_usage(token_data["id"])
    log_token_usage(token)

    # ✅ Return plain JSON response with the transcription result
    return {
        "message": "Transcription completed successfully.",
        "transcription": transcription
    }
