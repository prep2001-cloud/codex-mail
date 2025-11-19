"""
Vector Store - Manages embeddings and semantic search
Supports ChromaDB and Pinecone
"""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from ..core.config import settings
from ..core.logger import get_logger

logger = get_logger(__name__)


class VectorStoreBase(ABC):
    """Abstract base class for vector stores"""

    @abstractmethod
    def add_documents(
        self,
        documents: List[str],
        metadata: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ):
        """Add documents to vector store"""
        pass

    @abstractmethod
    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        pass

    @abstractmethod
    def delete(self, ids: List[str]):
        """Delete documents by ID"""
        pass


class ChromaVectorStore(VectorStoreBase):
    """ChromaDB implementation of vector store"""

    def __init__(
        self,
        collection_name: str = "nexxbot_knowledge",
        persist_directory: str = "chroma_db"
    ):
        """
        Initialize ChromaDB vector store

        Args:
            collection_name: Name of the collection
            persist_directory: Directory to persist data
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory

        # Initialize ChromaDB client
        self.client = chromadb.Client(ChromaSettings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "NEXXBot knowledge base"}
        )

        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        logger.info(f"ChromaDB vector store initialized: {collection_name}")

    def add_documents(
        self,
        documents: List[str],
        metadata: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ):
        """
        Add documents to ChromaDB

        Args:
            documents: List of document texts
            metadata: Optional metadata for each document
            ids: Optional IDs for each document
        """
        if not documents:
            return

        # Generate IDs if not provided
        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in documents]

        # Generate embeddings
        embeddings = self.embedding_model.encode(documents).tolist()

        # Add to collection
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadata or [{} for _ in documents],
            ids=ids
        )

        logger.info(f"Added {len(documents)} documents to ChromaDB")

    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents

        Args:
            query: Search query
            n_results: Number of results to return
            filter_dict: Optional metadata filter

        Returns:
            List of search results with documents and metadata
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()[0]

        # Search in collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_dict
        )

        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    'document': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else 0,
                    'id': results['ids'][0][i] if results['ids'] else None
                })

        logger.debug(f"Found {len(formatted_results)} results for query")
        return formatted_results

    def delete(self, ids: List[str]):
        """
        Delete documents by ID

        Args:
            ids: List of document IDs to delete
        """
        self.collection.delete(ids=ids)
        logger.info(f"Deleted {len(ids)} documents from ChromaDB")

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "document_count": count,
            "persist_directory": self.persist_directory
        }


class VectorStore:
    """
    Main VectorStore interface - auto-selects backend based on config
    """

    def __init__(
        self,
        collection_name: str = "nexxbot_knowledge",
        backend: Optional[str] = None
    ):
        """
        Initialize vector store

        Args:
            collection_name: Name of the collection
            backend: Vector DB backend (chromadb or pinecone)
        """
        self.backend_type = backend or settings.VECTOR_DB_TYPE

        if self.backend_type == "chromadb":
            self.backend = ChromaVectorStore(collection_name=collection_name)
        elif self.backend_type == "pinecone":
            # TODO: Implement Pinecone backend
            logger.warning("Pinecone not implemented, falling back to ChromaDB")
            self.backend = ChromaVectorStore(collection_name=collection_name)
        else:
            raise ValueError(f"Unknown vector DB backend: {self.backend_type}")

        logger.info(f"VectorStore initialized with backend: {self.backend_type}")

    def add_sop_documents(self, sop_documents: List[Dict[str, str]]):
        """
        Add SOP (Standard Operating Procedure) documents

        Args:
            sop_documents: List of SOP documents with 'title' and 'content'
        """
        documents = [f"{doc['title']}\n\n{doc['content']}" for doc in sop_documents]
        metadata = [
            {
                "type": "sop",
                "title": doc['title'],
                "category": doc.get('category', 'general')
            }
            for doc in sop_documents
        ]

        self.backend.add_documents(documents, metadata)
        logger.info(f"Added {len(sop_documents)} SOP documents")

    def add_case_studies(self, cases: List[Dict[str, Any]]):
        """
        Add historical case studies / decision examples

        Args:
            cases: List of case study dictionaries
        """
        documents = [
            f"Problem: {case['problem']}\nSolution: {case['solution']}\nOutcome: {case['outcome']}"
            for case in cases
        ]
        metadata = [
            {
                "type": "case_study",
                "category": case.get('category', 'general'),
                "success": case.get('success', True)
            }
            for case in cases
        ]

        self.backend.add_documents(documents, metadata)
        logger.info(f"Added {len(cases)} case studies")

    def search_knowledge(
        self,
        query: str,
        n_results: int = 5,
        knowledge_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search knowledge base

        Args:
            query: Search query
            n_results: Number of results
            knowledge_type: Filter by type (sop, case_study, etc.)

        Returns:
            List of relevant knowledge items
        """
        filter_dict = {"type": knowledge_type} if knowledge_type else None
        return self.backend.search(query, n_results, filter_dict)

    def add_documents(self, documents: List[str], metadata: Optional[List[Dict]] = None):
        """Add generic documents"""
        self.backend.add_documents(documents, metadata)

    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search documents"""
        return self.backend.search(query, n_results)
