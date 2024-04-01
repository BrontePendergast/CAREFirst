## Capstone: CAREFirst - Companion AI Response and Emergency First-aid

## Create .env file from .env.template

## Start redis local docker image
docker run --name redis -p 6379:6379 -d redis

## ./run.sh 
run.sh is located in the CareFirst directory and implements the yaml files located in the infra/ directory. It builds docker images for both the backend and frontend and deploys them with minikube.

The backend takes some time to start.

docker run -d --name temp-redis -p 6379:6379 redis