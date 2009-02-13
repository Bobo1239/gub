import os
#
from gub import tools
from gub import target
from gub import w32

class Glib (target.AutoBuild):
    ## 2.12.4 : see bug  http://bugzilla.gnome.org/show_bug.cgi?id=362918
    source = 'http://ftp.gnome.org/pub/GNOME/platform/2.22/2.22.0/sources/glib-2.16.1.tar.bz2'
    source = 'http://ftp.gnome.org/pub/GNOME/platform/2.25/2.25.5/sources/glib-2.19.5.tar.gz'
    def _get_build_dependencies (self):
        if 'stat' in os.environ.get ('LIBRESTRICT', ''):
            return ['tools::glib', 'gettext-devel', 'libtool']
        return ['gettext-devel', 'libtool']
    def config_cache_overrides (self, str):
        return str + '''
glib_cv_stack_grows=${glib_cv_stack_grows=no}
'''
    def update_libtool (self): # linux-x86, linux-ppc, freebsd-x86
        target.AutoBuild.update_libtool (self)
        #URGME, 2.19.5: relinking libgio is broken, /usr/lib is inserted
        '''root/usr/lib/usr/lib -L/usr/lib -lgobject-2.0 -L/home/janneke/vc/gub/target/linux-ppc/install/glib-2.19.5-root/usr/lib/home/janneke/vc/gub/target/linux-ppc/build/glib-2.19.5/gmodule/.libs -lgmodule-2.0 -ldl -lglib-2.0    -Wl,-soname -Wl,libgio-2.0.so.0 -Wl,-version-script -Wl,.libs/libgio-2.0.ver -o .libs/libgio-2.0.so.0.1905.0
/home/janneke/vc/gub/target/linux-ppc/root/usr/cross/bin/powerpc-linux-ld: skipping incompatible /usr/lib/libgobject-2.0.so when searching for -lgobject-2.0
/home/janneke/vc/gub/target/linux-ppc/root/usr/cross/bin/powerpc-linux-ld: skipping incompatible /usr/lib/libgobject-2.0.a when searching for -lgobject-2.0
/home/janneke/vc/gub/target/linux-ppc/root/usr/cross/bin/powerpc-linux-ld: cannot find -lgobject-2.0
collect2: ld returned 1 exit status
libtool: install: error: relink `libgio-2.0.la' with the above command before installing it
make[5]: *** [install-libLTLIBRARIES] Error 1
'''
        self.map_locate (w32.libtool_disable_relink, '%(builddir)s', 'libtool')
    def install (self):
        target.AutoBuild.install (self)
        self.system ('rm %(install_prefix)s/lib/charset.alias',
                     ignore_errors=True)
        
class Glib__darwin (Glib):
    def configure (self):
        Glib.configure (self)
        self.file_sub ([('nmedit', '%(target_architecture)s-nmedit')],
                       '%(builddir)s/libtool')

class Glib__darwin__x86 (Glib__darwin):
    def compile (self):
        self.file_sub ([('(SUBDIRS = .*) tests', r'\1'),
                        (r'GTESTER = \$.*', ''),
                        ('(am__EXEEXT(_[0-9])? = )gtester.*', r'\1'),
                        ('(am__append(_[0-9])? = )gtester', r'\1')],
                       '%(builddir)s/glib/Makefile', must_succeed=True)
        Glib__darwin.compile (self)
        
class Glib__mingw (Glib):
    def _get_build_dependencies (self):
        return Glib._get_build_dependencies (self) + ['libiconv-devel']

class Glib__freebsd (Glib):
    def _get_build_dependencies (self):
        return Glib._get_build_dependencies (self) + ['libiconv-devel']
    def configure_command (self):
        return Glib.configure_command (self) + ' CFLAGS=-pthread'

class Glib__freebsd__x86 (Glib):
    def makeflags (self):
        # MUST include -pthread in lib flags, because our *most*
        # *beloved* libtool (2.2.6a) thinks it knows best and strips
        # -pthread if it thinks it's a compile flag.
        # FIXME: should add fixup to update_libtool ()
        return ' G_THREAD_LIBS=-pthread G_THREAD_LIBS_FOR_GTHREAD=-pthread '

class Glib__tools (tools.AutoBuild, Glib):
    def install (self):
        tools.AutoBuild.install (self)
        self.system ('rm %(install_root)s%(packaging_suffix_dir)s%(prefix_dir)s/lib/charset.alias',
                     ignore_errors=True)
    def _get_build_dependencies (self):
        return ['gettext', 'libtool']            
