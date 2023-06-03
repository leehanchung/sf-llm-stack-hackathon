import os
import streamlit as st
import langchain
import os
from typing import List

import redis
from langchain.vectorstores.redis import Redis
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
from urllib.error import URLError

from prompts import prompt

load_dotenv()


CACHE_TYPE = os.getenv("CACHE_TYPE")
REDIS_URL = os.getenv("REDIS_URL")
OPENAI_COMPLETIONS_ENGINE = os.getenv("OPENAI_COMPLETIONS_ENGINE")
INDEX_NAME = os.getenv("INDEX_NAME")



llm = OpenAI()
embeddings = OpenAIEmbeddings()
vectorstore = Redis.from_existing_index(
    redis_url=REDIS_URL,
    index_name='chat_index',
    embedding=embeddings,
)
chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(),
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt}
)


try:
    default_question = ""
    default_answer = ""

    if 'question' not in st.session_state:
        st.session_state['question'] = default_question
    if 'response' not in st.session_state:
        st.session_state['response'] = {
            "choices" :[{
                "text" : default_answer
            }]
        }

    st.image(os.path.join('assets','events.png'))

    st.write("# Ask the MLOps Community")
    

    question = st.text_input("*There's no stupid questions, only stupid people*", default_question)

    if question != '':
        if question != st.session_state['question']:
            st.session_state['question'] = question
            with st.spinner("OpenAI and Redis are working to answer your question..."):
                result = chain({"query": question})
                st.session_state['context'], st.session_state['response'] = result['source_documents'], result['result']
            st.write("### Response")
            st.write(f"{st.session_state['response']}")
            with st.expander("Show Q&A Context Documents"):
                if st.session_state['context']:
                    docs = "\n".join([doc.page_content for doc in st.session_state['context']])
                    st.text(docs)

    st.markdown("____")
    st.markdown("")
    st.write("## How does it work?")
    st.write("""
        The Q&A app exposes a dataset of Slack chat history hosted by [MLOps Community](https://mlops.community/). Ask questions like
        *"What is the best way to train models for tabular data?"* or *"How can I structure a good Data Science team?"*, and get answers!

        Everything is powered by OpenAI's embedding and generation APIs and [Redis](https://redis.com/redis-enterprise-cloud/overview/) as a vector database.

        There are 3 main steps:

        1. OpenAI's embedding service converts the input question into a query vector (embedding).
        2. Redis' vector search identifies relevant wiki articles in order to create a prompt.
        3. OpenAI's generative model answers the question given the prompt+context.

        See the reference architecture diagram below for more context.
    """)



except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
        """
        % e.reason
    )