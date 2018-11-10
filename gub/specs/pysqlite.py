import re
#
from gub import target
from gub import tools

class Pysqlite (target.PythonBuild):
    source = 'https://pypi.python.org/packages/source/p/pysqlite/pysqlite-2.6.0.tar.gz'
    subpackage_names = ['']
    python_version = tools.python_version
    def patch (self):
        def defer (logger):
            dist_fix = '''
import os
import sys
from distutils import sysconfig
def get_python_inc(plat_specific=0, prefix='%(system_prefix)s'):
    return os.path.join(prefix, "include", "python" + sys.version[:3])
sysconfig.get_python_inc = get_python_inc

from distutils.command import build_ext
build_ext.build_ext._get_libraries = build_ext.build_ext.get_libraries
def get_libraries (self, ext):
    return self._get_libraries (ext) + ['python%(python_version)s']
build_ext.build_ext.get_libraries = get_libraries
'''
            setup = self.expand ('%(srcdir)s/setup.py')
            s = open (setup).read ()
            s = re.sub (' H..?ring ', 'Haering', s)
            open (setup, 'w').write (self.expand (dist_fix) + s)
        self.func (defer)
    install_command = 'cd %(srcdir)s && SO=%(so_extension)s LDSHARED="$CC -shared" LDFLAGS="-L%(system_prefix)s/bin -lpython%(python_version)s" CFLAGS="--verbose" python %(srcdir)s/setup.py install --prefix=%(prefix_dir)s --root=%(install_root)s'
    dependencies = [
        'python',
        'sqlite',
        'tools::setuptools',
        ]

class Pysqlite__mingw (Pysqlite):
    def install (self):
        Pysqlite.install (self)
        self.system ('cd %(install_prefix)s/lib/python%(python_version)s/site-packages/pysqlite2 && mv _sqlite.so _sqlite.dll')
