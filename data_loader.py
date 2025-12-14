import json
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv


load_dotenv()

DB_URL = f"postgresql+asyncpg://{os.getenv('DB_USER', 'user')}:{os.getenv('DB_PASS', 'pass')}@localhost:5432/video_analytics"

engine = create_async_engine(DB_URL, echo=False)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def apply_migrations():
    migration_path = "migrations/create_tables.sql"
    try:
        with open(migration_path, "r", encoding="utf-8") as f:
            sql_content = f.read()

        commands = [
            cmd.strip() + ";"
            for cmd in sql_content.split(";")
            if cmd.strip() and not cmd.strip().startswith("--")
        ]

        async with engine.begin() as conn:
            for cmd in commands:
                await conn.execute(text(cmd))

    except Exception as e:
        raise


async def load_data(json_file_path: str):
    await apply_migrations()
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    async with AsyncSessionLocal() as session:
        for video_data in data['videos']:
            #Вставка видео
            video_query = text("""
                               INSERT INTO videos (creator_id, video_created_at, views_count, likes_count,
                                                   comments_count, reports_count)
                               VALUES (:creator_id, :video_created_at, :views_count, :likes_count, :comments_count,
                                       :reports_count) RETURNING id
                               """)

            result = await session.execute(video_query,{
                'creator_id' : video_data['creator_id'],
                'video_created_at' : datetime.fromisoformat(video_data['video_created_at']),
                'views_count' : video_data['views_count'],
                'likes_count' : video_data['likes_count'],
                'comments_count' : video_data['comments_count'],
                'reports_count' : video_data['reports_count']
            })
            video_id = result.scalar()

            #вставка снапшотов
            for snapshots in video_data['snapshots']:
                snapshot_query = text("""
                                      INSERT INTO video_snapshots (video_id, views_count, likes_count, comments_count,
                                                                   reports_count,
                                                                   delta_views_count, delta_likes_count,
                                                                   delta_comments_count, delta_reports_count,
                                                                   created_at)
                                      VALUES (:video_id, :views_count, :likes_count, :comments_count, :reports_count,
                                              :delta_views_count, :delta_likes_count, :delta_comments_count,
                                              :delta_reports_count,
                                              :created_at)
                                      """)
                await session.execute(snapshot_query,{
                    'video_id' : video_id,
                    'views_count' : snapshots['views_count'],
                    **{k: snapshots[k] for k in ['likes_count', 'comments_count', 'reports_count', 'delta_views_count',
                       'delta_likes_count', 'delta_comments_count', 'delta_reports_count']},
                    'created_at' : datetime.fromisoformat(snapshots['created_at'])
                })
                await session.commit()

if __name__ == '__main__':
    asyncio.run(load_data("C:/video/videos.json"))