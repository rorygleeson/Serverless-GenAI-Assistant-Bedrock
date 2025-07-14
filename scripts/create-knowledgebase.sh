echo "Retrieve Bucket Name"
bucket_name="$1"

echo "Retrieve Opensearch Collection ARN and Bedrock Service Role ARN"
opensearch_collection_stack_name="opensearch-stack"
opensearch_collection_arn=$(aws cloudformation describe-stacks --stack-name "$opensearch_collection_stack_name" --query 'Stacks[0].Outputs[?OutputKey==`OpenSearchCollectionArn`].OutputValue' --output text)
role_arn=$(aws cloudformation describe-stacks --stack-name "$opensearch_collection_stack_name" --query 'Stacks[0].Outputs[?OutputKey==`OpensearchBedrockKnowledgeBaseExecutionRoleArn`].OutputValue' --output text)

echo "Create knowledgebase"
response=$(aws cloudformation create-stack \
--stack-name webapp-bedrock-knowledgebase-stack \
--capabilities CAPABILITY_IAM \
--template-body file://webapp-bedrock-knowledgebase-stack.yml \
--parameters \
ParameterKey=CollectionArn,ParameterValue=$opensearch_collection_arn \
ParameterKey=KnowledgeBaseRoleArn,ParameterValue=$role_arn \
ParameterKey=S3BucketName,ParameterValue=$bucket_name)
aws cloudformation wait stack-create-complete --stack-name webapp-bedrock-knowledgebase-stack