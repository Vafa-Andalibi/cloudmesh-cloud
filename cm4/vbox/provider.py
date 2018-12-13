from cm4.abstractclass.CloudManagerABC import CloudManagerABC
from cloudmesh.common.Shell import Shell
import webbrowser
from cloudmesh.common.dotdict import dotdict
import os
import textwrap
from cm4.configuration.config import Config
from pprint import pprint
from cloudmesh.common.console import Console


class VboxProvider(CloudManagerABC):

    #
    # if name is none, take last name from mongo, apply to last started vm
    #

    def __init__(self):
        pass

    def start(self, name):
        """
        start a node

        :param name: the unique node name
        :return:  The dict representing the node
        """
        pass

        #    def nodes(self, verbose=False):

    def nodes(self, verbose=False):
        """
        list all nodes id

        :return: an array of dicts representing the nodes
        """

        def convert(line):
            entry = (' '.join(line.split())).split(' ')
            data = dotdict()
            data.id = entry[0]
            data.name = entry[1]
            data.provider = entry[2]
            data.state = entry[3]
            data.directory = entry[4]
            return data

        result = Shell.execute("vagrant", "global-status --prune")
        if verbose:
            print(result)
        if "There are no active" in result:
            return None

        lines = []
        for line in result.split("\n")[2:]:
            if line == " ":
                break
            else:
                lines.append(convert(line))
        return lines

    def boot(self, **kwargs):

        arg = dotdict(kwargs)
        arg.cwd = kwargs.get("cwd", None)

        # get the dir based on anme




        print("ARG")
        pprint(arg)
        vms = self.to_dict(self.nodes())

        print("VMS", vms)

        arg = self._get_specification(**kwargs)


        pprint(arg)

        if arg.name in vms:
            Console.error("vm {name} already booted".format(**arg), traceflag=False)
            return None

        else:
            self.create(**kwargs)
            Console.ok("{name} created".format(**arg))
            Console.ok("{directory}/{name} booting ...".format(**arg))

            result = Shell.execute("vagrant",
                                   ["up", arg.name],
                                   cwd=arg.directory)
            Console.ok("{name} ok.".format(**arg))

            return result

    def execute(self, name, command, cwd=None):

        arg = dotdict()
        arg.cwd = cwd
        arg.command = command
        arg.name = name
        config = Config()
        cloud = "vagrant"  # TODO: must come through parameter or set cloud
        arg.path = config.data["cloudmesh"]["cloud"]["vagrant"]["default"]["path"]
        arg.directory = os.path.expanduser("{path}/{name}".format(**arg))

        vms = self.to_dict(self.nodes())

        arg = "ssh {} -c {}".format(name, command)
        result = Shell.execute("vagrant", ["ssh", name, "-c", command], cwd=arg.directory)
        return result

    def to_dict(self, lst, id="name"):

        d = {}
        if lst is not None:
            for entry in lst:
                d[entry[id]] = entry
        return d

    def stop(self, name=None):
        """
        stops the node with the given name

        :param name:
        :return: The dict representing the node including updated status
        """
        pass

    def info(self, name=None):
        """
        gets the information of a node with a given name

        :param name:
        :return: The dict representing the node including updated status
        """

        arg = dotdict()
        arg.name = name
        config = Config()

        cloud = "vagrant"  # TODO: must come through parameter or set cloud
        arg.path = config.data["cloudmesh"]["cloud"]["vagrant"]["default"]["path"]
        arg.directory = os.path.expanduser("{path}/{name}".format(**arg))

        result = Shell.execute("vagrant",
                               ["ssh-config"],
                               cwd=arg.directory)
        lines = result.split("\n")
        data = {}
        for line in lines:
            attribute, value = line.strip().split(" ", 1)
            if attribute == "IdentityFile":
                value = value.replace('"', '')

            data[attribute] = value
        return data

    def suspend(self, name=None):
        """
        suspends the node with the given name

        :param name: the name of the node
        :return: The dict representing the node
        """
        # TODO: find last name if name is None
        result = Shell.execute("vagrant", ["suspend", name])
        return result

    def resume(self, name=None):
        """
        resume the named node

        :param name: the name of the node
        :return: the dict of the node
        """
        # TODO: find last name if name is None
        result = Shell.execute("vagrant", ["resume", name])
        return result

    def destroy(self, name=None):
        """
        Destroys the node
        :param name: the name of the node
        :return: the dict of the node
        """
        pass

    @classmethod
    def delete(self, name=None):
        # TODO: check

        arg = dotdict()
        arg.name = name
        config = Config()
        cloud = "vagrant"  # TODO: must come through parameter or set cloud
        arg.path = config.data["cloudmesh"]["cloud"]["vagrant"]["default"]["path"]
        arg.directory = os.path.expanduser("{path}/{name}".format(**arg))

        result = Shell.execute("vagrant",
                               ["destroy", "-f", name],
                               cwd=arg.directory)
        return result

    def vagrantfile(cls, **kwargs):

        arg = dotdict(kwargs)

        provision = kwargs.get("script", None)

        if provision is not None:
            arg.provision = 'config.vm.provision "shell", inline: <<-SHELL\n'
            for line in textwrap.dedent(provision).split("\n"):
                if line.strip() != "":
                    arg.provision += 12 * " " + "    " + line + "\n"
            arg.provision += 12 * " " + "  " + "SHELL\n"
        else:
            arg.provision = ""

        # not sure how I2 gets found TODO verify, comment bellow is not enough
        # the 12 is derived from the indentation of Vagrant in the script
        # TODO we may need not just port 80 to forward
        script = textwrap.dedent("""
               Vagrant.configure(2) do |config|

                 config.vm.define "{name}"
                 config.vm.hostname = "{name}"
                 config.vm.box = "{image}"
                 config.vm.box_check_update = true
                 config.vm.network "forwarded_port", guest: 80, host: {port}
                 config.vm.network "private_network", type: "dhcp"

                 # config.vm.network "public_network"
                 # config.vm.synced_folder "../data", "/vagrant_data"
                 config.vm.provider "virtualbox" do |vb|
                    # vb.gui = true
                    vb.memory = "{memory}"
                 end
                 {provision}
               end
           """.format(**arg))

        return script


    def _get_specification(self, cloud=None, name=None, port=None, image=None, **kwargs):
        arg = dotdict(kwargs)
        arg.port = port
        config = Config()
        pprint (config.data)


        if cloud is None:
            #
            # TOD read default cloud
            #
            cloud = "vagrant"  # TODO must come through parameter or set cloud


        print("CCC", cloud)
        spec = config.data["cloudmesh"]["cloud"][cloud]
        pprint(spec)
        default = spec["default"]
        pprint(default)

        if name is not None:
            arg.name = name
        else:
            # TODO get new name
            pass

        if image is not None:
            arg.image = image
        else:
            arg.image = default["image"]
            pass


        arg.path = default["path"]
        arg.directory = os.path.expanduser("{path}/{name}".format(**arg))
        arg.vagrantfile = "{directory}/Vagrantfile".format(**arg)
        return arg

    def create(self, name=None, image=None, size=None, timeout=360, port=80, **kwargs):
        """
        creates a named node

        :param port:
        :param name: the name of the node
        :param image: the image used
        :param size: the size of the image
        :param timeout: a timeout in seconds that is invoked in case the image does not boot.
               The default is set to 3 minutes.
        :param kwargs: additional arguments passed along at time of boot
        :return:
        """
        """
        create one node
        """

        #
        # TODO BUG: if name contains not just letters and numbers and - return error, e. undersore not allowed
        #

        arg = self._get_specification(name=name, image=image, size=size, timeout=timeout, port=port, **kwargs)

        if not os.path.exists(arg.directory):
            os.makedirs(arg.directory)


        configuration = self.vagrantfile(**arg)

        with open(arg.vagrantfile, 'w') as f:
            f.write(configuration)

        pprint(arg)

        return arg

    def rename(self, name=None, destination=None):
        """
        rename a node

        :param name: the current name
        :param new_name: the new name
        :return: the dict with the new name
        """
        # if destination is None, increase the name counter and use the new name
        pass

    #
    # Additional methods
    #

    @classmethod
    def find_image(cls, keywords):
        """
        Finds an image on hashicorps web site

        :param keywords: The keywords to narrow down the search
        """
        d = {
            'key': '+'.join(keywords),
            'location': "https://app.vagrantup.com/boxes/search"
        }
        link = "{location}?utf8=%E2%9C%93&sort=downloads&provider=&q=\"{key}\"".format(**d)
        webbrowser.open(link, new=2, autoraise=True)

    @classmethod
    def add_image(cls, name=None):
        result = ""
        if name is None:
            pass
            return "ERROR: please specify an image name"
            # read name form config
        else:
            try:
                # result = Shell.execute("vagrant", ["box", "add", name])
                os.system("vagrant box add {name}".format(name=name))
            except Exception as e:
                print(e)

            return result

    @classmethod
    def delete_image(cls, name=None):
        result = ""
        if name is None:
            pass
            return "ERROR: please specify an image name"
            # read name form config
        else:
            try:
                # result = Shell.execute("vagrant", ["box", "remove", name])
                os.system("vagrant box remove {name}".format(name=name))
            except Exception as e:
                print(e)

            return result

    @classmethod
    def list_images(cls):
        def convert(line):
            line = line.replace("(", "")
            line = line.replace(")", "")
            line = line.replace(",", "")
            entry = line.split(" ")
            data = dotdict()
            data.name = entry[0]
            data.provider = entry[1]
            data.date = entry[2]
            return data

        result = Shell.execute("vagrant", ["box", "list"])

        if "There are no installed boxes" in result:
            return None
        else:
            result = result.split("\n")
        lines = []
        for line in result:
            lines.append(convert(line))

        return lines