import os
#
from gub import build
from gub import context
from gub import cross
from gub import cygwin
from gub import loggedos
from gub import misc
from gub.specs import gcc

class Gcc (cross.AutoBuild):
    source = 'http://ftp.gnu.org/pub/gnu/gcc/gcc-4.1.2/gcc-4.1.2.tar.bz2'
    def _get_build_dependencies (self):
        return ['cross/binutils']
    def patch (self):
        cross.AutoBuild.patch (self)
        gcc.do_not_look_in_slash_usr (self)
    @context.subst_method
    def NM_FOR_TARGET (self):
         return '%(toolchain_prefix)snm'
    def get_subpackage_names (self):
        # FIXME: why no -devel package?
        return ['doc', 'c++-runtime', 'runtime', '']
    def get_subpackage_definitions (self):
        d = cross.AutoBuild.get_subpackage_definitions (self)
        prefix_dir = self.settings.prefix_dir
        d['c++-runtime'] = [prefix_dir + '/lib/libstdc++.so*']
        return d
    def languages (self):
        return ['c', 'c++']
    def configure_command (self):
        # FIXME: using --prefix=%(tooldir)s makes this
        # uninstallable as a normal system package in
        # /usr/i686-mingw/
        # Probably --prefix=/usr is fine too
        enable_libstdcxx_debug = ''
        if 'c++' in self.languages ():
            enable_libstdcxx_debug = ' --enable-libstdcxx-debug'
        return (cross.AutoBuild.configure_command (self)
                + ' --enable-languages=' + ','.join (self.languages ())
# python2.5-ism
#                + ' --enable-libstdcxx-debug' if 'c++' in self.languages () else ''
                + enable_libstdcxx_debug
                + ' --enable-static'
                + ' --enable-shared'
                + ' --with-as=%(cross_prefix)s/bin/%(target_architecture)s-as'
                + ' --with-ld=%(cross_prefix)s/bin/%(target_architecture)s-ld'
                + ' --with-nm=%(cross_prefix)s/bin/%(target_architecture)s-nm'
                )
    def makeflags (self):
        return misc.join_lines ('''
tooldir='%(cross_prefix)s/%(target_architecture)s
gcc_tooldir='%(prefix_dir)s/%(target_architecture)s'
''')
    def FAILED_attempt_to_avoid_post_install_MOVE_TARGET_LIBS_makeflags (self):
        return misc.join_lines ('''
toolexeclibdir=%(system_prefix)s
GUB_FLAGS_TO_PASS='toolexeclibdir=$(toolexeclibdir)'
RECURSE_FLAGS_TO_PASS='$(BASE_FLAGS_TO_PASS) $(GUB_FLAGS_TO_PASS)'
FLAGS_TO_PASS='$(BASE_FLAGS_TO_PASS) $(EXTRA_HOST_FLAGS) $(GUB_FLAGS_TO_PASS)'
TARGET_FLAGS_TO_PASS='$(BASE_FLAGS_TO_PASS) $(EXTRA_TARGET_FLAGS) $(GUB_FLAGS_TO_PASS)'
''')
    def pre_install (self):
        cross.AutoBuild.pre_install (self)
        # Only id <PREFIX>/<TARGET-ARCH>/bin exists, gcc's install installs
        # the plain gcc drivers without <TOOLCHAIN-PREFIX>gcc
#        self.system ('mkdir -p %(install_root)s%(cross_prefix)s/%(target_architecture)s/bin')
        self.system ('mkdir -p %(install_root)s%(prefix_dir)s/%(target_architecture)s/bin')
    def install (self):
        cross.AutoBuild.install (self)
        gcc.move_target_libs (self, '%(install_prefix)s%(cross_dir)s/%(target_architecture)s')
        gcc.move_target_libs (self, '%(install_prefix)s%(cross_dir)s/lib')
        self.disable_libtool_la_files ('libstdc[+][+]')

class Gcc__from__source (Gcc):
    def _get_build_dependencies (self):
        return (Gcc._get_build_dependencies (self)
                + ['cross/gcc-core', 'glibc-core'])
    def get_conflict_dict (self):
        return {'': ['cross/gcc-core'], 'doc': ['cross/gcc-core'], 'runtime': ['cross/gcc-core']}
    #FIXME: merge all configure_command settings with Gcc
    def configure_command (self):
        return (Gcc.configure_command (self)
                + misc.join_lines ('''
--with-local-prefix=%(system_prefix)s
--disable-multilib
--disable-nls
--enable-threads=posix
--enable-__cxa_atexit
--enable-symvers=gnu
--enable-c99 
--enable-clocale=gnu 
--enable-long-long
'''))

Gcc__linux = Gcc__from__source

class Gcc__mingw (Gcc):
    source = 'ftp://ftp.gnu.org/pub/gnu/gcc/gcc-4.1.1/gcc-4.1.1.tar.bz2'
    def _get_build_dependencies (self):
        return (Gcc._get_build_dependencies (self)
                + ['mingw-runtime', 'w32api']
                + ['tools::libtool'])
    def patch (self):
        Gcc.patch (self)
        for f in ['%(srcdir)s/gcc/config/i386/mingw32.h',
                  '%(srcdir)s/gcc/config/i386/t-mingw32']:
            self.file_sub ([('/mingw/include','%(prefix_dir)s/include'),
                            ('/mingw/lib','%(prefix_dir)s/lib'),
                            ], f)
    def STATIC_GXX_WIP_REMOVE_THIS_PREFIX_configure (self):
        # leave this for now.
        # lots of undefined refs.
        # possibly try static libstc++ with gcc > 4.1.1
        '''.libs/bitmap_allocator.o: In function `__gthread_mutex_init_function':
/home/janneke/vc/gub/target/mingw/build/cross/gcc-4.1.1/i686-mingw32/libstdc++-v3/include/i686-mingw32/bits/gthr-default.h:463: undefined reference to `___gthr_win32_mutex_init_function'
.libs/bitmap_allocator.o: In function `_ZN9__gnu_cxx9free_list6_M_getEj':
/home/janneke/vc/gub/target/mingw/src/cross/gcc-4.1.1/libstdc++-v3/src/bitmap_allocator.cc:53: undefined reference to `__Unwind_SjLj_Register'

'''
        Gcc.configure (self)
        # Configure all subpackages, makes
        # w32.libtool_fix_allow_undefined to find all libtool files
        self.system ('cd %(builddir)s && make %(makeflags)s configure-host configure-target')
        # Must ONLY do target stuff, otherwise cross executables cannot find their libraries
        # self.map_locate (lambda logger,file: build.libtool_update (logger, self.expand ('%(tools_prefix)s/bin/libtool'), file), '%(builddir)s/', 'libtool')
        #self.map_locate (lambda logger, file: build.libtool_update (logger, self.expand ('%(tools_prefix)s/bin/libtool'), file), '%(builddir)s/i686-mingw32', 'libtool')
        vars = ['CC', 'CXX', 'LTCC', 'LD', 'sys_lib_search_path_spec', 'sys_lib_dlsearch_path_spec', 'predep_objects', 'postdep_objects', 'predeps', 'postdeps', 'old_striplib', 'striplib']
        self.map_locate (lambda logger, file: build.libtool_update_preserve_vars (logger, self.expand ('%(tools_prefix)s/bin/libtool'), vars, file), '%(builddir)s/i686-mingw32', 'libtool')
        self.map_locate (lambda logger, file: build.libtool_force_infer_tag (logger, 'CXX', file), '%(builddir)s/i686-mingw32', 'libtool')

# http://gcc.gnu.org/PR24196            
class this_works_but_has_string_exception_across_dll_bug_Gcc__cygwin (Gcc__mingw):
    def _get_build_dependencies (self):
        return (Gcc__mingw._get_build_dependencies (self)
                + ['cygwin', 'w32api-in-usr-lib'])
    def makeflags (self):
        return misc.join_lines ('''
tooldir="%(cross_prefix)s/%(target_architecture)s"
gcc_tooldir="%(cross_prefix)s/%(target_architecture)s"
''')
    def compile_command (self):
        return (Gcc__mingw.compile_command (self)
                + self.makeflags ())
    def configure_command (self):
        # We must use --with-newlib, otherwise configure fails:
        # No support for this host/target combination.
        # [configure-target-libstdc++-v3]
        return (Gcc__mingw.configure_command (self)
                + misc.join_lines ('''
--with-newlib
--enable-threads
'''))

# Cygwin sources Gcc
# Hmm, download is broken.  How is download of gcc-g++ supposed to work anyway?
# wget http://mirrors.kernel.org/sourceware/cygwin/release/gcc/gcc-core/gcc-core-3.4.4-3-src.tar.bz2 
# wget http://mirrors.kernel.org/sourceware/cygwin/release/gcc/gcc-g++/gcc-g++-3.4.4-3-src.tar.bz2

# Untar stage is gone, use plain gcc + cygwin patch
#class Gcc__cygwin (Gcc):
class Gcc__cygwin (Gcc):
    source = 'ftp://ftp.gnu.org/pub/gnu/gcc/gcc-3.4.4/gcc-3.4.4.tar.bz2'
    patches = ['gcc-3.4.4-cygwin-3.patch']
    def xuntar (self):
        ball = self.source._file_name ()
        cygwin.untar_cygwin_src_package_variant2 (self, ball.replace ('-core', '-g++'),
                                                  split=True)
        cygwin.untar_cygwin_src_package_variant2 (self, ball)
    def _get_build_dependencies (self):
        return (Gcc._get_build_dependencies (self)
#                + ['cygwin', 'w32api-in-usr-lib', 'cross/gcc-g++'])
                + ['cygwin', 'w32api-in-usr-lib'])
    def makeflags (self):
        return misc.join_lines ('''
tooldir="%(cross_prefix)s/%(target_architecture)s"
gcc_tooldir="%(cross_prefix)s/%(target_architecture)s"
''')
    def configure_command (self):
        # We must use --with-newlib, otherwise configure fails:
        # No support for this host/target combination.
        # [configure-target-libstdc++-v3]
        return (Gcc.configure_command (self)
                + misc.join_lines ('''
--with-newlib
--verbose
--enable-nls
--without-included-gettext
--enable-version-specific-runtime-libs
--without-x
--enable-libgcj
--with-system-zlib
--enable-interpreter
--disable-libgcj-debug
--enable-threads=posix
--disable-win32-registry
--enable-sjlj-exceptions
--enable-hash-synchronization
--enable-libstdcxx-debug
'''))
