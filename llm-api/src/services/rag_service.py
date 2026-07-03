"""Local RAG service using ChromaDB and SentenceTransformers."""

from pathlib import Path
from typing import List, Dict, Any

import chromadb
from sentence_transformers import SentenceTransformer


class LocalRAGService:
    """Indexes local markdown/text files and retrieves relevant chunks."""

    def __init__(
        self,
        knowledge_base_dir: str = "data/knowledge_base",
        chroma_db_dir: str = "data/chroma_db",
        collection_name: str = "product_labeling_knowledge",
        embedding_model_name: str = "all-MiniLM-L6-v2",
    ):
        self.knowledge_base_dir = Path(knowledge_base_dir)
        self.chroma_db_dir = Path(chroma_db_dir)
        self.collection_name = collection_name

        self.embedding_model = SentenceTransformer(embedding_model_name)

        self.chroma_client = chromadb.PersistentClient(path=str(self.chroma_db_dir))
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name
        )

    def load_documents(self) -> List[Dict[str, Any]]:
        """Load markdown and text files from the knowledge base folder."""
        documents = []

        for file_path in self.knowledge_base_dir.rglob("*"):
            if file_path.suffix.lower() not in [".md", ".txt"]:
                continue

            text = file_path.read_text(encoding="utf-8")
            chunks = self._chunk_text(text)

            for index, chunk in enumerate(chunks):
                documents.append(
                    {
                        "id": f"{file_path.stem}-{index}",
                        "text": chunk,
                        "metadata": {
                            "source": str(file_path),
                            "chunk_index": index,
                        },
                    }
                )

        return documents

    def index_documents(self) -> int:
        """Index local documents into ChromaDB."""
        documents = self.load_documents()

        if not documents:
            return 0

        ids = [doc["id"] for doc in documents]
        texts = [doc["text"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]

        embeddings = self.embedding_model.encode(texts).tolist()

        existing = self.collection.get(ids=ids)
        existing_ids = set(existing.get("ids", []))

        new_ids = []
        new_texts = []
        new_metadatas = []
        new_embeddings = []

        for doc_id, text, metadata, embedding in zip(ids, texts, metadatas, embeddings):
            if doc_id in existing_ids:
                continue

            new_ids.append(doc_id)
            new_texts.append(text)
            new_metadatas.append(metadata)
            new_embeddings.append(embedding)

        if not new_ids:
            return 0

        self.collection.add(
            ids=new_ids,
            documents=new_texts,
            metadatas=new_metadatas,
            embeddings=new_embeddings,
        )

        return len(new_ids)

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search the vector database for relevant chunks."""
        query_embedding = self.embedding_model.encode([query]).tolist()[0]

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        matches = []

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for document, metadata, distance in zip(documents, metadatas, distances):
            matches.append(
                {
                    "text": document,
                    "metadata": metadata,
                    "distance": distance,
                }
            )

        return matches

    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """Split text into simple word-based chunks."""
        words = text.split()
        chunks = []

        for start in range(0, len(words), chunk_size):
            chunk = " ".join(words[start : start + chunk_size])
            if chunk.strip():
                chunks.append(chunk)

        return chunks
