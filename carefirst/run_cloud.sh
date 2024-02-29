#!/bin/bash

NAMESPACE=jhsmith

# Set context (DIFFERENT)
echo "Set kubernetes context"
kubectl config use-context w255-aks

echo "Apply Kustomize Files"
kubectl apply -k .k8s/bases
kubectl apply -k .k8s/overlays/prod
kubectl get all -n $NAMESPACE

echo "Wait for API to be accessible"
# # wait for the /health endpoint to return a 200 and then move on
finished=false
while ! $finished; do
    health_status=$(curl -o /dev/null -s -w "%{http_code}\n" -X GET 'https://jhsmith.mids255.com/health')
    if [ $health_status == "200" ]; then
        finished=true
        echo "API is ready"
    else
        echo "API not responding yet"
        sleep 1
    fi
done

echo "curl the defined endpoints and return status codes (same format as lab_1 requirement)"
echo "testing '/hello' endpoint with ?name=Winegar. Expect status code of 200 returned"
curl -o /dev/null -s -w "%{http_code}\n" -X GET 'https://jhsmith.mids255.com/hello?name=Winegar'

echo "testing '/' endpoint. Expect status code of 404 returned"
curl -o /dev/null -s -w "%{http_code}\n" -X GET 'https://jhsmith.mids255.com/'

echo "testing '/docs' endpoint. expect status code of 200 returned"
curl -o /dev/null -s -w "%{http_code}\n" -X GET 'https://jhsmith.mids255.com/docs'

echo "testing '/health' endpoint. expect status code of 200 returned"
curl -o /dev/null -s -w "%{http_code}\n" -X GET 'https://jhsmith.mids255.com/health'

curl -o /dev/null -s -w "%{http_code}\n" -X POST "http://localhost:8000/conversations/9999" -H 'Content-Type: application/json' -d \
'{"question": "cut"}'

echo "Delete deployments and services in namespace"
kubectl delete --all deployments --namespace=${NAMESPACE}
kubectl delete --all services --namespace=${NAMESPACE}