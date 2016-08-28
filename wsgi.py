from gevent.wsgi import WSGIServer
from serve import app

http_server = WSGIServer(('', 8000), app)
http_server.serve_forever()
