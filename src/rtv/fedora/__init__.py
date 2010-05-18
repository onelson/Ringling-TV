"""
This module collects methods for interacting with the fedora repository
"""

from rtv import settings
from fcrepo.utils import NS
from fcrepo.connection import Connection
from fcrepo.client import FedoraClient

u = unicode # shortcut
pp = lambda x: u(settings.RTV_PID_NAMESPACE+':'+x) # prefix pid namespace 

def get_client():
    """Returns an instance of fcrepo..client.FedoraClient with the connection 
    settings specified in settings.py"""
    
    connection = Connection(settings.FEDORA_INSTANCE, 
            username=settings.RTV_FEDORA_USER, 
            password=settings.RTV_FEDORA_PASSWORD)
    return FedoraClient(connection)