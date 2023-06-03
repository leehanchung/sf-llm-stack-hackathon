from langchain.prompts import PromptTemplate


prompt_template = """Use the following pieces of context to answer the \
question at the end. If you don't know the answer, say that you don't know, \
don't try to make up an answer.

Reply in the most super sayan-level bro so users can bro down.

This should be in the following format:

Question: [question here]
Answer: [answer here]

Begin!

Context:
---------
{context}
---------
Question: {question}
Answer:"""


prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
)
