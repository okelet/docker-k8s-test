# docker-k8s-test

## Docker

```
cd docker
docker build -t flasktest .
docker run --rm -it -p 8000:8000 --name flasktest flasktest
```

Access to http://127.0.0.1:8000, or curl-it:

```
curl 127.0.0.1:8000
```

Upload to Docker Hub:

```
docker tag flasktest okelet/flasktest:latest
docker push okelet/flasktest:latest
```

Run from Docker Hub:

```
docker run --rm -it -p 8000:8000 --name flasktest okelet:flasktest
```

Set an application/route prefix:

```
docker run --rm -it -p 8000:8000 --name flasktest -e APP_PREFIX=/myapp okelet:flasktest
```

So then use:

```
curl 127.0.0.1:8000/myapp
```