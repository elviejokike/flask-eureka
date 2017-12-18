from flask import Blueprint

from .eurekaclient import EurekaClient

eureka_bp = Blueprint('eureka', __name__)

@eureka_bp.route('/healthcheck')
def healthcheck():
    """
    This function is used to say current status to the Consul.
    Format: https://www.consul.io/docs/agent/checks.html

    :return: Empty response with status 200, 429 or 500
    """
    return '', 200



class Eureka(object):
    def __init__(self, app=None, **kwargs):
        """
        Initialize the flask extension
        """

        self.kwargs = kwargs if kwargs else {}
        self.app = None


        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        if 'eureka' in app.extensions:
            raise RuntimeError('Flask application already initialized')
        app.extensions['eureka'] = self

    def register_service(self, name=None, **kwargs):

        name = self.app.config.get('SERVICE_NAME', name)
        eureka_url = self.app.config.get('EUREKA_SERVICE_URL', None)
        data_center = self.app.config.get('EUREKA_DATACENTER', None)
        host_name = self.app.config.get('EUREKA_HOSTNAME', 'localhost')
        heartbeat_interval = self.app.config.get('EUREKA_HEARTBEAT', None)

        ec = EurekaClient(name=name, host_name=host_name,
            eureka_url=eureka_url, 
            data_center= data_center,
            heartbeat_interval=heartbeat_interval, 
            **kwargs)
        ec.star()

        pass

