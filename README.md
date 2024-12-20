# FCD
Project for FCD ( Fundamentos de Ciência de Dados) from University of Aveiro 2024/25.

# Run 

To run website and neo4j:
```
$ docker compose up -d
```

To build dataset and insert into neo4j: (you dont need to specificy all steps for example you can do -s 4 do only insert into neo4j if you have the necessary files)
```
$ python3 run.py -s 1 2 3 4
```

# Run neo4j (with Docker)

1. Install docker desktop from [here](https://www.docker.com/products/docker-desktop/).
2. Make sure the docker daemon is running.
3. Run the following command to create a container with the neo4j image:
( You can change the authentication with the parameter "*--env NEO4J_AUTH=neo4j/your_password" and the volume where data is persisted with "*--volume=path*")
```
docker run --restart always --publish=7474:7474 --publish=7687:7687 --env NEO4J_AUTH=neo4j/example123456789 --volume=$PWD/data:/data neo4j:5.25.1
 ```
4. Check if neo4j is running on [localhost:7474](http://localhost:7474/)
5. Login credentials should be user=neo4j and password=example123456789 ( or whatever you set on --env NEO4J_AUTH)
# Resources
- https://github.com/arquivo/pwa-technologies/wiki/Arquivo.pt-API
- https://neo4j.com/docs/cypher-manual/current/introduction/

# Author
**Diogo Machado Marto**