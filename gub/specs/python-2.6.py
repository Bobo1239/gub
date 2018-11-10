from gub import misc
from gub import target
from gub import tools
python = misc.load_spec ('python-2.4')

def get_conflict_dict (self):
    return {
        '': ['python-2.4', 'python'],
        'doc': ['python-2.4-doc', 'python-doc'],
        'devel': ['python-2.4-devel', 'python-devel'],
        'runtime': ['python-2.4-runtime', 'python-runtime'],
        }

class Python_2_6 (python.Python_2_4):
    source = 'http://www.python.org/ftp/python/2.6.4/Python-2.6.4.tar.bz2'
    dependencies = [
        'db-devel',
        'expat-devel',
        'libffi-devel',
        'zlib-devel',
        'tools::python-2.6',
        ]
    patches = [
        'python-2.6.4.patch',
        'python-2.6.4-hashlib.patch',
        'python-configure.in-posix.patch&strip=0',
        'python-2.6.4-configure.in-sysname.patch',
        'python-2.4.2-configure.in-sysrelease.patch',
        'python-2.4.2-setup.py-import.patch&strip=0',
        'python-2.6.4-setup.py-cross_root.patch',
#        'python-2.4.2-fno-stack-protector.patch',
#        'python-2.4.5-python-2.6.patch',
        'python-2.4.5-native.patch',
#        'python-2.4.5-db4.7.patch',
        'python-2.6.4-configure.in-cross.patch',
        'python-2.6.4-include-pc.patch',
        'python-2.6.4-setup-cross.patch',
        'python-2.6.4-unixcompiler-libtool.patch',
        ]
    config_cache_overrides = python.Python_2_4.config_cache_overrides + '''
ac_cv_have_chflags=no
ac_cv_have_lchflags=no
ac_cv_py_format_size_t=no
'''
    so_modules = [
        '_struct',
        'datetime',
        'itertools',
        'time',
        ]
    configure_flags = (python.Python_2_4.configure_flags
                       + ' --with-system-ffi')
    get_conflict_dict = get_conflict_dict
    def python_version (self):
        return '2.6'

class Python_2_6__mingw (python.Python_2_4__mingw):
    source = Python_2_6.source
    patches = Python_2_6.patches + [
        'python-2.4.2-winsock2.patch',
        'python-2.4.2-setup.py-selectmodule.patch',
        'python-2.4.5-disable-pwd-mingw.patch',
        'python-2.6.4-mingw-site.patch',
        'python-2.4.5-mingw-socketmodule.patch',
        'python-2.6.4-mingw-ctypes.patch',
        ]
    dependencies = Python_2_6.dependencies + ['pthreads-w32-devel']
    config_cache_overrides = python.Python_2_4__mingw.config_cache_overrides + '''
ac_cv_have_chflags=no
ac_cv_have_lchflags=no
ac_cv_py_format_size_t=no
'''
    so_modules = Python_2_6.so_modules
    get_conflict_dict = get_conflict_dict
    configure_flags = (python.Python_2_4__mingw.configure_flags
                       + ' --with-system-ffi')
    def patch (self):
        python.Python_2_4__mingw.patch (self)
        self.system ('cd %(srcdir)s && cp -pv PC/dl_nt.c Python/fileblocks.c')
    def generate_dll_a_and_la (self, libname, depend=''):
        target.AutoBuild.generate_dll_a_and_la (self, 'python%(python_version)s', depend)
    def configure (self):
        Python_2_4__mingw.configure (self)

class Python_2_6__linux__ppc (Python_2_6):
    pass

class Python_2_6__freebsd (Python_2_6):
    def configure (self):
        Python_2_6.configure (self)
        self.file_sub ([
                ('^CFLAGSFORSHARED=.*', 'CFLAGSFORSHARED = -fPIC'),
                ('^LDLIBRARY=.*', 'LDLIBRARY = libpython$(VERSION).so'),
                ('^INSTSONAME=.*', 'INSTSONAME = libpython$(VERSION).so.0.1'),
                ], '%(builddir)s/Makefile')
        # avoid re-running makesetup and overwriting Makefile
        self.system ('cd %(builddir)s && make Modules/config.c')

class Python_2_6__tools (tools.AutoBuild, Python_2_6):
    patches = [
        'python-2.6.4-hashlib.patch',
        'python-2.6.4-readline.patch',
        'python-2.6.4-setup-cross.patch',
        ]
    dependencies = [
        'autoconf',
        'db', # _bsddb
        'libffi',
        'libtool',
        ]
    force_autoupdate = True
    parallel_build_broken = True
    not_supported = ['nis', 'crypt']
    configure_flags = (tools.AutoBuild.configure_flags
                       + ' --with-system-ffi')
    def patch (self):
        Python_2_6.patch (self)
    def configure (self):
        tools.AutoBuild.configure (self)
        self.file_sub ([
                ('^LDSHARED=.*', 'LDSHARED = $(CC) -shared -fPIC'),
                ('BLDSHARED=.*', 'BLDSHARED = $(CC) -shared -fPIC -L. -lpython%(python_version)s'),
                ], '%(builddir)s/Makefile')
        # avoid re-running makesetup and overwriting Makefile
        self.system ('cd %(builddir)s && make Modules/config.c')
