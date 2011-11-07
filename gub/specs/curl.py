from gub import context
from gub import target
from gub import tools

class Curl (target.AutoBuild):
    source = 'http://curl.haxx.se/download/curl-7.22.0.tar.gz'
    dependencies = ['tools::libtool']
    configure_flags = (tools.AutoBuild.configure_flags
                       + ' --without-openssl')
    def install (self):
        target.AutoBuild.install (self)
        self.system ('mkdir -p %(install_prefix)s%(cross_dir)s/bin')
        self.system ('cp %(install_prefix)s/bin/curl-config %(install_prefix)s%(cross_dir)s/bin/curl-config')
        self.file_sub ([('%(system_prefix)s', '%(prefix_dir)s')]
                       , '%(install_prefix)s/bin/curl-config')
    @context.subst_method
    def config_script (self):
        return 'curl-config'

class Curl__tools (tools.AutoBuild, Curl):
    dependencies = ['libtool']
    configure_flags = (tools.AutoBuild.configure_flags
                       + ' --without-openssl')

