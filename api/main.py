import redis
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
import json
import os
from models import Base, VideosTable
from helpers import datetime_to_iso

# PostgreSQL Engine Setup
POSTGRES_URL = os.environ.get("POSTGRES_URL", None)
engine = create_engine(POSTGRES_URL)
Base.metadata.create_all(engine, checkfirst=True)
Session = sessionmaker(bind=engine)
session = Session()

# Redis Client Setup
redisClient = redis.Redis(
    os.environ.get("REDIS_HOST", "localhost"),
    port=os.environ.get("REDIS_PORT", 6379),
    db=os.environ.get("REDIS_DB", 0),
    decode_responses=True,
)

# Flask Setup
app = Flask(__name__)

# Flask-RESTful Setup
api = Api(app)


class Videos(Resource):
    def get(self):
        # Get Page URL Param
        page = request.args.get("page", 1, type=int)

        # Ensure page is at least 1
        page = max(1, page)

        # Check if page is cached
        cached_data = redisClient.get(f"{page}")
        if cached_data is not None:
            # Convert cached data to JSON and return it
            return jsonify(json.loads(cached_data))

        # Get videos from database
        count = session.query(VideosTable).count()

        pages = count // 20 + (1 if count % 20 > 0 else 0)
        page = min(page, pages)

        videos = (
            session.query(VideosTable)
            .order_by(desc(VideosTable.publishedAt))
            .limit(20)
            .offset((page - 1) * 20)
        )

        json_videos = []

        for video in videos:
            json_video = {
                "id": video.videoId,
                "title": video.title,
                "description": video.description,
                "thumbnail": video.thumbnail,
                "channelId": video.channelId,
                "channelTitle": video.channelTitle,
                "publishedAt": datetime_to_iso(video.publishedAt),
            }
            json_videos.append(json_video)

        content = {
            "info": {"currentPage": page, "maxPages": pages, "maxVideos": count},
            "videos": json_videos,
        }

        # Convert content to JSON and cache it
        redisClient.set(f"{page}", json.dumps(content))
        return jsonify(content)


api.add_resource(Videos, "/videos", endpoint="videos")
