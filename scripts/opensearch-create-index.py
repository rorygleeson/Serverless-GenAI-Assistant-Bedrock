import argparse
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
import os
from requests_aws4auth import AWS4Auth
import time
import re

# Retrieve arguments from command line
parser = argparse.ArgumentParser(description="Help", 
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--opensearch-endpoint", help="opensearch endpoint url (Example: https://abc123.us-east-1.aoss.amazonaws.com", required=True)
parser.add_argument("--vector-index", help="vector index", required=True)

args = parser.parse_args()
print(args)
service = 'aoss'
credentials = boto3.Session().get_credentials()
region = os.environ.get('AWS_REGION')
print(region)
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
print(awsauth)
#Remove http or https prefixes with regex
opensearch_vector_endpoint = re.sub(r'^https?://', '', args.opensearch_endpoint)
opensearch_vector_port = 443
opensearch_vector_field="vector_field"
opensearch_vector_index = args.vector_index
print("opensearch vector endpoint and index")
print(opensearch_vector_endpoint)
print(opensearch_vector_index)

opensearch_client = OpenSearch(
   hosts = [{'host': opensearch_vector_endpoint, 'port': opensearch_vector_port}],
   http_auth = awsauth,
   use_ssl = True,
   verify_certs = True,
   http_compress = True,
   connection_class = RequestsHttpConnection
)
print(opensearch_client)

index_body = {
    'settings': {
        'index': {
            'knn': True,
            'knn.algo_param.ef_search': 100,  # Optional: tune for search performance
            'number_of_shards': 1,
            'number_of_replicas': 0
        }
    },
    'mappings': {
        'properties': {
            'vector_field': {  # Name of your vector field
                'type': 'knn_vector',
                'dimension': 1024,
                'method': {
                    'name': 'hnsw',
                    'space_type': 'cosinesimil',
                    'engine': 'faiss',
                    'parameters': {
                        'ef_construction': 128,
                        'm': 24
                    }
                }
            },
            'text_field': {
                'type': 'text'
            }
        }
    }
}





print(index_body)


# Create index if it doesn't exist


try:
    if not opensearch_client.indices.exists(index=opensearch_vector_index):
        response = opensearch_client.indices.create(index=opensearch_vector_index, body=index_body)
        print(f"Index '{opensearch_vector_index}' created: {response}")
    else:
        print(f"Index '{opensearch_vector_index}' already exists.")
except Exception as e:
    print(f"Error creating index: {e}")