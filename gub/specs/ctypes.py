from gub import target
from gub import tools

class Ctypes (target.PythonBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/ctypes/ctypes/1.0.2/ctypes-1.0.2.tar.gz'
    install_command = 'cd %(srcdir)s && python %(srcdir)s/setup.py install --prefix=%(prefix_dir)s --root=%(install_root)s'
    subpackage_names = ['']
    dependencies = [
        'libffi',
        'python',
        ]
    python_version = tools.python_version
    def patch (self):
        target.PythonBuild.patch (self)
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
            open (setup, 'w').write (self.expand (dist_fix) + s)
        self.func (defer)
        self.file_sub ([('config_args = [[][]]', '''config_args = [
' --cache-file=%(srcdir)s/config.cache'
' --enable-shared'
' --disable-static'
' --disable-silent-rules'
' --build=%(build_architecture)s'
' --host=%(target_architecture)s'
' --target=%(target_architecture)s'
' --prefix=%(prefix_dir)s'
' --sysconfdir=%(prefix_dir)s/etc'
' --includedir=%(prefix_dir)s/include'
' --infodir=%(prefix_dir)s/share/info'
' --mandir=%(prefix_dir)s/share/man'
' --libdir=%(prefix_dir)s/lib'
' CFLAGS=-I%(system_prefix)s/include/python%(python_version)s'
]
'''
)],
                       '%(srcdir)s/setup.py')
        self.file_sub ([("""LIBFFI_SOURCES='source/libffi'""",
                         'LIBFFI_SOURCES = None'),],
                       '%(srcdir)s/setup.py')

class Ctypes__mingw (Ctypes):
    patches = Ctypes.patches + [
        'ctypes-mingw.patch',
        ]
    install_command = 'cd %(srcdir)s && SO=%(so_extension)s LDSHARED="$CC -shared" LDFLAGS="-L%(system_prefix)s/bin -lpython%(python_version)s" CFLAGS="-DMS_WIN32" python %(srcdir)s/setup.py install --prefix=%(prefix_dir)s --root=%(install_root)s'
    def patch (self):
        Ctypes.patch (self)
        self.file_sub ([('-fPIC', '-DMS_WIN32',)], '%(srcdir)s/setup.py')
        self.file_sub ([('''[[]'python%(python_version)s'[]]''',
                         '''['python%(python_version)s', 'ffi', 'ole32', 'oleaut32', 'uuid']''')],
                       '%(srcdir)s/setup.py')
    def install (self):
        Ctypes.install (self)
        self.system ('cd %(install_prefix)s/lib/python%(python_version)s/site-packages && mv _ctypes.so _ctypes.dll')
        self.system ('cd %(install_prefix)s/lib/python%(python_version)s/site-packages && mv _ctypes_test.so _ctypes_test.dll')
