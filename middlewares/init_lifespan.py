import json
from fastapi import FastAPI
from datetime import timedelta, datetime
from contextlib import asynccontextmanager
from middlewares.image_searcher import ImageSemanticSearcher
from middlewares.knowledge_builder import KnowledgeGraphBuilder
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from apscheduler.triggers.interval import IntervalTrigger
# from apscheduler.triggers.cron import CronTrigger
#
# from databases.fastapi_sqlalchemy import AsyncDatabase, AsyncManageDataBase
# from databases.fastapi_redis import redis_connect
# from services.fetch_db_instance import SchoolFetcher
# from services.timer_tasks import flush_db_connection, update_server_functions, update_devices_info
# from services.db_conn_test import db_conn_test


@asynccontextmanager
async def tai_middleware(app: FastAPI):
    """
    FastAPI 应用的 lifespan 管理器，负责初始化和清理资源。

    :param app: FastAPI 应用实例
    """
    # 初始化资源
    image_searcher = ImageSemanticSearcher()
    app.state.image_searcher = image_searcher

    knowledge_graph = KnowledgeGraphBuilder()
    app.state.knowledge_graph = knowledge_graph
    try:
        yield  # 应用运行期间
    finally:
        pass

    # scheduler = AsyncIOScheduler()
    #
    # redis = await redis_connect()
    # app.state.redis = redis
    #
    # mysql = AsyncDatabase()
    # app.state.mysql = await mysql.get_sessions()
    # app.state.db_manager = mysql
    #
    # scheduler.add_job(update_server_functions,
    #                   IntervalTrigger(hours=24),
    #                   next_run_time=datetime.now(),
    #                   kwargs={"manage_mysql": app.state.manage_mysql, "redis_client": redis},  # 参数通过 kwargs 传
    #                   )
    #
    # scheduler.add_job(update_devices_info,
    #                   IntervalTrigger(hours=24),
    #                   next_run_time=datetime.now(),
    #                   kwargs={"manage_mysql": app.state.manage_mysql, "redis_client": redis}
    #                   )
    # scheduler.start()
    #
    # await db_conn_test(app.state.mysql)
    # try:
    #     yield  # 应用运行期间
    # finally:
    #     await app.state.redis.close()
    #     scheduler.shutdown()
    #     await mysql.dispose()
    #     print("redis 关闭")






