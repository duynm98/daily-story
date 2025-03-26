from celery import Celery, Task

from app import logger
from app.db.redis_db import database
from app.db.utils import export_status


# class GenerateStory(Task):
    
#     def on_success(self, retval, task_id, args, kwargs):
#         logger.success(f"Celery task {task_id} success!")
#         if database is None:
#             logger.warning("Database None")
#             return
#         moral = args[0]
#         database.set(task_id, export_status(id=task_id, status="SUCCESS", moral=moral, response=retval))

#     def on_failure(self, exc, task_id, args, kwargs, einfo):
#         logger.error(f"Celery task {task_id} failed: {exc}")
#         if database is None:
#             logger.w("Database None")
#             return
#         moral = args[0]
#         database.set(task_id, export_status(id=task_id, status="FAILED", moral=moral, response=exc))


# class GenerateVideo(Task):
#     def on_success(self, retval, task_id, args, kwargs):
#         logger.success(f"Celery task {task_id} success!")
#         if database is None:
#             logger.warning("Database None")
#             return
#         moral = args[0]
#         database.set(task_id, export_status(id=task_id, status="SUCCESS", moral=moral, response=retval))

#     def on_failure(self, exc, task_id, args, kwargs, einfo):
#         logger.error(f"Celery task {task_id} failed")
#         if database is None:
#             logger.w("Database None")
#             return
#         moral = args[0]
#         database.set(task_id, export_status(id=task_id, status="FAILED", moral=moral, response=exc))
