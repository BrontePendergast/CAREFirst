#!/bin/bash

IMAGE_PREFIX=$(az account list --all | jq '.[].user.name' | grep -i berkeley.edu | awk -F@ '{print $1}' | tr -d '"' | tr -d "." | tr '[:upper:]' '[:lower:]' | tr '_' '-' | uniq)

echo FQDN = Fully-Qualified Domain Name
IMAGE_NAME=api-lab4
ACR_DOMAIN=w255mids.azurecr.io
IMAGE_FQDN="${ACR_DOMAIN}/${IMAGE_PREFIX}/${IMAGE_NAME}"

echo "IMAGE_FQDN" ${IMAGE_FQDN}

echo "Get latest github hash as TAG"
export TAG=$(git rev-parse --short HEAD)
echo "TAG" ${TAG}

echo "Send TAG to yaml files"
sed "s/\[TAG\]/${TAG}/g" .k8s/overlays/prod/patch-deployment-lab4_copy.yaml > .k8s/overlays/prod/patch-deployment-lab4.yaml

echo "Build image on a Apple Silicon"
docker build --platform linux/amd64 -t ${IMAGE_NAME}:${TAG} .

echo "Push image to azure repository"
docker tag ${IMAGE_NAME}:${TAG} ${IMAGE_FQDN}:${TAG}

# Azure Credentials
az acr login --name jhsmith

# Push image to Azure
docker push ${IMAGE_FQDN}:${TAG}
docker pull ${IMAGE_FQDN}:${TAG}

