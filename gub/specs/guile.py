import os
#
from gub import misc
from gub import loggedos
from gub import octal
from gub import repository
from gub import target
from gub import tools

class Guile (target.AutoBuild):
    # http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=494337
    # source = 'git://git.sv.gnu.org/guile.git&branch=branch_release-1-8&revision=release_1-8-4'
    #source = 'git://git.sv.gnu.org/guile.git&branch=branch_release-1-8&revision=release_1-8-5'
    # 1.8.5 breaks with autoconf >= 2.62
    # source = 'git://git.sv.gnu.org/guile.git&branch=branch_release-1-8&revision=release_1-8-6'
    # 1.8.6's ./autogen.sh barfs
    # branch = 'branch_release-1-8'
    source = 'git://git.sv.gnu.org/guile.git&branch=branch_release-1-8&revision=bba579611b3671c7e4c1515b100f01c048a07935'
    patches = ['guile-reloc-1.8.6.patch',
               'guile-cexp.patch',
               'guile-1.8.6-test-use-srfi.patch']
    def __init__ (self, settings, source):
        target.AutoBuild.__init__ (self, settings, source)
        if isinstance (source, repository.Repository):
            source.version = lambda: '1.8.6'
        self.so_version = '17'
    def _get_build_dependencies (self):
        return ['gettext-devel', 'gmp-devel', 'libtool', 'tools::guile']
    def get_subpackage_names (self):
        return ['doc', 'devel', 'runtime', '']
    def patch (self):
        self.dump ('''#!/bin/sh
exec %(tools_prefix)s/bin/guile "$@"
''', "%(srcdir)s/pre-inst-guile.in")
        self.autogen_sh ()
        # Guile [doc] does not compile with dash *and* not with
        # librestrict-stat.so; patch out.
        target.AutoBuild.patch (self)
        if 'stat' in misc.librestrict ():
            self.file_sub ([(' doc ', ' ')], '%(srcdir)s/Makefile.am')
    def autogen_sh (self):
        self.file_sub ([(r'AC_CONFIG_SUBDIRS\(guile-readline\)', '')],
                       '%(srcdir)s/configure.in')
        self.file_sub ([(r'guile-readline', '')],
                       '%(srcdir)s/Makefile.am')
        self.dump ('', '%(srcdir)s/doc/ref/version.texi')
        self.dump ('', '%(srcdir)s/doc/tutorial/version.texi')
    def configure_flags (self):
        return misc.join_lines ('''
--without-threads
--with-gnu-ld
--enable-deprecated
--enable-discouraged
--disable-error-on-warning
--enable-relocation
--enable-rpath
''')
    def configure_variables (self):
        return misc.join_lines ('''
CC_FOR_BUILD="
C_INCLUDE_PATH=
CPPFLAGS=
LIBRARY_PATH=
PATH_SEPARATOR=':'
cc
-I%(builddir)s
-I%(srcdir)s
-I%(builddir)s/libguile
-I.
-I%(srcdir)s/libguile"
''')
    def configure_command (self):
        return ('GUILE_FOR_BUILD=%(tools_prefix)s/bin/guile '
                + 'LD_LIBRARY_PATH=%(system_prefix)s/lib:${LD_LIBRARY_PATH-/foe} '
                + target.AutoBuild.configure_command (self)
                + self.configure_flags ())
    def makeflags (self):
        return '''LDFLAGS='%(rpath)s' '''
    def compile_command (self):
        return ('preinstguile=%(tools_prefix)s/bin/guile ' +
                target.AutoBuild.compile_command (self))
    def compile (self):
        ## Ugh: broken dependencies break parallel build with make -jX
        self.system ('cd %(builddir)s/libguile && make gen-scmconfig guile_filter_doc_snarfage')
        # Remove -L %(system_root)s from `guile-config link'
        self.system ('cd %(builddir)s/libguile && make libpath.h')
        self.file_sub ([('''-L *%(system_root)s''', '-L')],
                       '%(builddir)s/libguile/libpath.h')
        target.AutoBuild.compile (self)
    def install (self):
        target.AutoBuild.install (self)
        majmin_version = '.'.join (self.expand ('%(version)s').split ('.')[0:2])
        
        self.dump ("prependdir GUILE_LOAD_PATH=$INSTALLER_PREFIX/share/guile/%(majmin_version)s\n",
                   '%(install_prefix)s/etc/relocate/guile.reloc',
                   env=locals ())
        version = self.expand ('%(version)s')
        #FIXME: c&p linux.py
        self.dump ('''\
#! /bin/sh
test "$1" = "--version" && echo "%(target_architecture)s-guile-config - Guile version %(version)s"
#test "$1" = "compile" && echo "-I $%(system_prefix)s/include"
#test "$1" = "link" && echo "-L%(system_prefix)s/lib -lguile -lgmp"
#prefix=$(dirname $(dirname $0))
prefix=%(system_prefix)s
test "$1" = "compile" && echo "-I$prefix/include"
test "$1" = "link" && echo "-L$prefix/lib -lguile -lgmp"
exit 0
''',
             '%(install_prefix)s%(cross_dir)s/bin/%(target_architecture)s-guile-config')
        self.chmod ('%(install_prefix)s%(cross_dir)s/bin/%(target_architecture)s-guile-config', octal.o755)

class Guile__mingw (Guile):
    def __init__ (self, settings, source):
        Guile.__init__ (self, settings, source)
        # Configure (compile) without -mwindows for console
        self.target_gcc_flags = '-mms-bitfields'
    def Xmakeflags (self):
        # hack for (only) running libtool under dash-librestrict.
        return (Guile.makeflags (self)
                + ''' 'LIBTOOL=%(tools_prefix)s/bin/dash $(top_builddir)/libtool' ''')
    def _get_build_dependencies (self):
        if 'stat' in misc.librestrict ():
            return (Guile._get_build_dependencies (self)
                    + ['tools::dash', 'tools::coreutils']
                    + ['regex-devel'])
        return Guile._get_build_dependencies (self) +  ['regex-devel']
    def configure_command (self):
        SHELL = ''
        if 'stat' in misc.librestrict ():
            SHELL = ' SHELL=%(tools_prefix)s/bin/dash'
        return (Guile.configure_command (self)
                + SHELL
                # + ' --with-threads=pthread'
                # checking whether pthread_attr_getstack works for the main thread... configure: error: cannot run test program while cross compiling
                # also, gen-scmconfig.c has
                #ifdef HAVE_STRUCT_TIMESPEC
                # pf ("typedef struct timespec scm_t_timespec;\n");
                # which breaks because __MINGW32__ needs #include <pthread.h>
                # So, for now:
                    + ' --without-threads'
                + Guile.configure_variables (self)
                # Use PATH_SEPARATOR=; or it will breaks tools
                # searching for the build platform.
                .replace (':', ';'))
                ###LDFLAGS=-L%(system_prefix)s/lib
    def config_cache_overrides (self, str):
        return str + '''
scm_cv_struct_timespec=${scm_cv_struct_timespec=no}
guile_cv_func_usleep_declared=${guile_cv_func_usleep_declared=yes}
guile_cv_exeext=${guile_cv_exeext=}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="%(system_prefix)s/lib"}
'''
    def configure (self):
        self.file_sub ([('''^#(LIBOBJS=".*fileblocks.*)''', r'\1')],
                       '%(srcdir)s/configure')
        Guile.configure (self)
        for libtool in ['%(builddir)s/libtool']: # readline patched-out: '%(builddir)s/guile-readline/libtool']:
            self.file_sub ([('-mwindows', '')], libtool)
    def compile (self):
        ## Why the !?#@$ is .EXE only for guile_filter_doc_snarfage?
        self.system ('''cd %(builddir)s/libguile && make CFLAGS='-DHAVE_CONFIG_H=1 -I%(builddir)s' gen-scmconfig guile_filter_doc_snarfage.exe''')
        self.system ('cd %(builddir)s/libguile && cp guile_filter_doc_snarfage.exe guile_filter_doc_snarfage')
        Guile.compile (self)
    def install (self):
        Guile.install (self)
        # dlopen-able .la files go in BIN dir, BIN OR LIB package
        self.system ('''mv %(install_prefix)s/lib/lib*[0-9].la %(install_prefix)s/bin''')

class Guile__linux (Guile):
    def compile_command (self):
        # FIXME: when not x-building, guile runs guile without
        # setting the proper LD_LIBRARY_PATH.
        return ('export LD_LIBRARY_PATH=%(builddir)s/libguile/.libs:$LD_LIBRARY_PATH;'
                + Guile.compile_command (self))

class Guile__linux__ppc (Guile__linux):
    def config_cache_overrides (self, str):
        return str + "\nguile_cv_have_libc_stack_end=no\n"

class Guile__freebsd (Guile):
    def config_cache_settings (self):
        return (Guile.config_cache_settings (self)
                + '''
ac_cv_type_socklen_t=yes
guile_cv_use_csqrt="no"
''')
    def configure_command (self):
        return (Guile.configure_command (self)
                + Guile.configure_flags (self)
                + Guile.configure_variables (self))

class Guile__darwin (Guile):
    def install (self):
        Guile.install (self)

        def dylib_link (logger, fname):
            directory = os.path.split (fname)[0]
            src = os.path.basename (fname)
            dst = os.path.splitext (os.path.basename (fname))[0] + '.so'
            loggedos.symlink (logger, src, os.path.join (directory, dst))
                              
        self.map_locate (dylib_link,
                         self.expand ('%(install_prefix)s/lib/'),
                         'libguile-srfi*.dylib')
 
class Guile__darwin__x86 (Guile__darwin):
    def configure (self):
        Guile__darwin.configure (self)
        self.file_sub ([('guile-readline', '')],
                       '%(builddir)s/Makefile')
        
class Guile__cygwin (Guile):
    def category_dict (self):
        return {'': 'Interpreters'}
    # Using gub dependencies only would be nice, but
    # we need to a lot of gup.gub_to_distro_deps ().
    def GUB_get_dependency_dict (self):
        d = Guile.get_dependency_dict (self)
        d['runtime'].append ('cygwin')
        return d
    # Using gub dependencies only would be nice, but
    # we need to a lot of gup.gub_to_distro_deps ().
    def GUB_get_build_dependencies (self):
        return Guile._get_build_dependencies (self) + ['libiconv-devel']
    # FIXME: uses mixed gub/distro dependencies
    def get_dependency_dict (self): #cygwin
        d = Guile.get_dependency_dict (self)
        d[''] += ['cygwin']
        d['devel'] += ['cygwin'] + ['bash']
        d['runtime'] += ['cygwin', 'crypt', 'libreadline6']
        return d
    # FIXME: uses mixed gub/distro dependencies
    def get_build_dependencies (self): # cygwin
        return ['crypt', 'libgmp-devel', 'gettext-devel', 'libiconv', 'libtool', 'readline']
    def config_cache_overrides (self, str):
        return str + '''
guile_cv_func_usleep_declared=${guile_cv_func_usleep_declared=yes}
guile_cv_exeext=${guile_cv_exeext=}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="%(system_prefix)s/lib"}
'''
    def configure (self):
        self.file_sub ([('''^#(LIBOBJS=".*fileblocks.*)''', r'\1')],
                       '%(srcdir)s/configure')
        Guile.configure (self)
        if 0:  # should be fixed in w32.py already
            self.file_sub ([
                    ('^(allow_undefined_flag=.*)unsupported', r'\1')],
                           '%(builddir)s/libtool')
            self.file_sub ([
                    ('^(allow_undefined_flag=.*)unsupported', r'\1')],
                           '%(builddir)s/guile-readline/libtool')
    # C&P from Guile__mingw
    def compile (self):
        ## Why the !?#@$ is .EXE only for guile_filter_doc_snarfage?
        self.system ('''cd %(builddir)s/libguile && make CFLAGS='-DHAVE_CONFIG_H=1 -I%(builddir)s' gen-scmconfig guile_filter_doc_snarfage.exe''')
        self.system ('cd %(builddir)s/libguile && cp guile_filter_doc_snarfage.exe guile_filter_doc_snarfage')
        Guile.compile (self)
    def description_dict (self):
        return {
            '': """The GNU extension language and Scheme interpreter - executables
Guile, the GNU Ubiquitous Intelligent Language for Extension, is a scheme
implementation designed for real world programming, supporting a
rich Unix interface, a module system, and undergoing rapid development.

`guile' is a scheme interpreter that can execute scheme scripts (with a
#! line at the top of the file), or run as an inferior scheme
process inside Emacs.
""",
            'runtime': '''The GNU extension language and Scheme interpreter - runtime
Guile shared object libraries and the ice-9 scheme module.  Guile is
the GNU Ubiquitous Intelligent Language for Extension.
''',
            'devel': """The GNU extension language and Scheme interpreter - development
`libguile.h' etc. C headers, aclocal macros, the `guile-snarf' and
`guile-config' utilities, and static `libguile.a' libraries for Guile,
the GNU Ubiquitous Intelligent Language for Extension.
""",
            'doc': """The GNU extension language and Scheme interpreter - documentation
This package contains the documentation for guile, including both
a reference manual (via `info guile'), and a tutorial (via `info
guile-tut').
""",
    }

class Guile__tools (tools.AutoBuild, Guile):
    def _get_build_dependencies (self):
        return (Guile._get_build_dependencies (self)
                + ['autoconf', 'automake', 'gettext', 'flex', 'libtool'])
    def patch (self):
        # Guile [doc] does not compile with dash *and* not with
        # librestrict-stat.so; patch out.
        tools.AutoBuild.patch (self)
        if 'stat' in misc.librestrict ():
            self.file_sub ([(' doc ', ' ')], '%(srcdir)s/Makefile.am')
    def configure_command (self):
        # FIXME: when configuring, guile runs binaries linked against
        # libltdl.
        return ('LD_LIBRARY_PATH=%(system_prefix)s/lib:${LD_LIBRARY_PATH-/foe} '
                + tools.AutoBuild.configure_command (self)
                + Guile.configure_flags (self))
    def compile_command (self):
        # FIXME: when not x-building, guile runs gen_scmconfig, guile without
        # setting the proper LD_LIBRARY_PATH.
        return ('export LD_LIBRARY_PATH=%(builddir)s/libguile/.libs:%(system_prefix)s/lib:${LD_LIBRARY_PATH-/foe};'
                + Guile.compile_command (self))
    def makeflags (self):
        return Guile.makeflags (self)
    def install (self):
        tools.AutoBuild.install (self)
        # Ugh: remove development stuff from tools
        # Make sure no tool GUILE headers can interfere with compile.
        self.system ("rm -rf %(install_root)s%(packaging_suffix_dir)s%(prefix_dir)s/include/ %(install_root)s%(packaging_suffix_dir)s%(prefix_dir)s/bin/guile-config ")
    def wrap_executables (self):
        # using rpath
        pass
