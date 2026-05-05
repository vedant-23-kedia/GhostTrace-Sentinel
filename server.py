from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import os
import json
import shutil
import subprocess
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INDEX_PATH = os.path.join(BASE_DIR, "index.html")
CONTEXT_PATH = os.path.join(BASE_DIR, "current_context.json")
REPORT_PATH = os.path.join(BASE_DIR, "latest_report.json")
JUDGE_PATH = os.path.join(BASE_DIR, "judge_engine.py")


@app.get("/")
async def serve_ui():
    if not os.path.exists(INDEX_PATH):
        return JSONResponse(
            status_code=404,
            content={"error": "index.html not found in project folder"}
        )
    return FileResponse(INDEX_PATH)


@app.post("/api/login")
async def login(
    name: str = Form(None),
    dev_id: str = Form(None),
    team_name: str = Form(None),
    access_key: str = Form(None)
):
    operator_name = team_name or name
    key = access_key or dev_id

    if operator_name and key == "SENTINEL2026":
        return {
            "status": "success",
            "developer": operator_name
        }

    raise HTTPException(status_code=401, detail="Unauthorized")


@app.post("/api/sync")
async def sync_sentinel(
    requirements: str = Form(...),
    developer: str = Form(...),
    design_image: UploadFile = File(None)
):
    try:
        img_path = ""

        if design_image is not None and design_image.filename:
            ext = os.path.splitext(design_image.filename)[1]
            img_path = os.path.join(BASE_DIR, f"active_design{ext}")

            with open(img_path, "wb") as buffer:
                shutil.copyfileobj(design_image.file, buffer)

        context_data = {
            "developer": developer,
            "requirement": requirements,
            "image_path": img_path,
            "last_synced": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with open(CONTEXT_PATH, "w", encoding="utf-8") as f:
            json.dump(context_data, f, indent=4)

        return {
            "status": "success",
            "message": "Context synced successfully",
            "data": context_data
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "failed",
                "error": str(e)
            }
        )


@app.post("/api/audit")
async def run_audit():
    try:
        if not os.path.exists(JUDGE_PATH):
            return JSONResponse(
                status_code=404,
                content={
                    "status": "failed",
                    "error": "judge_engine.py not found"
                }
            )

        result = subprocess.run(
            ["python", JUDGE_PATH],
            capture_output=True,
            text=True,
            cwd=BASE_DIR
        )

        return {
            "status": "completed",
            "exit_code": result.returncode,
            "output": result.stdout,
            "error": result.stderr
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "failed",
                "error": str(e)
            }
        )


@app.get("/api/report")
async def get_report():
    if os.path.exists(REPORT_PATH):
        with open(REPORT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "status": "WAITING",
        "reason": "No audit has been run yet.",
        "developer": "GhostTrace Team",
        "timestamp": ""
    }


@app.post("/api/git-commit")
async def git_commit(commit_message: str = Form(...)):
    try:
        if not commit_message.strip():
            return JSONResponse(
                status_code=400,
                content={
                    "status": "failed",
                    "error": "Commit message cannot be empty"
                }
            )

        # Check if Git repo exists
        git_check = subprocess.run(
            ["git", "status"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=BASE_DIR
        )

        if git_check.returncode != 0:
            subprocess.run(
                ["git", "init"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=BASE_DIR
            )

        add_result = subprocess.run(
            ["git", "add", "."],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=BASE_DIR
        )

        commit_result = subprocess.run(
            ["git", "commit", "--no-verify", "-m", commit_message],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=BASE_DIR
        )

        return {
            "status": "completed",
            "git_add_output": add_result.stdout,
            "git_add_error": add_result.stderr,
            "commit_output": commit_result.stdout,
            "commit_error": commit_result.stderr,
            "exit_code": commit_result.returncode
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "failed",
                "error": str(e)
            }
        )