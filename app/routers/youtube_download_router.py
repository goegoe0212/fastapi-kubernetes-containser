from pathlib import Path
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse
from yt_dlp import YoutubeDL  # type: ignore
from settings.config import settings
import uuid
import queue


router = APIRouter(tags=["Youtube Download"])

download_queue = queue.Queue() # type: ignore
download_statuses = {}


@router.post("/download")
def download(url: str, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    download_statuses[task_id] = {"status": "queued", "error": None}
    download_queue.put((task_id, url))
    background_tasks.add_task(process_queue)
    return JSONResponse({"task_id": task_id, "message": "キューに登録しました"})


@router.get("/download/status")
def download_status():
    return JSONResponse(download_statuses)


def process_queue():
    while not download_queue.empty():
        task_id, url = download_queue.get()
        download_statuses[task_id]["status"] = "processing"
        try:
            download_youtube(url, settings.output_dir)
            download_statuses[task_id]["status"] = "done"
        except Exception as e:
            download_statuses[task_id]["status"] = "error"
            download_statuses[task_id]["error"] = str(e)


def download_youtube(url, output_dir):
    path_out_dir = Path(output_dir)
    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": str(path_out_dir / "%(title)s.mp4"),
        "merge_output_format": "mp4",
        "postprocessors": [],
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
