import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate


@st.cache_resource
def load_rag():

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = Chroma(
        persist_directory="data/chroma_db",
        embedding_function=embeddings
    )

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3}
    )

    llm = OllamaLLM(
        model="llama3.2:3b"
    )

    return retriever, llm


prompt = ChatPromptTemplate.from_template("""
You are an AI Interview Preparation Assistant.

Use the context when it is relevant to the question.
If the context is not relevant, answer using your general knowledge.

Context:
{context}

Question:
{question}

Give a short, clear and beginner-friendly answer.
""")


def ask_question(question):

    retriever, llm = load_rag()

    docs = retriever.invoke(question)

    context = "\n\n".join(
        doc.page_content for doc in docs
    )

    response = llm.invoke(
        prompt.format(
            context=context,
            question=question
        )
    )

    return response