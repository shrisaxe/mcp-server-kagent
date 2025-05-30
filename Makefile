CEC_ID = ${USER}
CEC_ID = shrisaxe
IMAGE = containers.cisco.com/${CEC_ID}/mcp_server_for_kagent

#include .envrc

fmt:  # lint and format code
	python -m ruff check --select I --fix
	python -m ruff format

test:  # run unit tests
	python -m pytest --cov event_hook

local:  # run api locally
	uvicorn atlas-notification.main:app --reload

push-dev:  # build and push dev image #-build-arg GITHUB_SSH_KEY_PATH=${GITHUB_SSH_KEY_PATH} .
	podman build -t ${IMAGE}:test --platform linux/amd64 .
	
	podman push ${IMAGE}:test
push: push-dev

push-ga:  # build and push ga image 	#--build-arg GITHUB_SSH_KEY_PATH=${GITHUB_SSH_KEY_PATH} .
	podman build -t ${IMAGE}:stable --platform linux/amd64 .

	podman push ${IMAGE}:stable
