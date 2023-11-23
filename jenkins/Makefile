.PHONY: build
build:  ## Build image
	DOCKER_BUILDKIT=1 docker build \
		-f docker/Dockerfile \
		-t python_image \
		.

.PHONY: run
run:  ## Run container
run: build
	docker run -it --rm \
		--name python_container \
		--network host \
		-v $(PWD)/credentials.yaml:/usr/src/sing_off_cli/credentials.yaml \
		python_image \
		python3 src/sign_off_cli.py

.PHONY: run
run:  ## Run container
run: build
	docker run -it --rm \
		--name python_container \
		--network host \
		-v $(PWD)/credentials:/usr/src/sing_off_cli/credentials \
		python_image \
		python3 src/sign_off_cli.py

.PHONY: set_up
set_up:  ## set up env
set_up: build
	docker run -it --rm \
		--name python_container \
		--network host \
		-v $(PWD)/credentials:/usr/src/sing_off_cli/credentials \
		python_image \
		python3 src/set_up.py