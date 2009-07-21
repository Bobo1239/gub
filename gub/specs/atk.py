from gub import context
from gub import target

class Atk (target.AutoBuild):
    source = 'ftp://ftp.gnome.org/pub/GNOME/sources/atk/1.25/atk-1.25.2.tar.gz'
    def _get_build_dependencies (self):
        return ['tools::libtool', 'glib-devel']
    def configure_command (self):
        # FIXME: use cross_compiling=yes from gtk+.patch ()?
        # UGH. glib-2.0.m4's configure snippet compiles and runs a
        # program linked against glib; so it needs LD_LIBRARY_PATH (or
        # a configure-time-only -Wl,-rpath, -Wl,%(system_prefix)s/lib
        return (target.AutoBuild.configure_command (self)
                + ''' LDFLAGS='%(rpath)s -Wl,-rpath -Wl,%(system_prefix)s/lib' ''')

class Atk__mingw (Atk):
    def patch (self):
        self.file_sub ([('\$\(srcdir\)/atk.def', 'atk.def')], '%(srcdir)s/atk/Makefile.in', must_succeed=True)

class Atk__darwin (Atk):
    def configure_command (self):
        # no rpath on darwin
        return target.AutoBuild.configure_command (self)
