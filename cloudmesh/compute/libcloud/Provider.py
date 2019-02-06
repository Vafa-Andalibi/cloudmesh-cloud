from cloudmesh.abstractclass.ComputeNodeABC import ComputeNodeABC
from pprint import pprint
from datetime import datetime
from cloudmesh.common.util import HEADING
from cloudmesh.common.parameter import Parameter
from cloudmesh.management.configuration.config import Config

from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider as LibcloudProvider


class Provider(ComputeNodeABC):

    ProviderMapper = {
        "openstack": LibcloudProvider.OPENSTACK,
        "aws": LibcloudProvider.EC2
    }

    def __init__(self, name=None, configuration="~/.cloudmesh/cloudmesh4.yaml"):
        HEADING(c=".")
        conf = Config(configuration)["cloudmesh"]
        mycloud = conf["cloud"][name]
        cred = mycloud["credentials"]
        cloudkind = mycloud["cm"]["kind"]
        self.kind = cloudkind
        #pprint (cred)
        #print (cloudkind)
        super().__init__(name, conf)
        if cloudkind in Provider.ProviderMapper:
            if cloudkind == 'openstack':
                self.driver = get_driver(Provider.ProviderMapper[cloudkind])
                self.cloudman = self.driver(cred["OS_USERNAME"],
                                    cred["OS_PASSWORD"],
                                    ex_force_auth_url=cred['OS_AUTH_URL'],
                                    ex_force_auth_version='2.0_password',
                                    ex_tenant_name=cred['OS_TENANT_NAME'])
        else:
            print ("Specified provider not available")
            self.cloudman = None
        self.default_image = None
        self.default_size = None
        self.public_key_path = conf["profile"]["key"]["public"]

    def dict(self, elements, kind=None):
        if elements is None:
            return None
        elif type(elements) == list:
            _elements = elements
        else:
            _elements = [elements]
        d = []
        for element in _elements:
            entry = element.__dict__
            entry["kind"] = kind
            entry["driver"] = self.kind

            if kind == 'node':
                entry["updated"] = str(datetime.utcnow())

                if "created_at" in entry:
                    entry["created"] = str(entry["created_at"])
                    del entry["created_at"]
                else:
                    entry["created"] = entry["modified"]
            elif kind == 'flavor':
                entry["created"] = entry["updated"] = str(datetime.utcnow())
            elif kind == 'image':
                entry['created'] = entry['extra']['created']
                entry['updated'] = entry['extra']['updated']

            del entry["_uuid"]

            d.append(entry)
        return d

    def find(self, elements, name=None):
        for element in elements:
            if element["name"] == name:
                return element
        return None

    def images(self, raw=False):
        if self.cloudman:
            entries = self.cloudman.list_images()
            if raw:
                return entries
            else:
                return self.dict(entries, kind="image")

        return None

    def image(self, name=None):
        """
        Gets the image with a given nmae
        :param name: The name of the image
        :return:
        """
        return self.find(self.images(), name=name)

    def flavors(self, raw=False):
        if self.cloudman:
            entries = self.cloudman.list_sizes()
            if raw:
                return entries
            else:
                return self.dict(entries, kind="flavor")
        return None


    def flavor(self, name=None):
        """
        Gest the flavor with a given name

        :param name: The aname of the flavor
        :return:
        """
        return self.find(self.flavors(), name=name)

    def start(self, name):
        """
        start a node
    
        :param name: the unique node name
        :return:  The dict representing the node
        """
        HEADING(c=".")
        return None

    def stop(self, name=None):
        """
        stops the node with the given name
    
        :param name:
        :return: The dict representing the node including updated status
        """
        HEADING(c=".")
        return None

    def info(self, name=None):
        """
        gets the information of a node with a given name
    
        :param name:
        :return: The dict representing the node including updated status
        """
        return self.find(self.list(), name=name)

    def suspend(self, name=None):
        """
        suspends the node with the given name
    
        :param name: the name of the node
        :return: The dict representing the node
        """
        HEADING(c=".")
        return None

    def list(self, raw=False):
        """
        list all nodes id
    
        :return: an array of dicts representing the nodes
        """
        if self.cloudman:
            entries = self.cloudman.list_nodes()
            if raw:
                return entries
            else:
                return self.dict(entries, kind="node")
        return None

    def resume(self, name=None):
        """
        resume the named node
    
        :param name: the name of the node
        :return: the dict of the node
        """
        HEADING(c=".")
        return None

    def destroy(self, names=None):
        """
        Destroys the node
        :param name: the name of the node
        :return: the dict of the node
        """
        HEADING(c=".")

        names = Parameter.expand(names)

        nodes = self.list(raw=True)
        for node in nodes:
            if node.name in names:
                self.cloudman.destroy_node(node)
        return None

    def reboot(self, name=None):
        """
        Reboot the node
        :param name: the name of the node
        :return: the dict of the node
        """
        HEADING(c=".")
        return None

    def create(self, name=None, image=None, size=None, timeout=360, **kwargs):
        """
        creates a named node
    
        :param name: the name of the node
        :param image: the image used
        :param size: the size of the image
        :param timeout: a timeout in seconds that is invoked in case the image does not boot.
               The default is set to 3 minutes.
        :param kwargs: additional arguments HEADING(c=".")ed along at time of boot
        :return:
        """
        """
        create one node
        """
        HEADING(c=".")
        #imagename = "CC-Ubuntu16.04"
        #flavorname = "m1.medium"
        images = self.images(raw=True)
        imageUse = None
        flavors = self.flavors(raw=True)
        flavorUse = None
        for _image in images:
            if _image.name == image:
                imageUse = _image
                break
        for _flavor in flavors:
            if _flavor.name == size:
                flavorUse = _flavor
                break
        node = self.cloudman.create_node(name=name, image=imageUse, size=flavorUse)
        pprint (node)
        return (self.dict(node))
        # no brackets needed?

    def rename(self, name=None, destination=None):
        """
        rename a node
    
        :param destination:
        :param name: the current name
        :return: the dict with the new name
        """
        # if destination is None, increase the name counter and use the new name
        HEADING(c=".")
        return None
