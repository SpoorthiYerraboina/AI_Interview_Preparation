from pathlib import Path
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader
)


def load_documents():
    documents = []

    document_folder = Path("documents")

    for file in document_folder.iterdir():

        if file.suffix.lower() == ".txt":
            loader = TextLoader(str(file), encoding="utf-8")
            documents.extend(loader.load())

        elif file.suffix.lower() == ".pdf":
            loader = PyPDFLoader(str(file))
            documents.extend(loader.load())

    return documents


if __name__ == "__main__":
    docs = load_documents()

    print(f"Loaded {len(docs)} document(s)")

    for doc in docs:
        print(doc.page_content[:200])
        print("-" * 50)