"""Unit tests for ChromaRAG class."""

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from chroma_rag import ChromaRAG
from constants import EmbeddingModel


class TestChromaRAGInitialization(unittest.TestCase):
    """Test ChromaRAG initialization."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_chroma_rag_initialization_with_defaults(self):
        """Test ChromaRAG initialization with default parameters."""
        with patch("chroma_rag.chromadb.PersistentClient"):
            rag = ChromaRAG(persist_directory=self.test_dir)
            self.assertEqual(rag.persist_directory, self.test_dir)
            self.assertEqual(rag.collection_name, "documents")
            self.assertEqual(rag.hnsw_space, "cosine")

    def test_chroma_rag_initialization_with_custom_params(self):
        """Test ChromaRAG initialization with custom parameters."""
        with patch("chroma_rag.chromadb.PersistentClient"):
            rag = ChromaRAG(
                persist_directory=self.test_dir,
                collection_name="custom_collection",
                embedding_model="default",
                hnsw_space="l2",
            )
            self.assertEqual(rag.collection_name, "custom_collection")
            self.assertEqual(rag.hnsw_space, "l2")

    def test_chroma_rag_creates_persist_directory(self):
        """Test that ChromaRAG creates persist directory if it doesn't exist."""
        persist_dir = os.path.join(self.test_dir, "new_chroma_data")
        self.assertFalse(os.path.exists(persist_dir))

        with patch("chroma_rag.chromadb.PersistentClient"):
            rag = ChromaRAG(persist_directory=persist_dir)
            self.assertTrue(os.path.exists(persist_dir))

    def test_chroma_rag_embedding_model_default(self):
        """Test that ChromaRAG handles default embedding model."""
        with patch("chroma_rag.chromadb.PersistentClient"):
            with patch("chroma_rag.embedding_functions.DefaultEmbeddingFunction"):
                rag = ChromaRAG(
                    persist_directory=self.test_dir, embedding_model="default"
                )
                self.assertIsNotNone(rag.embedding_fn)

    def test_chroma_rag_embedding_model_sentence_transformer(self):
        """Test that ChromaRAG handles SentenceTransformer embedding model."""
        with patch("chroma_rag.chromadb.PersistentClient"):
            with patch(
                "chroma_rag.embedding_functions.SentenceTransformerEmbeddingFunction"
            ):
                rag = ChromaRAG(
                    persist_directory=self.test_dir,
                    embedding_model=EmbeddingModel.MINI_LM,
                )
                self.assertIsNotNone(rag.embedding_fn)


class TestChromaRAGDocumentManagement(unittest.TestCase):
    """Test document management operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.mock_client = MagicMock()
        self.mock_collection = MagicMock()
        self.mock_client.get_or_create_collection.return_value = self.mock_collection

    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch("chroma_rag.chromadb.PersistentClient")
    def test_add_documents(self, mock_client_class):
        """Test adding documents to the collection."""
        mock_client_class.return_value = self.mock_client

        rag = ChromaRAG(persist_directory=self.test_dir)
        documents = ["Document 1", "Document 2", "Document 3"]

        rag.add_documents(documents)

        self.mock_collection.add.assert_called_once()
        call_args = self.mock_collection.add.call_args
        self.assertEqual(call_args[1]["documents"], documents)

    @patch("chroma_rag.chromadb.PersistentClient")
    def test_add_documents_with_metadata(self, mock_client_class):
        """Test adding documents with metadata."""
        mock_client_class.return_value = self.mock_client

        rag = ChromaRAG(persist_directory=self.test_dir)
        documents = ["Document 1", "Document 2"]
        metadata = [{"source": "test1"}, {"source": "test2"}]

        rag.add_documents(documents, metadata=metadata)

        call_args = self.mock_collection.add.call_args
        self.assertEqual(call_args[1]["metadatas"], metadata)

    @patch("chroma_rag.chromadb.PersistentClient")
    def test_add_documents_with_custom_ids(self, mock_client_class):
        """Test adding documents with custom IDs."""
        mock_client_class.return_value = self.mock_client

        rag = ChromaRAG(persist_directory=self.test_dir)
        documents = ["Document 1", "Document 2"]
        custom_ids = ["id_1", "id_2"]

        rag.add_documents(documents, ids=custom_ids)

        call_args = self.mock_collection.add.call_args
        self.assertEqual(call_args[1]["ids"], custom_ids)

    @patch("chroma_rag.chromadb.PersistentClient")
    def test_add_documents_generates_ids(self, mock_client_class):
        """Test that add_documents generates IDs if not provided."""
        mock_client_class.return_value = self.mock_client

        rag = ChromaRAG(persist_directory=self.test_dir)
        documents = ["Document 1", "Document 2"]

        rag.add_documents(documents)

        call_args = self.mock_collection.add.call_args
        ids = call_args[1]["ids"]
        self.assertEqual(len(ids), 2)

    @patch("chroma_rag.chromadb.PersistentClient")
    def test_delete_document(self, mock_client_class):
        """Test deleting a document by ID."""
        mock_client_class.return_value = self.mock_client

        rag = ChromaRAG(persist_directory=self.test_dir)
        rag.delete_document("doc_123")

        self.mock_collection.delete.assert_called_once_with(ids=["doc_123"])

    @patch("chroma_rag.chromadb.PersistentClient")
    def test_clear_collection(self, mock_client_class):
        """Test clearing all documents from collection."""
        mock_client_class.return_value = self.mock_client
        self.mock_collection.get.return_value = {
            "ids": ["doc_1", "doc_2", "doc_3"]
        }

        rag = ChromaRAG(persist_directory=self.test_dir)
        rag.clear_collection()

        self.mock_collection.delete.assert_called_once()
        self.assertEqual(self.mock_collection.delete.call_args[1]["ids"], 
                         ["doc_1", "doc_2", "doc_3"])

    @patch("chroma_rag.chromadb.PersistentClient")
    def test_get_collection_stats(self, mock_client_class):
        """Test getting collection statistics."""
        mock_client_class.return_value = self.mock_client
        self.mock_collection.count.return_value = 42

        rag = ChromaRAG(persist_directory=self.test_dir, collection_name="test_docs")
        stats = rag.get_collection_stats()

        self.assertEqual(stats["collection_name"], "test_docs")
        self.assertEqual(stats["document_count"], 42)
        self.assertEqual(stats["persist_directory"], self.test_dir)


class TestChromaRAGRetrieval(unittest.TestCase):
    """Test document retrieval operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.mock_client = MagicMock()
        self.mock_collection = MagicMock()
        self.mock_client.get_or_create_collection.return_value = self.mock_collection

    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch("chroma_rag.chromadb.PersistentClient")
    def test_retrieve_documents(self, mock_client_class):
        """Test retrieving documents."""
        mock_client_class.return_value = self.mock_client
        self.mock_collection.query.return_value = {
            "documents": [["doc1", "doc2"]],
            "distances": [[0.1, 0.2]],
            "metadatas": [[{"source": "test"}]],
            "ids": [["id1", "id2"]],
        }

        rag = ChromaRAG(persist_directory=self.test_dir)
        results = rag.retrieve("test query", k=2)

        self.assertEqual(len(results["documents"]), 2)
        self.assertEqual(results["documents"], ["doc1", "doc2"])
        self.assertEqual(results["distances"], [0.1, 0.2])

    @patch("chroma_rag.chromadb.PersistentClient")
    def test_retrieve_with_scores(self, mock_client_class):
        """Test retrieving documents with similarity scores."""
        mock_client_class.return_value = self.mock_client
        self.mock_collection.query.return_value = {
            "documents": [["doc1", "doc2"]],
            "distances": [[0.1, 0.3]],
            "metadatas": [[{"source": "test1"}, {"source": "test2"}]],
            "ids": [["id1", "id2"]],
        }

        rag = ChromaRAG(persist_directory=self.test_dir)
        results = rag.retrieve_with_scores("test query", k=2)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["document"], "doc1")
        self.assertEqual(results[0]["similarity_score"], 1 - 0.1)  # 0.9
        self.assertEqual(results[1]["similarity_score"], 1 - 0.3)  # 0.7

    @patch("chroma_rag.chromadb.PersistentClient")
    def test_retrieve_empty_results(self, mock_client_class):
        """Test retrieving when no documents match."""
        mock_client_class.return_value = self.mock_client
        self.mock_collection.query.return_value = {
            "documents": [[]],
            "distances": [[]],
            "metadatas": [[]],
            "ids": [[]],
        }

        rag = ChromaRAG(persist_directory=self.test_dir)
        results = rag.retrieve("unknown query", k=5)

        self.assertEqual(results["documents"], [])
        self.assertEqual(results["distances"], [])


class TestChromaRAGFilePersistence(unittest.TestCase):
    """Test file persistence operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test_document.txt")
        with open(self.test_file, "w") as f:
            f.write("This is a test document.\n\nWith multiple paragraphs.")

        self.mock_client = MagicMock()
        self.mock_collection = MagicMock()
        self.mock_client.get_or_create_collection.return_value = self.mock_collection

    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch("chroma_rag.chromadb.PersistentClient")
    @patch("chroma_rag.MarkdownTextSplitter")
    def test_add_documents_from_file(self, mock_splitter_class, mock_client_class):
        """Test adding documents from a file."""
        mock_client_class.return_value = self.mock_client
        mock_splitter = MagicMock()
        mock_splitter_class.return_value = mock_splitter
        mock_splitter.split_text.return_value = ["chunk1", "chunk2"]

        rag = ChromaRAG(persist_directory=self.test_dir)
        rag.add_documents_from_file(self.test_file, chunk_size=500, chunk_overlap=50)

        self.mock_collection.add.assert_called_once()
        call_args = self.mock_collection.add.call_args
        self.assertEqual(len(call_args[1]["documents"]), 2)

    @patch("chroma_rag.chromadb.PersistentClient")
    @patch("chroma_rag.MarkdownTextSplitter")
    def test_add_documents_from_file_with_metadata(
        self, mock_splitter_class, mock_client_class
    ):
        """Test adding documents from file with metadata."""
        mock_client_class.return_value = self.mock_client
        mock_splitter = MagicMock()
        mock_splitter_class.return_value = mock_splitter
        mock_splitter.split_text.return_value = ["chunk1"]

        metadata = {"category": "test"}
        rag = ChromaRAG(persist_directory=self.test_dir)
        rag.add_documents_from_file(
            self.test_file, chunk_size=500, chunk_overlap=50, metadata=metadata
        )

        call_args = self.mock_collection.add.call_args
        added_metadata = call_args[1]["metadatas"][0]
        self.assertIn("category", added_metadata)
        self.assertEqual(added_metadata["category"], "test")

    @patch("chroma_rag.chromadb.PersistentClient")
    def test_add_documents_from_nonexistent_file(self, mock_client_class):
        """Test adding documents from a file that doesn't exist."""
        mock_client_class.return_value = self.mock_client

        rag = ChromaRAG(persist_directory=self.test_dir)

        with self.assertRaises(Exception):
            rag.add_documents_from_file("/nonexistent/path/to/file.txt")

    @patch("chroma_rag.chromadb.PersistentClient")
    def test_persist(self, mock_client_class):
        """Test persisting the database."""
        mock_client_class.return_value = self.mock_client
        mock_persist = MagicMock()
        self.mock_client.persist = mock_persist

        rag = ChromaRAG(persist_directory=self.test_dir)
        rag.persist()

        mock_persist.assert_called_once()


if __name__ == "__main__":
    unittest.main()
