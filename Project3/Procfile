api1: ./traefik --configFile=traefik.toml
api2: uvicorn --port=${PORT:-7000} microservice1proj2:app --reload
api3: uvicorn --port=${PORT:-7001} microservice2proj2:app --reload
api4: uvicorn --port=${PORT:-8000} microserviceproj3:app --reload



