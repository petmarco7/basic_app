.PHONY: build-images watch-services start-services develop-services clean-images stop-services

# Build Docker images
build-images:
	docker compose build

# Watch services (e.g., for file changes or live development)
watch-services:
	trap 'exit 0' INT; docker compose watch --no-up

start-init:
	docker compose up -d database
	docker compose up init

# Full start sequence with init check
start-services: build-images start-init
	trap 'exit 0' INT; docker compose up backend frontend

# Start for development (watch + start sequence)
develop-services: watch-services start-services

# Clean up Docker images and volumes
clean-images: stop-services
	docker system prune -af --volumes

# Stop services and remove all the imaages, containers and volumes
vacuum: clean-images
	docker volume prune -a -f

# Stop and remove containers
stop-services:
	docker compose down

connect-database:
	docker exec -it database psql -U postgres -d mydatabase
