from rtv import settings
from fcrepo.utils import NS
from fcrepo.connection import Connection
from fcrepo.client import FedoraClient

u = unicode # shortcut
pp = lambda x: u(settings.RTV_PID_NAMESPACE+':'+x) # prefix pid namespace 

def get_client():
    connection = Connection(settings.FEDORA_INSTANCE, 
            username=settings.RTV_FEDORA_USER, 
            password=settings.RTV_FEDORA_PASSWORD)
    return FedoraClient(connection)