import streamlit as st
from models import Base, VideosTable
from sqlalchemy import create_engine, desc, and_
from sqlalchemy.orm import sessionmaker
import os
import datetime as dt

st.header(f"Query: `financial news`")
st.sidebar.header("YouTube API Dashboard")
POSTGRES_URL = os.environ.get("POSTGRES_URL")

engine = create_engine(POSTGRES_URL)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

st.session_state.filters = {'channelTitle': [], 'publishedAfter': None}

base_query = session.query(VideosTable).order_by(desc(VideosTable.publishedAt))
channels = session.query(VideosTable.channelTitle).distinct().all()

st.sidebar.write("**Filters**")

options = st.sidebar.multiselect("Channel", set([channel[0] for channel in channels]), )
st.sidebar.write("Published After")

dt_edited = False


def set_edited():
    global dt_edited
    dt_edited = True


date = st.sidebar.date_input("Date", format="DD/MM/YYYY", value=dt.date(2020, 1, 1),disabled=True)
time = st.sidebar.time_input("Time", value=dt.time(0, 0), disabled=True)
st.sidebar.write("*date and time filters are disabled since they are having issues*")

if True:
    if options == [] and (date == dt.date(2020, 1, 1) and time == dt.time(0, 0)):
        print("no filters")
        count = base_query.count()
        page = st.sidebar.number_input("Page", min_value=1, max_value=(count // 20 + (0 if count % 20 == 0 else 1)),
                                       value=1)
        result = base_query.limit(20).offset((page - 1) * 20).all()
        for video in result:
            col1, col2 = st.columns(2)
            col1.image(video.thumbnail)
            col2.write(f"**{video.title}**")
            col2.write(f"`{video.publishedAt.strftime('%d/%m/%Y %H:%M:%S UTC')}`")
            col2.write(f"{video.channelTitle}")
            col2.expander("Description").write(video.description)


    else:
        print("filters")
        filtered_query = base_query
        if options != [] and (date == dt.date(2020, 1, 1) and time == dt.time(0, 0)):
            print("channel")
            filtered_query = base_query.filter(VideosTable.channelTitle.in_(options))
        elif options == [] and (ts:=dt.datetime.combine(date, time)) != dt.datetime(2020, 1, 1, 0, 0):
            print("date")
            filtered_query = filtered_query.filter(VideosTable.publishedAt > ts)
        else:
            print("both")
            filtered_query = filtered_query.filter(and_(VideosTable.channelTitle.in_(options),
                                                        VideosTable.publishedAt > dt.datetime.combine(date, time)))
        count = filtered_query.count()
        page = st.sidebar.number_input("Page", min_value=1, max_value=(count // 20 + (0 if count % 20 == 0 else 1)),
                                       value=1)
        result = filtered_query.limit(20).offset((page - 1) * 20).all()
        for video in result:
            col1, col2 = st.columns(2)
            col1.image(video.thumbnail)
            col2.write(f"**{video.title}**")
            col2.write(f"`{video.publishedAt.strftime('%d/%m/%Y %H:%M:%S UTC')}`")
            col2.write(f"{video.channelTitle}")
            col2.expander("Description").write(video.description)
