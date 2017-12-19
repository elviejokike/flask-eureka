# flask-eureka

Flask Eureka Integration

[![Build Status](https://travis-ci.org/elviejokike/flask-eureka.svg?branch=master)](https://travis-ci.org/elviejokike/flask-eureka)


How to
======

```python
    from flask import Flask
    from flask_eureka import Eureka

    app = Flask(__name__)

    # do 

    eureka = Eureka(app)
    eureka.register_service(name="my-flask-service")

    app.run()
```

In addition to this, the Eureka defaul blueprint *eureka_bp* offered by the library must be added to your application:
```python
    from flask_eureka.eureka import eureka_bp
    app.register_blueprint(eureka_bp)
```

Open your eureka discovery service, and the application will be shown as *my-flask-service*.

Configuration
=============

The flask-eureka library integrate with flask's configuration mechanism. The following environment variables are used:

- SERVICE_NAME = Service name is used as the application ID towards Eureka
- EUREKA_SERVICE_URL= The Eureka service endpoint used for registration
- EUREKA_SERVICE_PATH = The path of eureka service end point. Default to *eureka/apps*
- EUREKA_INSTANCE_HOSTNAME = The hostname used for registration on eureka. 
- EUREKA_INSTANCE_PORT = The port number used for the instance
- EUREKA_HEARTBEAT = Number of seconds used for updating registration status towards Eureka. Default is 90 seconds
