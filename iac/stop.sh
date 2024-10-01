#!/bin/bash
docker compose -f docker-compose-db.yml -p db down -v

docker compose -f docker-compose-superset.yml -p superset down -v

docker compose -f docker-compose-airflow.yml -p airflow down -v

docker compose -f docker-compose-kafka.yml -p kafka down -v