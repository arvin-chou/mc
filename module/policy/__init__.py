#import os
#import glob
#modules = glob.glob(os.path.dirname(__file__)+"/*.py")
#__all__ = [ os.path.basename(f)[:-3] for f in modules]
__policies_security_tablename__ = 'policies_security'
__policies_security_head__ = 'secpolicy'
__policies_security_heads__ = 'secpolicies'

# one to many
__policies_security_ipaddrs_table__ = 'policies_security_ipaddrs'
__policies_security_ipgroups_table__ = 'policies_security_ipgroups'
