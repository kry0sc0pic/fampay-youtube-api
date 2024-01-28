import redis
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
import json
import os
from models import Base, VideosTable
from helpers import datetime_to_iso

# Get the environment variables
POSTGRES_URL = os.environ.get('POSTGRES_URL', None)
if POSTGRES_URL is None:
    print("POSTGRES_URL environment variable not set")
    exit(1)

# Create the engine to connect to the PostgreSQL database
engine = create_engine(POSTGRES_URL)
Base.metadata.create_all(engine, checkfirst=True)
Session = sessionmaker(bind=engine)
session = Session()

redisClient = redis.Redis(os.environ.get('REDIS_HOST','localhost'), port=os.environ.get('REDIS_PORT',6379), db=os.environ.get('REDIS_DB',0),decode_responses=True)


app = Flask(__name__)
api = Api(app)




def execution_time(f):
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        result = f(*args, **kwargs)
        end = time.time()
        print(f'{f.__name__} took {end - start} seconds')
        return result

    return wrapper

class Videos(Resource):
    @execution_time
    def get(self):
        page = request.args.get('page', 1, type=int)
        page = max(1, page)

        cachedData = redisClient.get(f'{page}')
        if cachedData is not None:
            return jsonify(json.loads(cachedData))


        count = session.query(VideosTable).count()
        pages = count // 20 + (1 if count % 20 > 0 else 0)
        page = min(page, pages)
        videos = session.query(VideosTable).order_by(desc(VideosTable.publishedAt)).limit(20).offset((page - 1) * 20)
        json_videos = []
        for video in videos:
            json_video = {'id': video.videoId, 'title': video.title, 'description': video.description,
                          'thumbnail': video.thumbnail, 'channelId': video.channelId, 'channelTitle': video.channelTitle,
                          'publishedAt': datetime_to_iso(video.publishedAt)}
            json_videos.append(json_video)
        content = {
                'info': {
                    'currentPage': page,
                    'maxPages': pages,
                    'maxVideos': count
                },
                'videos': json_videos
            }
        redisClient.set(f'{page}', json.dumps(content))
        return jsonify(content)


api.add_resource(Videos, '/videos', endpoint='videos')
