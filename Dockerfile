FROM python3.8

ENV PYTHONPATH="/var/gitapply"
COPY requirements.txt /root/requments.txt
RUN pip3 install -r /root/requirements.txt

EXPOSE 5000

ENTRYPOINT ["python", "/var/gitapply/bin/gitapply_server.py"]
