# flask-eureka

Flask Eureka Integration

[![Build Status](https://travis-ci.org/elviejokike/flask-eureka.svg?branch=master)](https://travis-ci.org/elviejokike/flask-eureka)


How to
======

.. code-block:: python

    from flask import Flask
    from flask_eureka import Eureka

    app = Flask(__name__)

    # do 

    eureka = Eureka(app)
    eureka.register_service(name="my-flask-service",
          port=5000,
    )

    app.run()

Open your eureka discovery service, and the application will be shown as *my-flask-service*.

Configuration
=============

The flask-eureka library integrate with flask's configuration mechanism. The following environment variables are used:

- SERVICE_NAME = Service name is used as the application ID towards Eureka
- EUREKA_SERVICE_URL= The Eureka service endpoint used for registration
- EUREKA_DATACENTER = Data center name. Use "Amazon" when running the service on EC2 instances
- EUREKA_HOSTNAME = The hostname used for registration on eureka. 
- EUREKA_HEARTBEAT = Number of seconds used for updating registration status towards Eureka. Default is 90 seconds
