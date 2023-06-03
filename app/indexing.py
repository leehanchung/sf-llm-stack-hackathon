import os
from typing import List

import redis
import pandas as pd
from langchain.document_loaders import CSVLoader
from langchain.vectorstores.redis import Redis
from langchain.schema import Document
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
import fire


load_dotenv()


CACHE_TYPE = os.getenv("CACHE_TYPE")
REDIS_URL = os.getenv("REDIS_URL")
OPENAI_COMPLETIONS_ENGINE = os.getenv("OPENAI_COMPLETIONS_ENGINE")
INDEX_NAME = os.getenv("INDEX_NAME")


def load_documents(*, csv_path: str = '../data/chats.csv') -> List[Document]:
    datasource = pd.read_csv(
        '../data/chats.csv'
    ).to_dict("records")

    chat_texts = [
        Document(
            page_content=doc["chat_text"],
            metadata={
                "channel_name": doc["channel_name"],
                "thread_id": doc["thread_id"],
            }
        ) for doc in datasource
    ]
    return chat_texts


def index_documents(*, csv_path: str = '../data/chats.csv'):
    chat_texts = load_documents(csv_path=csv_path)
    embeddings = OpenAIEmbeddings()
    vectorstore = Redis.from_documents(
        documents=chat_texts,
        embedding=embeddings,
        index_name='chat_index',
        redis_url=REDIS_URL,
    )


if __name__ == "__main__":
    fire.fire(index_documents)
