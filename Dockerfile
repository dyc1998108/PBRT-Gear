
FROM veckiina/pbrt-v3-spectral:LatestTest

RUN apt-get update \
 && apt-get -y install python3-pip\
 && pip3 install --upgrade pip\
 && pip3 install flywheel-sdk
ENTRYPOINT ["python run.py"] 

