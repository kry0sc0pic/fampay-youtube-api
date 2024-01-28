from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class VideosTable(Base):
    __tablename__ = 'videos'
    videoId = Column(String, primary_key=True, nullable=False, unique=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    publishedAt = Column(Date, nullable=False)
    channelId = Column(String, nullable=False)
    channelTitle = Column(String, nullable=False)
