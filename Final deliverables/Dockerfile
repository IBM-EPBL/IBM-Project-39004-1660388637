
FROM python
WORKDIR /ibm222
 LABEL maintainer="KAVINRAJA, 1905023cse@cit.edu.in"
 RUN apt-get update
COPY requirements.txt requirements.txt
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN /usr/local/bin/python -m pip install ibm_db
RUN /usr/local/bin/python -m pip install flask
ENV IBM_DB_HOME /ibm222/db2_license/licenses/clidriver
ENV LD_LIBRARY_PATH /ibm222/db2_license/licenses/clidriver/lib:$LD_LIBRARY_PATH
EXPOSE 5000
COPY . .
ENTRYPOINT [ "python" ]
 CMD [ "app.py"]