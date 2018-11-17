# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 23:58:09 2018

@author: Rui
"""

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
import os
from cm4.configuration.config import Config
import cm4.vm.VmUtil as util


###
### provide generic methods to manipulate nodes from various providers by name

class VmRefactor(object):
    def __init__(self, vm):
        self.config = Config()
        self.vm = vm


    def confirm_resize(self, name):
        '''
        confirm a resizing request for a node
        :param: node_id
        :return: bool
        '''
        node = self.get_node_by_name(name)
        node_id = node.id
        return self.vm.provider.ex_confirm_resize(node)


    def resize(self, name, size):
        '''
        resize a node
        :param: node_id, new size object
        :return: bool
        '''
        node = self.get_node_by_name(name)
        node_id = node.id
        return self.vm.provider.ex_resize(node, size)


    def revert_resize(self, name):
        '''
        revert previous resize request
        :param: node_id
        :return: bool
        '''
        node = self.get_node_by_name(name)
        node_id = node.id
        return self.vm.provider.ex_revert_resize(node)


    # rebuild node with new image
    def rebuild(self, name, image):
        '''
        refactor node to a different image
        :param: node id, new image object
        :return: Node
        '''
        node = self.get_node_by_name(name)
        node_id = node.id
        return self.vm.provider.ex_rebuild(node, image=image)


    def rename(self, name, newname):
        '''
        rename a node by its id
        :param: name: new name for node
        :return: Node
        '''
        node = self.get_node_by_name(name)
        node_id = node.id
        return self.vm.provider.ex_set_server_name(node, newname)


    def list(self):
        """
        list existed nodes
        :return: all nodes' information
        """
        result = self.cloud.driver.list_nodes()
        return result


    def get_node_by_name(self, name):
        """
        show node information based on id
        :param node_id:
        :return: all information about one node
        """
        nodes = self.list()
        for i in nodes:
            if i.name == name:
                document = vars(i)
                self.mongo.update_document('cloud', 'name', name, document)
                return i
        raise ValueError('Node with name: \"'+name+'\" was not found!')