from gub import build
from gub import misc
from gub import tools

class Python_config (build.SdkBuild):
    source = 'url://host/python-config-' + tools.python_version + '.tar.gz'
    dependencies = ['tools::python']
    def install (self):
        build.SdkBuild.install (self)
        misc.dump_python_config (self)
