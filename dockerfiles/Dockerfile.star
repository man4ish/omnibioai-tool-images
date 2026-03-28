FROM ubuntu:24.04
RUN apt-get update && apt-get install -y libgomp1
COPY STAR /usr/local/bin/STAR
RUN chmod +x /usr/local/bin/STAR
CMD ["STAR", "--version"]
