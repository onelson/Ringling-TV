"""
This module collects methods for interacting with the fedora repository
"""

from rtv.settings import * 
from fcrepo.utils import NS
from fcrepo.connection import Connection
from fcrepo.client import FedoraClient

pp = lambda x: unicode(RTV_PID_NAMESPACE+':'+x) # prefix pid namespace 

def get_client():
    """Returns an instance of fcrepo..client.FedoraClient with the connection 
    settings specified in settings.py"""
    
    connection = Connection(FEDORA_INSTANCE, 
            username=RTV_FEDORA_USER, 
            password=RTV_FEDORA_PASSWORD)
    return FedoraClient(connection)