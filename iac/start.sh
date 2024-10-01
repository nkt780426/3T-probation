#!/bin/bash
docker network ls | grep -w "bigdata" || docker network create --driver bridge bigdata

docker compose -f docker-compose-db.yml -p db up -d

docker compose -f docker-compose-superset.yml -p superset up -d

docker compose -f docker-compose-airflow.yml -p airflow up airflow-init -d

docker compose -f docker-compose-airflow.yml -p airflow up -d

docker compose -f docker-compose-kafka.yml -p kafka up -d

docker compose -f docker-compose-superset.yml -p superset down superset-init

docker compose -f docker-compose-airflow.yml -p airflow down airflow-init

# docker compose -f docker-compose-initdb.yml -p demo up init-db -d

# docker compose -f docker-compose-initdb.yml -p demo up streamdata -d
