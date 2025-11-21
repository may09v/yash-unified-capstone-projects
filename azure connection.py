from openai import AzureOpenAI
 
AZURE_OPENAI_ENDPOINT = ""
AZURE_OPENAI_KEY = ""  # <-- IMPORTANT: Replace with your key
AZURE_OPENAI_API_VERSION = ""
AZURE_OPENAI_DEPLOYMENT_NAME = ""
embedding_deployment_name = ""
 
openai_client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,
    api_version=AZURE_OPENAI_API_VERSION
) 
response = openai_client.embeddings.create(
        input="how are you",
        model=embedding_deployment_name  # Specify the deployment name
    )

    # Extract embeddings from the response
embeddings = response.data
print(f"Embeddings for the input text:\n{embeddings}")
