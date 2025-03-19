import socket
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/operation")
def hello_world() -> JSONResponse:
    data = {"Hello": "World"}
    return JSONResponse(data)


@router.get("/operation/ip")
def get_status() -> JSONResponse:
    host = socket.gethostname()
    ip = socket.gethostbyname(host)

    response = {"hostname": host, "ip": ip}
    return JSONResponse(response)

@router.get("/operation/gzip-test")
def gzip_test() -> JSONResponse:
    large_data = {"data": "x" * 10000}  # 大きなデータを生成
    return JSONResponse(large_data)