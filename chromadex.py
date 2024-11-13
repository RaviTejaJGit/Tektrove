import os
import chromadb
import torchvision

torchvision.disable_beta_transforms_warning()

from dotenv import load_dotenv
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader,StorageContext,load_index_from_storage, Settings


# Load the environment variables
load_dotenv()

# Load the environment variables
api_base = os.getenv("API_BASE")
api_key = os.getenv("API_KEY")
deployment_name = os.getenv("DEPLOYMENT_NAME")
api_version = os.getenv("API_VERSION")

# Initialize the Azure OpenAI model
llm = AzureOpenAI(
    engine="gpt-4o-test",
    deployment_name=deployment_name,
    api_key=api_key,
    azure_endpoint=api_base,
    api_version=api_version,
)

# Initialize the Hugging Face embedding model
embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
    #device="cuda"
    )

# Initialize the Chroma client
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Load the collection or create a new one if it doesn't exist
try:
    chroma_collection = chroma_client.get_collection("quickstart")
    print("Collection 'quickstart' found and loaded.")
except chromadb.errors.InvalidCollectionException:
    chroma_collection = chroma_client.create_collection("quickstart")
    print("Collection 'quickstart' not found, so a new one was created.")

# Define embedding function and documents
Settings.llm = llm
Settings.embed_model = embed_model

# Set up ChromaVectorStore and load in data
vector_store = ChromaVectorStore(chroma_collection=chroma_collection) # Initialize the ChromaVectorStore
storage_context = StorageContext.from_defaults(vector_store=vector_store) # Initialize the storage context
index = VectorStoreIndex([]) # Initialize the index

corpus_file_path = "corpus.txt"

index.storage_context.persist(persist_dir="chroma_db") # Persist the index to disk
storage_context = StorageContext.from_defaults(persist_dir="chroma_db",vector_store=vector_store) # Load the storage Context
index = load_index_from_storage(storage_context) # Load the index from storage
print("Loaded the index from storage.")
        

def update_index_and_query_engine():
    #print("Updating index and query engine")
    documents = SimpleDirectoryReader("srts").load_data()

    with open(corpus_file_path, "r") as corpus_file:
        existing_file_names = set(line.strip() for line in corpus_file)

    # Insert new documents if their names are not in corpus.txt
    for doc in documents:
        if doc.metadata['file_name'] not in existing_file_names and not doc.metadata['file_name'].endswith('.pdf'):
            index.insert(doc)
                    
            with open(corpus_file_path, "a") as corpus_file:
                corpus_file.write(f"{doc.metadata['file_name']}\n")
            print(f"Inserted {doc.metadata['file_name']} into index and updated corpus.txt.")
            
    index.storage_context.persist(persist_dir="chroma_db") # Persist the index to disk

    # Create a query engine from the index
    return index.as_query_engine()

# Call the function to update the index and create the query engine
query_engine = update_index_and_query_engine()

# Define the prompt to be used for generating responses
prompt = """
You are a highly advanced language model, optimized to generate precise, thorough, and context-aware explanations.
Based on the retrieved context below, provide an answer with the highest degree of clarity and detail possible.
Ensure the response is exhaustive, addressing every facet of the topic comprehensively.
Your explanation should:
Be well-organized and broken down into clear sections or steps.
Highlight key points and distinctions that might be important for understanding.
Use concise, crystal-clear language that eliminates ambiguity.
Ensure the final answer leaves no room for misinterpretation or misunderstanding.
"""

# Define a function to process user queries
def update_index_in_background():
    global query_engine
    query_engine = update_index_and_query_engine()
    print("Loading in Background")

def process_query(user_query):
    file_name = set()

    global query_engine
    documents = SimpleDirectoryReader("srts").load_data()
    with open(corpus_file_path, "r") as corpus_file:
        existing_file_names = set(line.strip() for line in corpus_file)

    # Flag to check if any new documents are found
    new_doc_found = False

    for doc in documents:   
        if doc.metadata['file_name'] not in existing_file_names and not doc.metadata['file_name'].endswith('.pdf'):
            print("New document found",doc.metadata['file_name'])
            new_doc_found = True
            query_engine = update_index_and_query_engine()
            # Start a new thread for updating the index in the background
            #update_thread = threading.Thread(target=update_index_in_background)
            #update_thread.start()
            #break  # Exit after starting the update process

    # Proceed with the user query using the current index
    answer = query_engine.query(user_query + " " + prompt)
    metadata_dict = answer.metadata

    for key in metadata_dict:
        originalfilename = metadata_dict[key]["file_name"]
        mp4_filename = originalfilename.replace("srt", "mp4")
        file_name.add(mp4_filename)

    # Optionally, wait for the update to complete if desired
    # update_thread.join()

    return answer, list(file_name)
