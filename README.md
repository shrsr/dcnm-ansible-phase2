# dcnm-ansible-phase2

This repo. is an extension to Chris': https://github.com/cgascoig/dcnm-ansible.git

******************************************************

##### Added Libraries: 
1. dcnm_vrf2.py - Attach VRF
2. dcnm_vrf3.py - Deploy VRF

******************************************************

##### Added methods and attributes to dcnm.py in module_utils:

```python
def attach_vrf(self,fabric_name,module_params):
    body = self.generate_body(module_params, self.VRF_ATTRS2)
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
            
            
    VRF_ATTRS2 = {
        "lanAttachList": "lan_AttachList",
    }

    VRF_ATTRS3 = {
       
    }
```
****************************************************************
##### New tasks in playbook:
```playbook
 - name: attach VRF
      dcnm_vrf2:
        <<: *api_info 
        fabric_name: Demo
        vrf_name: "vrf1"
        lan_AttachList:
                  - fabric: Demo
                    vrfName: "vrf1"
                    serialNumber: "9NCHKKHXDBN"
                    vlan: 200
                    deployment: "true"
                    extensionValues: ""
                    instanceValues: ""
                    freeformConfig: ""

    - pause:
        seconds: 15

    - name: deploy VRF
        dcnm_vrf3:
          <<: *api_info 
          fabric_name: Demo
          vrf_name: "vrf1"
          lan_AttachList:
                  - fabric: Demo
                    vrfName: "vrf1"
                    serialNumber: "9NCHKKHXDBN"
                    vlan: 200
                    deployment: "true"
                    extensionValues: ""
                    instanceValues: ""
                    freeformConfig: ""
```
*************************************************************

##### Very similar methods and tasks apply to attach/deployment of network.

**************************************************************

##### An example for String Manipulation that might come in handy for idempotency at a later time:
- vrf = dcnm.get_vrfDep(module.params['fabric_name'])
- vrf=json.dumps(vrf)
- v=json.dumps(vrf)
- vrf = re.sub(r"[\[\]]", '', v)
- vrf=json.loads(vrf)
- if(module.params['vrf_name']==vrf["vrfName"]) and (vrf["vrfStatus"]=="NA"):
        
   
        
