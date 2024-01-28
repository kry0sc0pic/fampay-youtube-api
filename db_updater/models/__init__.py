from sqlalchemy import Column, String, TIMESTAMP
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class VideosTable(Base):
    __tablename__ = 'videos'
    videoId = Column(String, primary_key=True, nullable=False, unique=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    publishedAt = Column(TIMESTAMP, nullable=False)
    channelId = Column(String, nullable=False)
    channelTitle = Column(String, nullable=False)
    thumbnail = Column(String, nullable=False)
