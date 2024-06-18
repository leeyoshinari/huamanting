import os
import shutil
import traceback
import logging.handlers
from fastapi import FastAPI
from fastapi import APIRouter, Request


app = FastAPI(docs_url=None, redoc_url=None, root_path='/api/openapi')
router = APIRouter(prefix='/file', tags=['file (文件)'], responses={404: {'description': 'Not found'}})


class Result:
    def __init__(self, code=0, msg='Success!', data=None):
        self.code = code
        self.msg = msg
        self.data = data


path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.join(path, 'data')
log_path = os.path.join(path, 'logs')
if not os.path.exists(log_path):
    os.mkdir(log_path)

log_level = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

logger = logging.getLogger()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(threadName)s - %(filename)s[line:%(lineno)d] - %(message)s')
logger.setLevel(level=log_level.get('INFO'))

file_handler = logging.handlers.TimedRotatingFileHandler(
    os.path.join(log_path, 'access.log'), when='midnight', interval=1, backupCount=7)
file_handler.suffix = '%Y-%m-%d.log'
# file_handler = logging.StreamHandler()
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


@router.post("/upload", summary="Upload files (上传文件)")
async def upload_file(query: Request):
    ip = query.headers.get('x-real-ip', '')
    result = Result()
    info = shutil.disk_usage(parent_path)
    if info.free < 5 * 1024 * 1024 * 1024:
        result.code = 2
        result.msg = "储存空间不足，请明天重试"
        return result
    query = await query.form()
    file_name = query['file'].filename
    data = query['file'].file
    try:
        file_path = os.path.join(parent_path, file_name)
        with open(file_path, 'wb') as f:
            f.write(data.read())
        result.msg = "上传成功"
        result.data = file_name
        logger.info(f"{file_name} 上传成功，IP: {ip}")
    except:
        result.code = 1
        result.data = file_name
        result.msg = "上传失败"
        logger.error(f"{file_name} 上传失败， IP: {ip}")
        logger.error(traceback.format_exc())
    return result


app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app="huamanting:app", host='127.0.0.1', port=12113, reload=False)