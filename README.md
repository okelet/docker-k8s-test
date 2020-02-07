# docker-k8s-test

## Docker

```
cd docker
docker build -t flasktest .
docker run --rm -it -p 5000:5000 --name flasktest flasktest
```

Access to http://127.0.0.1:5000, or curl-it:

```
curl 127.0.0.1:5000
```

Upload to Docker Hub:

```
docker tag flasktest okelet/flasktest:latest
docker push okelet/flasktest:latest
```
