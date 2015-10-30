FROM debian:latest
RUN ["apt-get", "-y", "update"]
RUN ["apt-get", "install", "-y", "git-core"]
ADD ["docker-build.sh", "./"]
CMD ["docker-build.sh"]
