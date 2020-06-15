from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dcnm import DCNM, dcnm_argument_spec
import json
import re


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dcnm_argument_spec
    # the values you're entering on playbook
    module_args.update(
    fabric_name=dict(type='str', required=False),
    vrf_name=dict(type='str', required=False),
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

    try:
        dcnm = DCNM(module.params['baseurl'], module.params['username'], module.params['password'], verify=module.params['verify'])
        dcnm.login()
        #vrf = dcnm.get_vrf(module.params['fabric_name'], module.params['vrf_name'])
        #need_update = dcnm.compare_vrf_attrs(vrf, module.params)
        #if need_update:
        dcnm.attach_vrf(module.params['fabric_name'],module.params)
        #result['changed'] = True
        module.exit_json(**result)
        #else:
            #module.exit_json(**result)
                
    except Exception as e:
        module.fail_json(msg=str(e), result=result)
def main():
    run_module()

if __name__ == '__main__':
    main()