
FROM veckiina/pbrt-v3-spectral:LatestTest

RUN apt-get update \
 && apt-get -y install python3 \
 && apt-get -y install python3-pip\
 && pip3 install --upgrade pip\
 && pip3 install flywheel-sdk\
 && rm -rf /var/cache/apk/*    

ENV FLYWHEEL=/flywheel/v0       

RUN mkdir -p ${FLYWHEEL}        
COPY run.py ${FLYWHEEL}/run.py  
ENTRYPOINT ["python3 run.py"] 

