bind = "127.0.0.1:9000"                   # Don't use port 80 becaue nginx occupied it already. 
errorlog = '/Users/seonghyeongi/python_projects/py352_chatbot/logs/gunicorn-error.log'  # Make sure you have the log folder create
accesslog = '/Users/seonghyeongi/python_projects/py352_chatbot/logs/gunicorn-access.log'
loglevel = 'debug'
workers = 5     # the number of recommended workers is '2 * number of CPUs + 1' 
