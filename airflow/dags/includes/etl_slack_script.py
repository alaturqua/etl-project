import json
# Enable debug logging
import logging
import os
import warnings

import matplotlib.pyplot as plot
import pandas as pd

warnings.filterwarnings('ignore')
import json
import os
import time
from datetime import datetime
from time import sleep
from pathlib import Path

import pandas as pd
import psycopg2
import slack
from slack_sdk import WebClient

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)

def extract_data():
    logger.info("Extracting data from slack.")
    logger.debug("Getting token from environment variable")
    token = os.getenv("SLACK_TOKEN")

    CHANNEL = "GV5TKSZ1P"
    MESSAGES_PER_PAGE = 200
    MAX_MESSAGES = 5000

    # init web client
    client = slack.WebClient(token=token)

    # get first page
    page = 1
    print("Retrieving page {}".format(page))
    response = client.conversations_history(
        channel=CHANNEL,
        limit=MESSAGES_PER_PAGE,
    )
    assert response["ok"]
    messages_all = response['messages']

    # get additional pages if below max message and if they are any
    while len(messages_all) + MESSAGES_PER_PAGE <= MAX_MESSAGES and response['has_more']:
        page += 1
        print("Retrieving page {}".format(page))
        sleep(1)   # need to wait 1 sec before next call due to rate limits
        response = client.conversations_history(
            channel=CHANNEL,
            limit=MESSAGES_PER_PAGE,
            cursor=response['response_metadata']['next_cursor']
        )
        assert response["ok"]
        messages = response['messages']
        messages_all = messages_all + messages

    
    print(
        "Fetched a total of {} messages from channel {}".format(
            len(messages_all),
            CHANNEL
    ))

    timestr = time.strftime("%Y-%m-%d")
    folder_path = "/data/parquet"
    Path(folder_path).mkdir(parents=True, exist_ok=True)
    parquet_file_path = f"{folder_path}/timesheet_{timestr}.parquet"
    logger.info(f"Creating parquet file on: {parquet_file_path}")
    
    df = pd.DataFrame(messages_all)
    df_result = df[["user", "text", "ts"]]
    df_result.columns = ["user_name", "user_message", "ts"]
    logger.info(df_result.head(10))
    df_result.to_parquet(parquet_file_path)
    
    return parquet_file_path

def extract_user_list():
    token = os.getenv("SLACK_TOKEN")
    client = slack.WebClient(token=token)
    users_list = client.users_list()
    timestr = time.strftime("%Y-%m-%d")
    folder_path = "/data/parquet"
    Path(folder_path).mkdir(parents=True, exist_ok=True)
    parquet_file_path = f"{folder_path}/timesheet_{timestr}.parquet"

    df = pd.json_normalize(users_list.data['members'])[['id', 'name', 'real_name']]
    df['ts'] = datetime.now()
    logger.info(df.head(10))
    df.to_parquet(parquet_file_path)
    return parquet_file_path
    


def load_data_to_postgres(file_path):
    from sqlalchemy import create_engine
    
    alchemy_engine = create_engine('postgresql+psycopg2://airflow:airflow@postgres-dwh:5432/postgres')

    df = pd.read_parquet(file_path)
    df["ts"] = pd.to_datetime(df['ts'],unit='s')
    logger.info(df.head(10))
    df.to_sql(name="timesheet", schema="public", con=alchemy_engine, if_exists="replace")
    
    return "Success"

def load_user_list_to_postgres(file_path):
    from sqlalchemy import create_engine
    
    alchemy_engine = create_engine('postgresql+psycopg2://airflow:airflow@postgres-dwh:5432/postgres')

    df = pd.read_parquet(file_path)
    logger.info(df.head(10))
    df.to_sql(name="users_list", schema="public", con=alchemy_engine, if_exists="replace")
    
    return "Success"

