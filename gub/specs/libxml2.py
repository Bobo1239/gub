from gub import context
from gub import gnome
from gub import misc
from gub import target
from gub import tools

class Libxml2 (target.AutoBuild):
    source = 'http://ftp.gnome.org/pub/GNOME/platform/2.18/2.18.1/sources/libxml2-2.6.27.tar.gz'
    dependencies = ['zlib']
    configure_flags = (target.AutoBuild.configure_flags
                + misc.join_lines ('''
--without-python
'''))
    @context.subst_method
    def config_script (self):
        return 'xml2-config'

class Libxml2__mingw (Libxml2):
    configure_flags = (Libxml2.configure_flags
                + misc.join_lines ('''
--without-threads
'''))
    # Hmm, should rename sys/mman.h to sys/mingw-mman.h?
    config_cache_overrides = (Libxml2.config_cache_overrides
                              + '''
ac_cv_header_sys_mman_h=${ac_cv_header_sys_mman_h=no}
''')

    def install (self):
        Libxml2.install (self)
        self.copy ('%(install_prefix)s/lib/libxml2.la', '%(install_prefix)s/lib/libxml2-2.la')
        self.copy ('%(install_prefix)s/lib/libxml2.dll.a', '%(install_prefix)s/lib/libxml2-2.dll.a')

class Libxml2__tools (tools.AutoBuild, Libxml2):
    dependencies = Libxml2.dependencies + ['libtool']
    configure_flags = (tools.AutoBuild.configure_flags
                + misc.join_lines ('''
--without-python
'''))
