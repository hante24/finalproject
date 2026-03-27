bash ../COMPLETE_SETUP.sh

docker-compose up

docker-compose exec backend alembic upgrade head
docker-compose exec backend python init_db.py
