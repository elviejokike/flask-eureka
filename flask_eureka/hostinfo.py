from __future__ import division
from __future__ import print_function

import platform  # gets host info
import subprocess
from platform import python_version

if python_version().split('.')[0] == '2':
    def getoutput(cmd):
        return subprocess.check_output([cmd], shell=True)
else:
    def getoutput(cmd):
        return subprocess.getoutput(cmd)


class HostInfo(object):
    """
    This collects info on a host computer and generates a dictionary
    of it.
    """
    TB = 2 ** 40
    GB = 2 ** 30
    MB = 2 ** 20
    KB = 2 ** 10

    def __init__(self, iface='en0'):
        self.iface = iface
        self.system = platform.system()
        self.macaddr = None

    def get(self):
        return {
            'host': platform.node(),
            'IPv4': self.ipv4(),
            'IPv6': self.ipv6(),
            'MAC': self.mac()
        }

    def mac(self):
        if self.macaddr is None:
            if self.system == 'Darwin':
                self.macaddr = getoutput("ifconfig " + self.iface + "| grep ether | awk '{ print $2 }'")
            else:
                self.macaddr = getoutput("ifconfig " + self.iface + "| grep HWaddr | awk '{ print $5 }'")

        return self.macaddr

    def ipv4(self):
        if self.system == 'Darwin':
            ipv4 = getoutput("ifconfig " + self.iface + " | grep 'inet ' | awk '{ print $2 }'")
        else:
            ipv4 = getoutput("ifconfig " + self.iface + " | grep 'inet addr' | awk '{ print $2 }'")
            if ipv4.__contains__(":"):
                ipv4 = ipv4.split(':')[1]

        # ipv4 = socket.gethostbyname(platform.node())
        # if ipv4.split('.')[0] == '127':
        # 	ipv4 = socket.gethostbyname(platform.node() + '.local')
        return ipv4

    def ipv6(self):
        if self.system == 'Darwin':
            ipv6 = getoutput("ifconfig " + self.iface + "| grep inet6 | awk '{ print $2 }'")
        else:
            ipv6 = getoutput("ifconfig " + self.iface + "| grep inet6 | awk '{ print $3 }'")
        # result = socket.getaddrinfo(host, port, socket.AF_INET6)
        # return result[0][4][0]
        return ipv6
