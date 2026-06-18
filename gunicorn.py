import gevent.monkey
gevent.monkey.patch_all()
from config import port, workers, keepalive, timeout, max_requests, max_requests_jitter, real_ip_header

loglevel = "warning"
bind = "0.0.0.0:{}".format(port)
pidfile = "./gunicorn.pid"
logfile = "-"
errorlog = "-"
accesslog = "-"
if real_ip_header:
    access_log_format = '%({X-Forwarded-For}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
else:
    access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
capture_output = True

workers = workers
worker_class = "gunicorn.workers.ggevent.GeventWorker"
keepalive = keepalive
timeout = timeout
max_requests = max_requests
max_requests_jitter = max_requests_jitter
