import unittest
from flask_eureka.eurekaclient import EurekaClient

class EurekaClientMock(unittest.TestCase):
    def setUp(self):
        def mock_get_urls(self):
            pass
        
        EurekaClient.get_eureka_urls = mock_get_urls
        self.mocked_client = EurekaClient



class TestEurekaClient(EurekaClientMock):

    def test_true_https_flag(self):
        e_client = self.mocked_client(
            name='test-eureka-client',
            host_name='mocked_host_name',
            port=8080,
            https_enabled=True
        )
        instance_data = e_client.get_instance_data()
        healthcheckUrl = instance_data['instance']['healthCheckUrl']
        statusPageUrl = instance_data['instance']['statusPageUrl']
        homePageUrl = instance_data['instance']['homePageUrl']

        self.assertEqual(healthcheckUrl, 'https://mocked_host_name:8080/healthcheck')
        self.assertEqual(statusPageUrl, 'https://mocked_host_name:8080/healthcheck')
        self.assertEqual(homePageUrl, 'https://mocked_host_name:8080/healthcheck')


    def test_false_https_flag(self):
        e_client = self.mocked_client(
            name='test-eureka-client',
            host_name='mocked_host_name',
            port=8080,
            https_enabled=False
        )
        instance_data = e_client.get_instance_data()
        healthcheckUrl = instance_data['instance']['healthCheckUrl']
        statusPageUrl = instance_data['instance']['statusPageUrl']
        homePageUrl = instance_data['instance']['homePageUrl']

        self.assertEqual(healthcheckUrl, 'http://mocked_host_name:8080/healthcheck')
        self.assertEqual(statusPageUrl, 'http://mocked_host_name:8080/healthcheck')
        self.assertEqual(homePageUrl, 'http://mocked_host_name:8080/healthcheck')


    def test_default_https_flag(self):
        e_client = self.mocked_client(
            name='test-eureka-client',
            host_name='mocked_host_name',
            port=8080
        )
        instance_data = e_client.get_instance_data()
        healthcheckUrl = instance_data['instance']['healthCheckUrl']
        statusPageUrl = instance_data['instance']['statusPageUrl']
        homePageUrl = instance_data['instance']['homePageUrl']

        self.assertEqual(healthcheckUrl, 'http://mocked_host_name:8080/healthcheck')
        self.assertEqual(statusPageUrl, 'http://mocked_host_name:8080/healthcheck')
        self.assertEqual(homePageUrl, 'http://mocked_host_name:8080/healthcheck')