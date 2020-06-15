# -*- coding: utf-8 -*-
"""dcnm_facts module
Copyright (c) 2019 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__copyright__ = "Copyright (c) 2019 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.0"
__author__ = "Chris Gascoigne"

import requests
import sys
import json
import yaml
import time

dcnm_argument_spec = dict(
    baseurl=dict(type='str', required=True),
    u=dict(type='str', required=True),
    p=dict(type='str', required=True),
    verify=dict(type='bool', required=False, default=True),
)


class DCNM(object):
    def __init__(self, baseurl, u, p, verify=True):
        self.u = u
        self.p = p
        self.verify = verify
        self.baseurl = baseurl
        self.token=None

    def get_url(self, endpoint):
        return self.baseurl + endpoint

    def login(self):
        payload = "{'expirationTime': 999999999}"
        body = {
            'expirationTime': 99999999999
        }
        headers = {
            'Content-Type': "application/json",
        }

        auth = requests.auth.HTTPBasicAuth(self.u, self.p)
        url = self.get_url("/logon")

        try:
            response = requests.request("POST", url, auth=auth, json=body, headers=headers, verify=self.verify)

            js = response.json()
            self.token = js["Dcnm-Token"]

            print("DCNM authenticated, token %s"%self.token)
        except Exception as e:
            raise Exception("An error occurred while authenticating to DCNM: %s"%e)
            return None
        
        return self.token

    def request(self, method, endpoint, json=None):
        url = self.get_url(endpoint)
        headers = {
            'Dcnm-Token': self.token
        }
        try:
            response = requests.request(method, url, json=json, headers=headers, verify=self.verify)

            if not response.ok:
                raise Exception("%s: %s"%(response.reason, response.text))

            try:
                ret=response.json()
            except ValueError:
                ret=None

            return ret
        except Exception as e:
            raise Exception("An error has occurred while sending request to DCNM: %s" % e)
            return None


    # Switch related methods
    def importSwitches(self,module_params):
        body = self.generate_body(module_params, self.SWITCH_ATTRS)
        
        header = {'Dcnm-Token': self.login(), 'Content-Type': 'application/json'}
        switch = requests.post(self.baseurl + '/control/fabrics/Demo/inventory/discover',
                                      data=body,
                                      headers=header,
                                      verify=False)
        return switch
        #if self.token is None:
         #   raise Exception("Attempt to import switch before authentication")
        '''
        try:
            #switch = self.request("POST", "/control/fabrics/%s/inventory/discover"%(module_params['fabric_name']),json=body)
           
                        
           return switch
        except Exception as e:
            raise Exception("An error occurred while importing the switch: %s"%e)
       
'''

    ''' def importSwitches(self, dcnm_token):
        print("Importing switches begins: ")
        postURL = self.url + '/rest/control/fabrics/' + self.ext + '/inventory/discover'
        header = {'Dcnm-Token': dcnm_token, 'Content-Type': 'application/json'}
        with open('switchesImport.json', 'r') as json_file:
            content = json_file.read()
            response = requests.post(postURL,
                                      data=content,
                                      headers=header,
                                      verify=False)'''

    SWITCH_ATTRS = {
        "username":"user",
        "password":"pwd",
        "switches":"sw",
    }
    #################################
    # VRF related methods
    #################################
    def get_vrf(self, fabric_name, vrf_name):
        if self.token is None:
            raise Exception("Attempt to get VRF info before authentication")

        try:
            vrf=self.request("GET", "/top-down/fabrics/%s/vrfs/%s"%(fabric_name, vrf_name))
            return vrf
        except:
            # assume any exception means the VRF doesn't exist
            return None

    def delete_vrf(self, fabric_name, vrf_name):
        if self.token is None:
            raise Exception("Attempt to delete VRF before authentication")

        try:
            vrf=self.request("DELETE", "/top-down/fabrics/%s/vrfs/%s"%(fabric_name, vrf_name))
            return vrf
        except Exception as e:
            raise Exception("An error occurred while deleting VRF: %s" % e)

    def create_vrf(self, module_params):
        body = self.generate_body(module_params, self.VRF_ATTRS)
        body.update(
            fabric=module_params['fabric_name'],
            vrfName=module_params['vrf_name'],
            vrfId=module_params['vrf_id'],
        )

        if self.token is None:
            raise Exception("Attempt to create VRF info before authentication")
        
        try:
            vrf = self.request("POST", "/top-down/fabrics/%s/vrfs"%module_params['fabric_name'], json=body)
            return vrf
        except Exception as e:
            raise Exception("An error occurred while creating VRF: %s"%e)
    
    def update_vrf(self, module_params):
        body = self.generate_body(module_params, self.VRF_ATTRS)
        body.update(
            fabric=module_params['fabric_name'],
            vrfName=module_params['vrf_name'],
            vrfId=module_params['vrf_id'],
        )

        if self.token is None:
            raise Exception("Attempt to update VRF info before authentication")
        
        try:
            vrf = self.request("PUT", "/top-down/fabrics/%s/vrfs/%s"%(module_params['fabric_name'], module_params['vrf_name']), json=body)
            return vrf
        except Exception as e:
            raise Exception("An error occurred while updating VRF: %s"%e)
     
     # New method attach vrf       
    def attach_vrf(self,fabric_name,module_params):
        body = self.generate_body(module_params, self.VRF_ATTRS2)
        # body is the content for posting payload while POST
        body.update(
           
            vrfName=module_params['vrf_name'],
        )
        array=[]
        array.append(body)
        try:
            vrf = self.request("POST", "/top-down/fabrics/%s/vrfs/attachments"%(fabric_name),json=array)
            return vrf
        except Exception as e:
            raise Exception("An error occurred while attaching VRF: %s"%e)

    # New method deploy vrf          
    def deploy_vrf(self,fabric_name,module_params):
        body = self.generate_body(module_params, self.VRF_ATTRS3)
        body.update(
         vrfNames=module_params['vrf_name'],
        )
       
        try:
            vrf = self.request("POST", "/top-down/fabrics/%s/vrfs/deployments"%(fabric_name), json=body)
            return vrf
        except Exception as e:
            raise Exception("An error occurred while deploying VRF: %s"%e)

    # return True if update needed

    def get_vrfDep(self,fabric_name):
        try:
            vrf = self.request("GET", "/top-down/fabrics/%s/vrfs"%(fabric_name))
            return vrf
        except Exception as e:
            raise Exception("An error occurred while deploying VRF: %s"%e)

    def compare_vrf_attrs(self, js, yaml):
        return self.compare_attrs(js, yaml, self.VRF_ATTRS)

    def compare_vrf_attrs2(self, js, yaml):
        return self.compare_attrs2(js, yaml, self.VRF_ATTRS2)

    VRF_ATTRS = {
        "vrfTemplate": "vrf_template",
        "vrfExtensionTemplate": "vrf_extension_template",
        "vrfTemplateConfig": "vrf_template_config",
        "vrfId": "vrf_id",
    }

    VRF_ATTRS2 = {
        "lanAttachList": "lan_AttachList",
    }

    VRF_ATTRS3 = {
       
    }

    #################################
    # Network related methods
    #################################

    def get_net(self, fabric_name, net_name):
        if self.token is None:
            raise Exception("Attempt to get network info before authentication")

        try:
            net=self.request("GET", "/top-down/fabrics/%s/networks/%s"%(fabric_name, net_name))
            return net
        except:
            # assume any exception means the network doesn't exist
            return None

    def delete_net(self, fabric_name, net_name):
        if self.token is None:
            raise Exception("Attempt to delete network before authentication")

        try:
            net=self.request("DELETE", "/top-down/fabrics/%s/networks/%s"%(fabric_name, net_name))
            return net
        except Exception as e:
            raise Exception("An error occurred while deleting network: %s" % e)

    def create_net(self, module_params):
        body = self.generate_body(module_params, self.NET_ATTRS)
        body.update(
            fabric=module_params['fabric_name'],
            vrf=module_params['vrf_name'],
            networkName=module_params['network_name'],
        )

        if self.token is None:
            raise Exception("Attempt to create network info before authentication")
        
        try:
            net = self.request("POST", "/top-down/fabrics/%s/networks"%module_params['fabric_name'], json=body)
            return net
        except Exception as e:
            raise Exception("An error occurred while creating network: %s"%e)
    
    def update_net(self, module_params):
        body = self.generate_body(module_params, self.NET_ATTRS)
        body.update(
            fabric=module_params['fabric_name'],
            vrf=module_params['vrf_name'],
            networkName=module_params['network_name'],
        )

        if self.token is None:
            raise Exception("Attempt to update network info before authentication")
        
        try:
            net = self.request("PUT", "/top-down/fabrics/%s/networks/%s"%(module_params['fabric_name'], module_params['network_name']), json=body)
            return net
        except Exception as e:
            raise Exception("An error occurred while updating network: %s"%e)
    
    def attach_net(self,fabric_name,module_params):
        body = self.generate_body(module_params, self.NET_ATTRS2)
        # body is the content for posting payload while POST
        body.update(
            
            networkName=module_params['network_name'],
        )
        array=[]
        array.append(body)
        try:
            net = self.request("POST", "/top-down/fabrics/%s/networks/attachments"%(fabric_name),json=array)
            return net
        except Exception as e:
            raise Exception("An error occurred while attaching Network: %s"%e)

    def deploy_net(self,fabric_name,module_params):
        body = self.generate_body(module_params, self.NET_ATTRS3)
        body.update(
         networkNames=module_params['network_name'],
        )
       
        try:
            net = self.request("POST", "/top-down/fabrics/%s/networks/deployments"%(fabric_name), json=body)
            return net
        except Exception as e:
            raise Exception("An error occurred while deploying Network: %s"%e)


    # return True if update needed
    def compare_net_attrs(self, js, yaml):
        return self.compare_attrs(js, yaml, self.NET_ATTRS)

    def compare_net_attrs2(self, js, yaml):
        return self.compare_attrs(js, yaml, self.NET_ATTRS2)


    NET_ATTRS = {
        "networkTemplate": "network_template",
        "networkExtensionTemplate": "network_extension_template",
        "networkTemplateConfig": "network_template_config",
        "networkId": "network_id",
    }

    NET_ATTRS2 = {
        "lanAttachList": "lan_AttachList",
    }

    NET_ATTRS3 = {
       
    }

    #################################
    # Genric utility methods
    #################################
    
    # return True if update needed
    def compare_attrs(self, js, yaml, attrmap):
        need_update=False
        for jsattr, yamlattr in attrmap.iteritems():
            if type(yaml[yamlattr]) is dict:
                # if the attribute in the yaml is a dict, parse the json attribute as json
                # this handles the vrfTemplateConfig and networkTemplateConfig attributes which are actually JSON encoded strings in the API
                if json.loads(js[jsattr]) != yaml[yamlattr]:
                    need_update = True
            else:
                if js[jsattr] != yaml[yamlattr]:
                    need_update = True

        return need_update




    def compare_attrs2(self, js, yaml, attrmap):
        
        x = json.dumps(yaml)
        if (sorted(x.items()) == sorted(js.items())):
            need_update= False
        else:
            need_update = True
        return need_update

       


    def generate_body(self, module_params, attrmap):
        body=dict()
        for jsattr, yamlattr in attrmap.iteritems():
            # if the attribute in the module_params is a dict, dump the attribute as json
            # this handles the vrfTemplateConfig and networkTemplateConfig attributes which are actually JSON encoded strings in the API
            if type(module_params[yamlattr]) is dict:
                body[jsattr] = json.dumps(module_params[yamlattr])
            else:
                body[jsattr] = module_params[yamlattr]
        
        return body


    ''' for y in attrmap.values()[0]:
            for x in y:
                json.loads(x)
                for jsattr, yamlattr in x:
                    if type(yaml[yamlattr]) is dict:
                # if the attribute in the yaml is a dict, parse the json attribute as json
                # this handles the vrfTemplateConfig and networkTemplateConfig attributes which are actually JSON encoded strings in the API
                        if json.loads(js[jsattr]) != yaml[yamlattr]:
                            need_update = True
                    else:
                        if js[jsattr] != yaml[yamlattr]:
                            need_update = True

        return need_update'''
        
   