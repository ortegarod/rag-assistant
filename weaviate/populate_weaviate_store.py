import weaviate
from pathlib import Path
import logging
from typing import List, Dict
import os
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def document_exists(client: weaviate.Client, source: str) -> bool:
    try:
        query = (
            client.query
            .get("Document", ["source"])
            .with_where({
                "path": ["source"],
                "operator": "Equal",
                "valueString": source
            })
            .do()
        )

        logger.debug(f"Query response for document_exists: {query}")

        if 'data' not in query:
            logger.error(f"Unexpected query response structure: {query}")
            return False

        if 'Get' not in query['data']:
            logger.error(f"'Get' not found in query response data: {query['data']}")
            return False

        if 'Document' not in query['data']['Get']:
            logger.error(f"'Document' not found in Get data: {query['data']['Get']}")
            return False

        return len(query['data']['Get']['Document']) > 0
    except Exception as e:
        logger.error(f"Error checking if document exists: {str(e)}")
        logger.exception("Full traceback:")
        return False


def update_document(client: weaviate.Client, source: str, content: str) -> None:
    try:
        query = (
            client.query
            .get("Document", ["id"])
            .with_where({
                "path": ["source"],
                "operator": "Equal",
                "valueString": source
            })
            .do()
        )

        logger.debug(f"Query response for update: {query}")

        if 'data' not in query:
            logger.error(f"Unexpected query response structure: {query}")
            return

        if 'Get' not in query['data']:
            logger.error(f"'Get' not found in query response data: {query['data']}")
            return

        if 'Document' not in query['data']['Get']:
            logger.error(f"'Document' not found in Get data: {query['data']['Get']}")
            return

        documents = query['data']['Get']['Document']

        if not documents:
            logger.warning(f"No document found with source: {source}")
            return

        doc_id = documents[0]['id']
        client.data_object.update(
            uuid=doc_id,
            class_name="Document",
            data_object={
                "content": content,
                "source": source
            }
        )
        logger.info(f"Updated document: {source}")
    except Exception as e:
        logger.error(f"Error updating document {source}: {str(e)}")
        logger.exception("Full traceback:")

def create_schema(client: weaviate.Client) -> None:
    """
    Create the Weaviate schema if it doesn't exist.

    :param client: Weaviate client instance
    """
    schema = client.schema.get()
    if "Document" not in [class_obj["class"] for class_obj in schema["classes"]]:
        class_obj = {
            "class": "Document",
            "properties": [
                {"name": "content", "dataType": ["text"]},
                {"name": "source", "dataType": ["string"]}
            ]
        }
        client.schema.create_class(class_obj)
        logger.info("Created 'Document' schema in Weaviate.")


def read_documents(documents_dir: str) -> List[Dict[str, str]]:
    """
    Read documents from the specified directory.

    :param documents_dir: Path to the directory containing documents
    :return: List of dictionaries containing document content and source
    """
    documents = []
    for file_path in Path(documents_dir).glob('*'):
        if file_path.is_file():
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    documents.append({
                        "content": content,
                        "source": file_path.name
                    })
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
    return documents


def add_or_update_documents_to_weaviate(client: weaviate.Client, documents: List[Dict[str, str]]) -> None:
    """
    Add new documents to Weaviate or update existing ones.

    :param client: Weaviate client instance
    :param documents: List of documents to add or update
    """
    added_count = 0
    updated_count = 0
    for document in documents:
        if document_exists(client, document['source']):
            update_document(client, document['source'], document['content'])
            updated_count += 1
        else:
            client.data_object.create(
                data_object=document,
                class_name="Document"
            )
            added_count += 1

    logger.info(f"Added {added_count} new documents and updated {updated_count} existing documents in Weaviate.")


def query_all_documents(client: weaviate.Client) -> List[Dict[str, str]]:
    """
    Query all documents from Weaviate.

    :param client: Weaviate client instance
    :return: List of all documents in Weaviate
    """
    try:
        query = (
            client.query
            .get("Document", ["content", "source"])
            .with_limit(10000)  # Adjust this number based on your expected document count
            .do()
        )

        # Log the full response for debugging
        logger.debug(f"Full Weaviate response: {query}")

        if 'data' not in query:
            logger.error(f"Unexpected response structure: {query}")
            return []

        if 'Get' not in query['data']:
            logger.error(f"'Get' not found in response data: {query['data']}")
            return []

        if 'Document' not in query['data']['Get']:
            logger.error(f"'Document' not found in Get data: {query['data']['Get']}")
            return []

        return query['data']['Get']['Document']
    except Exception as e:
        logger.error(f"Error querying documents from Weaviate: {str(e)}")
        return []


def create_and_populate_document_store(documents_dir: str) -> None:
    """
    Create Weaviate schema, populate it with documents, and then query all documents.

    :param documents_dir: Path to the directory containing documents
    """
    try:
        # Initialize Weaviate client
        client = weaviate.Client(os.getenv("WEAVIATE_URL", "http://localhost:8080"))

        # Create schema
        create_schema(client)

        # Read documents
        documents = read_documents(documents_dir)

        if documents:
            # Add or update documents in Weaviate
            add_or_update_documents_to_weaviate(client, documents)
        else:
            logger.warning("No documents found in the specified directory.")

        # Query all documents from Weaviate
        all_documents = query_all_documents(client)

        logger.info(f"Total documents in Weaviate: {len(all_documents)}")
        for i, doc in enumerate(all_documents, 1):
            logger.info(f"Document {i}:")
            logger.info(f"  Source: {doc['source']}")
            logger.info(f"  Content: {doc['content'][:100]}...")  # First 100 characters
            logger.info("---")

    except Exception as e:
        logger.error(f"Error creating and populating document store: {str(e)}")
        logger.exception("Full traceback:")


def main():
    documents_dir = "documents"  # Create this directory and add your documents
    create_and_populate_document_store(documents_dir)
    logger.info("Document store creation, population, and query process completed.")


if __name__ == "__main__":
    main()