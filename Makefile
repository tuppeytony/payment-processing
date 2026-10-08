run:
	docker volume create postgres-data;\
	docker compose -p payment-processing -f ./ci/docker-compose.yaml up -d

rebuild:
	docker compose -p payment-processing -f ./ci/docker-compose.yaml down
	docker compose -p payment-processing -f ./ci/docker-compose.yaml up --build --force-recreate -d
