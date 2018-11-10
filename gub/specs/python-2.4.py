import re
#
from gub import build
from gub import context
from gub import misc
from gub import target
from gub import tools

class Python_2_4 (target.AutoBuild):
    source = 'https://www.python.org/ftp/python/2.4.5/Python-2.4.5.tar.bz2'
    #source = 'https://www.python.org/ftp/python/2.4.2/Python-2.4.2.tar.bz2'
    patches_242 = [
        'python-2.4.2-1.patch',
        'python-configure.in-posix.patch&strip=0',
        'python-configure.in-sysname.patch&strip=0',
        'python-2.4.2-configure.in-sysrelease.patch',
        'python-2.4.2-setup.py-import.patch&strip=0',
        'python-2.4.2-setup.py-cross_root.patch&strip=0',
        'python-2.4.2-fno-stack-protector.patch',
        ]

    patches = [
        'python-2.4.5-1.patch',
        'python-configure.in-posix.patch&strip=0',
        'python-2.4.5-configure.in-sysname.patch',
        'python-2.4.2-configure.in-sysrelease.patch',
        'python-2.4.2-setup.py-import.patch&strip=0',
        'python-2.4.2-setup.py-cross_root.patch&strip=0',
#        'python-2.4.2-fno-stack-protector.patch',
        'python-2.4.5-python-2.6.patch',
        'python-2.4.5-native.patch',
        'python-2.4.5-db4.7.patch',
        'python-2.4.5-setup-cross.patch',
        'python-2.6.4-unixcompiler-libtool.patch',
        ]
    dependencies = [
        'db-devel',
        'expat-devel',
        'zlib-devel',
        'tools::python-2.4'
        ]
    force_autoupdate = True
    parallel_build_broken = True
    subpackage_names = ['doc', 'devel', 'runtime', '']
    so_modules = [
        'itertools',
        'struct',
        'time',
        ]
    not_supported = []
    def python_version (self):
        return '2.4'
    def get_conflict_dict (self):
        return {
            '': ['python-2.6', 'python-2.4'],
            'doc': ['python-2.6-doc', 'python-2.4-doc'],
            'devel': ['python-2.6-devel', 'python-2.4-devel'],
            'runtime': ['python-2.6-runtime', 'python-2.4-runtime'],
            }
    def __init__ (self, settings, source):
        target.AutoBuild.__init__ (self, settings, source)
        self.CROSS_ROOT = '%(targetdir)s'
        if 'stat' in misc.librestrict ():
            self.install_command = ('LIBRESTRICT_ALLOW=/usr/lib/python%(python_version)s/lib-dynload:${LIBRESTRICT_ALLOW-/foo} '
                + target.AutoBuild.install_command)
    def patch (self):
        target.AutoBuild.patch (self)
        self.file_sub ([('@CC@', '@CC@ -I%(builddir)s')],
                        '%(srcdir)s/Makefile.pre.in')
    def autoupdate (self):
        target.AutoBuild.autoupdate (self)
        # FIXME: REMOVEME/PROMOTEME to target.py?
        if self.settings.build_platform == self.settings.target_platform:
            self.file_sub ([('cross_compiling=(maybe|no|yes)',
                             'cross_compiling=no')], '%(srcdir)s/configure')
    def configure (self):
        target.AutoBuild.configure (self)
        self.file_sub ([
                ('^CCSHARED=.*', 'CCSHARED = -fPIC'),
                ('^CFLAGSFORSHARED=.*', 'CFLAGSFORSHARED = -fPIC'),
                ('^LDSHARED=.*', 'LDSHARED = $(CC) -shared -fPIC'),
                ('BLDSHARED=.*', 'BLDSHARED = $(CC) -shared -fPIC -L. -lpython%(python_version)s'),
                ('^BLDLIBRARY=.*', 'BLDLIBRARY = %(rpath)s -L. -lpython$(VERSION)'),
                ], '%(builddir)s/Makefile')
        # avoid re-running makesetup and overwriting Makefile
        self.system ('cd %(builddir)s && make Modules/config.c')
    def install (self):
        target.AutoBuild.install (self)
        misc.dump_python_config (self)
        def assert_fine (logger):
            dynload_dir = self.expand ('%(install_prefix)s/lib/python%(python_version)s/lib-dynload')
            so = self.expand ('%(so_extension)s')
            all = [x.replace (dynload_dir + '/', '') for x in misc.find_files (dynload_dir, '.*' + so)]
            failed = [x.replace (dynload_dir + '/', '') for x in misc.find_files (dynload_dir, '.*failed' + so)]
            for i in self.not_supported:
                m = i + '_failed' + so
                if m in failed:
                    failed.remove (m)
            if failed:
                logger.write_log ('failed python modules:' + ', '.join (failed), 'error')
            for module in self.so_modules:
                if not module + so in all:
                    logger.write_log ('all python modules:' + ', '.join (all), 'error')
                    raise Exception ('Python module failed: ' + module)
        self.func (assert_fine)
    ### Ugh.
    @context.subst_method
    def python_version (self):
        return '.'.join (self.version ().split ('.')[0:2])

class Python_2_4__mingw_binary (build.BinaryBuild):
    source = 'http://lilypond.org/~hanwen/python-2.4.2-windows.tar.gz'

    def install (self):
        build.BinaryBuild.install (self)
        self.system ('''
cd %(install_root)s && mkdir usr && mv Python24/include usr
cd %(install_root)s && mkdir -p usr/bin/ && mv Python24/* usr/bin
rmdir %(install_root)s/Python24
''')

class Python_2_4__freebsd (Python_2_4):
    def configure (self):
        Python_2_4.configure (self)
        self.file_sub ([
                ('^CFLAGSFORSHARED=.*', 'CFLAGSFORSHARED = -fPIC'),
                ('^LDLIBRARY=.*', 'LDLIBRARY = libpython$(VERSION).so'),
                ('^INSTSONAME=.*', 'INSTSONAME = libpython$(VERSION).so.0.1'),
                ], '%(builddir)s/Makefile')

class Python_2_4__mingw (Python_2_4):
    patches = Python_2_4.patches + [
        'python-2.4.2-winsock2.patch',
        'python-2.4.2-setup.py-selectmodule.patch',
        'python-2.4.5-disable-pwd-mingw.patch',
        'python-2.4.5-mingw-site.patch',
        'python-2.4.5-mingw-socketmodule.patch',
        ]
    config_cache_overrides = (Python_2_4.config_cache_overrides
                              #FIXME: promoteme? see Gettext/Python
                              .replace ('ac_cv_func_select=yes',
                                        'ac_cv_func_select=no')
                              + '''
ac_cv_pthread_system_supported=yes,
ac_cv_sizeof_pthread_t=12
''')
    def __init__ (self, settings, source):
        Python_2_4.__init__ (self, settings, source)
        self.target_gcc_flags = '-DMS_WINDOWS -DMS_WIN32 -DPy_WIN_WIDE_FILENAMES -I%(system_prefix)s/include' % self.settings.__dict__
    dependencies = Python_2_4.dependencies + ['mingw-w64-runtime-winpthread-dll']
    # FIXME: first is cross compile + mingw patch, backported to
    # 2.4.2 and combined in one patch; move to cross-Python?
    def patch (self):
        Python_2_4.patch (self)
        self.file_sub ([
                ('(== "win32")', r'in ("win32", "mingw32")'),
                ], "%(srcdir)s/Lib/subprocess.py",
                       must_succeed=True)
    def configure (self):
        target.AutoBuild.configure (self)
        self.dump ('''
_subprocess ../PC/_subprocess.c
msvcrt ../PC/msvcrtmodule.c
''',
                   '%(builddir)s/Modules/Setup',
                   mode='a')
        # avoid re-running makesetup and overwriting Makefile
        self.system ('cd %(builddir)s && make Modules/config.c')
        if 0:
            self.file_sub ([
#                ('^LDSHARED=.*', 'LDSHARED = $(CC) -shared -fPIC'),
                ('^LIBC=.*', 'LIBC = -lpython%(python_version)s -lwsock32 -luuid -loleaut32 -lole32'),
#                 ('^EXT_LIBS=.*', 'EXT_LIBS = -lpython%(python_version)s -lwsock32 -luuid -loleaut32 -lole32'),
                ], '%(builddir)s/Makefile')
        self.dump ('''
EXT_LIBS = -lpython%(python_version)s -lwsock32 -luuid -loleaut32 -lole32
''',
                   '%(builddir)s/Makefile',
                   mode='a')
    def compile (self):
        self.system ('''
cd %(builddir)s && rm -f python.exe
''')
        Python_2_4.compile (self)
        self.system ('''
cd %(builddir)s && mv python.exe python-console.exe
cd %(builddir)s && make LINKFORSHARED='-mwindows'
cd %(builddir)s && mv python.exe python-windows.exe
cd %(builddir)s && cp -p python-console.exe python.exe
''')
    def install (self):
        Python_2_4.install (self)
        self.system ('''
cd %(builddir)s && cp -p python-windows.exe python-console.exe %(install_prefix)s/bin
''')
        self.file_sub ([('extra = ""', 'extra = "-L%(system_prefix)s/bin -L%(system_prefix)s/lib -lpython%(python_version)s -lpthread"')],
                       '%(install_prefix)s%(cross_dir)s/bin/python-config')

        def rename_so (logger, fname):
            dll = re.sub ('\.so*', '.dll', fname)
            loggedos.rename (logger, fname, dll)

        self.map_locate (rename_so,
                         self.expand ('%(install_prefix)s/lib/python%(python_version)s/lib-dynload'),
                                      '*.so*')
        ## UGH.
        self.system ('''
cp %(install_prefix)s/lib/python%(python_version)s/lib-dynload/* %(install_prefix)s/bin
''')
        self.system ('''
chmod 755 %(install_prefix)s/bin/*
''')
        # This builds and runs in wine, but produces DLLs that
        # do not load in Windows Vista
        if 0:
            self.generate_dll_a_and_la ('python%(python_version)s', '-lpthread')

class Python_2_4__linux__ppc (Python_2_4):
    pass

class Python_2_4__tools (tools.AutoBuild, Python_2_4):
    patches = [
#        'python-2.4.2-fno-stack-protector.patch',
        'python-2.4.5-readline.patch', # Stop python from reading ~/.inputrc
        'python-2.4.5-db4.7.patch',
        'python-2.4.5-regen.patch',
        'python-2.4.5-setup-cross.patch',
        ]
    dependencies = [
        'autoconf',
        'db', # _bsddb
        'libtool',
        ]
    force_autoupdate = True
    parallel_build_broken = True
    not_supported = ['nis', 'crypt']
    get_conflict_dict = Python_2_4.get_conflict_dict
    def patch (self):
        Python_2_4.patch (self)
    def configure (self):
        tools.AutoBuild.configure (self)
        self.file_sub ([
                ('^CCSHARED=.*', 'CCSHARED = -fPIC'),
                ('^LDSHARED=.*', 'LDSHARED = $(CC) -shared -fPIC'),
                ('BLDSHARED=.*', 'BLDSHARED = $(CC) -shared -fPIC -L. -lpython%(python_version)s'),
                ], '%(builddir)s/Makefile')
        # avoid re-running makesetup and overwriting Makefile
        self.system ('cd %(builddir)s && make Modules/config.c')
