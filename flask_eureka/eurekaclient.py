"""
    Eureka Client
"""

import json
import logging
import os
import random
import time
from threading import Thread

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

import dns.resolver

from .ec2metadata import get_metadata
from .httpclient import HttpClientObject, ApiException
from .hostinfo import HostInfo

logger = logging.getLogger('service.eureka')
logger.setLevel(logging.INFO)


class EurekaClientException(Exception):
    pass


class EurekaRegistrationFailedException(EurekaClientException):
    pass


class EurekaUpdateFailedException(EurekaClientException):
    pass


class EurekaHeartbeatFailedException(EurekaClientException):
    pass

class EurekaGetFailedException(EurekaClientException):
    pass

class EurekaClient(object):
    """
        Eureka Client
    """
    EUREKA_SERVICE_URL = 'EUREKA_SERVICE_URL'
    EUREKA_INSTANCE_DATACENTER = 'EUREKA_INSTANCE_DATACENTER'
    EUREKA_HEARTBEAT_INTERVAL = 'EUREKA_HEARTBEAT_INTERVAL'
    EUREKA_SERVICE_PATH = 'EUREKA_SERVICE_PATH'
    EUREKA_INSTANCE_HOSTNAME = 'EUREKA_INSTANCE_HOSTNAME'
    EUREKA_INSTANCE_PORT = 'EUREKA_INSTANCE_PORT'
    def __init__(self, name, eureka_url=None, eureka_domain_name=None, host_name=None, data_center=None,instance_id=None,
                 vip_address=None, secure_vip_address=None, port=None, secure_port=None, use_dns=True, region=None,
                 prefer_same_zone=True, context="eureka/v2", eureka_port=None, heartbeat_interval=None,service_path=None):

        self.app_name = name

        self.eureka_url = eureka_url or os.environ.get(EurekaClient.EUREKA_SERVICE_URL, None)
        self.data_center = data_center or os.environ.get(EurekaClient.EUREKA_INSTANCE_DATACENTER, None)
        self.heartbeat_interval = heartbeat_interval or int(os.environ.get(EurekaClient.EUREKA_HEARTBEAT_INTERVAL, 30))
        self.service_path = service_path or os.environ.get(EurekaClient.EUREKA_SERVICE_PATH, 'eureka/apps')
        self.host_name = host_name or os.environ.get(EurekaClient.EUREKA_INSTANCE_HOSTNAME, None)
        self.port = port or os.environ.get(EurekaClient.EUREKA_INSTANCE_PORT, None)
        self.secure_port = port
        self.use_dns = use_dns
        self.region = region
        self.prefer_same_zone = prefer_same_zone
        self.eureka_domain_name = eureka_domain_name
        self.eureka_port = eureka_port
        self.heartbeat_task = None
        self.instance_id = instance_id

        host_info = HostInfo().get()

        if data_center == "Amazon":
            self.host_name = get_metadata("hostname")
        elif not host_name:
            self.host_name = host_info['host']

        self.vip_address = vip_address
        if not self.vip_address:
            self.vip_address = host_info['IPv4']

        self.secure_vip_address = secure_vip_address
        if not self.secure_vip_address:
            self.secure_vip_address = host_info['IPv4']

        # Relative URL to eureka
        self.context = context
        self.eureka_urls = self.get_eureka_urls()
        self.requests = HttpClientObject()



    def _get_txt_records_from_dns(self, domain):
        records = dns.resolver.query(domain, 'TXT')
        for record in records:
            for string in record.strings:
                yield string

    def _get_zone_urls_from_dns(self, domain):
        for zone in self._get_txt_records_from_dns(domain):
            yield zone

    def get_zones_from_dns(self):
        return {
            zone_url.split(".")[0]: list(self._get_zone_urls_from_dns("txt.%s" % zone_url)) for zone_url in list(
                self._get_zone_urls_from_dns('txt.%s.%s' % (self.region, self.eureka_domain_name))
            )
        }

    def get_eureka_urls(self):
        """
            Get Eureka URLs
        """
        if self.eureka_url:
            return [self.eureka_url]
        elif self.use_dns:
            zone_dns_map = self.get_zones_from_dns()
            zones = zone_dns_map.keys()
            assert len(zones) > 0, "No availability zones found for, please add them explicitly"
            if self.prefer_same_zone:
                if self.get_instance_zone() in zones:
                    zones = [zones.pop(zones.index(self.get_instance_zone()))] + zones  # Add our zone as the first element
                else:
                    logger.warn("No match for the zone %s in the list of available zones %s" % (
                        self.get_instance_zone(), zones)
                    )
            service_urls = []
            for zone in zones:
                eureka_instances = zone_dns_map[zone]
                random.shuffle(eureka_instances)  # Shuffle order for load balancing
                for eureka_instance in eureka_instances:
                    server_uri = "http://%s" % eureka_instance
                    if self.eureka_port:
                        server_uri += ":%s" % self.eureka_port
                    eureka_instance_url = urljoin(server_uri, self.context, "/")
                    if not eureka_instance_url.endswith("/"):
                        eureka_instance_url = "%s/" % eureka_instance_url
                    service_urls.append(eureka_instance_url)
            primary_server = service_urls.pop(0)
            random.shuffle(service_urls)
            service_urls.insert(0, primary_server)
            logger.info("This client will talk to the following serviceUrls in order: %s" % service_urls)
            return service_urls

    def get_instance_zone(self):
        """
            Get Instance Zone
        """
        if self.data_center == "Amazon":
            return get_metadata('availability-zone')
        else:
            raise NotImplementedError("%s does not implement DNS lookups" % self.data_center)

    def get_instance_id(self):
        """
            Get Instance ID
        """
        if self.instance_id:
            return self.instance_id
        return self.host_name + ':' + self.app_name + ':' + str(self.port)

    def get_instance_data(self):
        """
            Get Instance Data
        """
        data_center_info = {
            'name': self.data_center
        }
        if self.data_center == "Amazon":
            data_center_info['metadata'] = {
                'ami-launch-index': get_metadata('ami-launch-index'),
                'local-hostname': get_metadata('local-hostname'),
                'availability-zone': get_metadata('availability-zone'),
                'instance-id': get_metadata('instance-id'),
                'public-ipv4': get_metadata('local-ipv4'),
                'public-hostname': get_metadata('hostname'),
                'ami-manifest-path': get_metadata('ami-manifest-path'),
                'local-ipv4': get_metadata('local-ipv4'),
                'ami-id': get_metadata('ami-id'),
                'instance-type': get_metadata('instance-type'),
            }
        return {
            'instance': {
                'app': self.app_name,
                'instanceId': self.get_instance_id(),
                'hostName': self.host_name,
                'ipAddr': self.vip_address,
                'healthCheckUrl': 'http://' + self.host_name  +':5000/healthcheck',
                'statusPageUrl': 'http://' + self.host_name + ':5000/healthcheck',
                'homePageUrl': 'http://' + self.host_name + ':5000/healthcheck',
                'port': {
                    '$': self.port,
                    '@enabled': 'true',
                },
                'vipAddress': self.vip_address,
                'dataCenterInfo': {
                    '@class': 'com.netflix.appinfo.InstanceInfo$DefaultDataCenterInfo',
                    'name': 'MyOwn',
                },
            },
        }

    def star(self):
        """
        Start registration process
        :return:
        """
        logger.info('Starting eureka registration')
        self.register()
        self.heartbeat_task = Thread(target=self._hearthbeat)
        self.heartbeat_task.daemon = True
        self.heartbeat_task.start()

    def _hearthbeat(self):
        while True:
            time.sleep(self.heartbeat_interval)
            self.renew()
            

    def register(self, initial_status="UP"):
        """
        Registers instance with Eureka, begins heartbeats, and fetches registry.
        :param initial_status: status string
        :return:
        """
        instance_data = self.get_instance_data()
        instance_data['instance']['status'] = initial_status

        success = False
        for eureka_url in self.eureka_urls:
            try:
                register_response = self.requests.POST(url=urljoin(eureka_url, self.service_path + "/%s" % self.app_name), body=instance_data,
                                  headers={'Content-Type': 'application/json'})
                success = True
            except ApiException as ex:
                success = False
        if not success:
            raise EurekaRegistrationFailedException("Did not receive correct reply from any instances")

    def renew(self):
        """
            Send application instance heartbeat
        """
        logger.info(' Updating registeration status ')
        success = False
        for eureka_url in self.eureka_urls:
            try:
                register_response = self.requests.PUT(url=urljoin(eureka_url, self.service_path + '/%s/%s' % (
                    self.app_name,
                    self.get_instance_id()
                )))
                success = True
            except ApiException as ex:
                if ex.status == 404:
                    self.register()
                    return
                else:
                    success = False
        if not success:
            raise EurekaUpdateFailedException("Did not receive correct reply from any instances")

    #a generic get request, since most of the get requests for discovery will take a similar form
    def _get_from_any_instance(self, endpoint):
        for eureka_url in self.eureka_urls:
            try:
                r = self.requests.GET(urljoin(eureka_url, endpoint), headers={'accept': 'application/json'})
                r.raise_for_status()
                return json.loads(r.content)
            except:
                pass
        raise EurekaGetFailedException("Failed to GET %s from all instances" % endpoint)

    def get_apps(self):
        return self._get_from_any_instance("apps")

    def get_app(self, app_id):
        return self._get_from_any_instance("apps/%s" % app_id)

    def get_vip(self, vip_address):
        return self._get_from_any_instance("vips/%s" % vip_address)

    def get_svip(self, vip_address):
        return self._get_from_any_instance("svips/%s" % vip_address)

    def get_instance(self, instance_id):
        return self._get_from_any_instance("instances/%s" % instance_id)

    def get_app_instance(self, app_id, instance_id):
        return self._get_from_any_instance("apps/%s/%s" % (app_id, instance_id))

