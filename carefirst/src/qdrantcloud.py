import os
load_dotenv(env_file_path())
QDRANT_API_KEY = os.environ["QDRANT_API_KEY"]


def createVectorDB(collection_name, embeddings_model, docs):

  # Store Persistent Vector Database in Qdrant Cloud
  url = 'https://341387f8-7994-46b4-bec4-84da0bb01b72.us-east4-0.gcp.cloud.qdrant.io'
  api_key=QDRANT_API_KEY
  vectordb = Qdrant.from_documents(
      docs,
      embeddings_model,
      url=url,
      prefer_grpc=True,
      api_key=api_key,
      collection_name=collection_name,
  )

  return vectordb

def loadVectorDB(collection_name, embeddings_model):
  # Load Persistent Vector Database

  qdrant_client = QdrantClient(
      host='341387f8-7994-46b4-bec4-84da0bb01b72.us-east4-0.gcp.cloud.qdrant.io',
      api_key=QDRANT_API_KEY,
  )

  vectordb = Qdrant(client=qdrant_client,
                    collection_name=collection_name ,
                    embeddings=embeddings_model)

  return vectordb