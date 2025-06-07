from pathlib import Path
from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from yt_dlp import YoutubeDL  # type: ignore
from settings.config import settings
import uuid
import json

router = APIRouter(tags=["Youtube Download"])

REDIS_QUEUE_KEY = "youtube_download_queue"
REDIS_STATUS_KEY = "youtube_download_statuses"

@router.post("/download")
def download(url: str, background_tasks: BackgroundTasks, request: Request):
    redis = request.app.state.redis
    task_id = str(uuid.uuid4())
    # 状態をセット
    redis.hset(REDIS_STATUS_KEY, task_id, json.dumps({"status": "queued", "error": None}))
    # キューに追加
    redis.rpush(REDIS_QUEUE_KEY, json.dumps({"task_id": task_id, "url": url}))
    # バックグラウンドで処理
    background_tasks.add_task(process_queue, request)
    return JSONResponse({"task_id": task_id, "message": "キューに登録しました"})

@router.get("/download/status")
def download_status(request: Request):
    redis = request.app.state.redis
    statuses = redis.hgetall(REDIS_STATUS_KEY)
    # JSONデコード
    return JSONResponse({k: json.loads(v) for k, v in statuses.items()})

def process_queue(request: Request):
    redis = request.app.state.redis
    while True:
        item = redis.lpop(REDIS_QUEUE_KEY)
        if not item:
            break
        data = json.loads(item)
        task_id = data["task_id"]
        url = data["url"]

        try:
            video_title = get_youtube_title(url)
            # 状態情報に動画タイトルを含めて保存
            redis.hset(REDIS_STATUS_KEY, task_id, json.dumps({
                "status": "processing",
                "error": None,
                "title": video_title
            }))
            download_youtube(url, settings.output_dir)
            redis.hset(REDIS_STATUS_KEY, task_id, json.dumps({
                "status": "done",
                "error": None,
                "title": video_title
            }))
        except Exception as e:
            # 例外時もタイトルを含めて保存
            redis.hset(REDIS_STATUS_KEY, task_id, json.dumps({
                "status": "error",
                "error": str(e),
                "title": video_title if 'video_title' in locals() else "unknown"
            }))


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
        
def get_youtube_title(url):
    with YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get("title", "unknown")
