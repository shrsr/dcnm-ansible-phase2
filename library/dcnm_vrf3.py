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

    # Collect result dict
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
        dcnm.deploy_vrf(module.params['fabric_name'],module.params)
        module.exit_json(**result)
                
    except Exception as e:
        module.fail_json(msg=str(e), result=result)

def main():
    run_module()

if __name__ == '__main__':
    main()