from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dcnm import DCNM, dcnm_argument_spec
import json


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dcnm_argument_spec
    module_args.update(
    fabric_name=dict(type='str', required=False),
    network_name=dict(type='str', required=True),
    lan_AttachList= dict(type=list, required=False),
    state=dict(type='str', choices=['present', 'absent'], default='present'),
    )

    # seed the result dict
    result = dict(
        changed=False,
        ansible_facts=dict()
    )

    module = AnsibleModule(
       argument_spec=module_args,
       supports_check_mode=True
    )


    
    dcnm = DCNM(module.params['baseurl'], module.params['username'], module.params['password'], verify=module.params['verify'])

    dcnm.login()

    net = dcnm.get_net(module.params['fabric_name'], module.params['network_name'])

        # Handle state==absent cases
                
    dcnm.attach_net(module.params['fabric_name'],module.params)
    dcnm.deploy_net(module.params['fabric_name'],module.params)
    result['changed'] = True
    module.exit_json(**result)
       

   
        

def main():
    run_module()

if __name__ == '__main__':
    main()