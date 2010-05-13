"""
This command is used to bulk add/import the app's required content models to 
the fedora repo.
"""

import sys
from django.core.management.base import CommandError, NoArgsCommand
import rtv.fedora
from rtv.fedora import NS, pp

u = unicode # shortcut

_EPISODE_DS_COMP_MODEL = u(
"""<dsCompositeModel xmlns="info:fedora/fedora-system:def/dsCompositeModel#">
  <comment xmlns="info:fedora/fedora-system:def/comment#">
    This DS-COMPOSITE-MODEL datastream is included as a starting point to
      assist in the creation of a content model. The DS-COMPOSITE-MODEL
      should define the datastreams that are required for any objects
      conforming to this content model.
    For more information about content models, see:
      http://fedora-commons.org/confluence/x/dgBI.
    For examples of completed content model objects, see the demonstration
      objects included with your Fedora distribution, such as:
      demo:CMImage, demo:UVA_STD_IMAGE, demo:DualResImageCollection,
      demo:TEI_TO_PDFDOC, and demo:XML_TO_HTMLDOC.
    For more information about the demonstration objects, see:
      http://fedora-commons.org/confluence/x/AwFI.
  </comment>
  <dsTypeModel ID="THUMBNAIL">
    <form MIME="image/jpeg"></form>
  </dsTypeModel>
  <dsTypeModel ID="RAW">
    <form MIME="application/octet-stream"></form>
  </dsTypeModel>
  <dsTypeModel ID="FLV">
    <form MIME="video/x-flv"></form>
  </dsTypeModel>
  <dsTypeModel ID="OGV">
    <form MIME="video/ogg"></form>
  </dsTypeModel>
</dsCompositeModel>""")

class Command(NoArgsCommand):
    help = 'add required content models to fedora repo'
    def handle_noargs(self, *args, **kwargs):
        client = rtv.fedora.get_client()

        obj = client.createObject(pp('EPISODE'), 
            label=u('Content Model for video objects'))
        
        obj.addDataStream(u('RELS-EXT'))
        rels = obj['RELS-EXT']
        rels[NS.rdfs.hasModel].append(dict(
            type = u('uri'),
            value = u('info:fedora/fedora-system:ContentModel-3.0')
            ))
        rels.checksumType = u('DISABLED')
        rels.setContent()
        
        obj.addDataStream(u('DS-COMPOSITE-MODEL'),_EPISODE_DS_COMP_MODEL, 
            label=u('datastream composite model'),
            formatURI=u('info:fedora/fedora-system:FedoraDSCompositeModel-1.0'), 
            logMessage=u('adding ds comp model'))
        comp = obj['DS-COMPOSITE-MODEL']
        comp.checksumType = u('DISABLED')
        # Done
        sys.exit(0)
