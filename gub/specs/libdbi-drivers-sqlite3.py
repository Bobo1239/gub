from gub import misc
from gub import target

class Libdbi_drivers_sqlite3 (target.AutoBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/libdbi-drivers/libdbi-drivers-0.8.2.tar.gz'
    dependencies = ['sqlite-devel', 'libdbi-devel', 'libtool']
    configure_flags = (target.AutoBuild.configure_flags
                + misc.join_lines ('''
--disable-docs
--with-dbi-incdir=%(system_prefix)s/include
--with-sqlite3
--with-sqlite3-libdir=%(system_prefix)s/include
--with-sqlite3-incdir=%(system_prefix)s/include
'''))

    def configure (self):
        self.system ('''
mkdir -p %(builddir)s/doc/include
cd %(builddir)s && touch doc/Makefile.in doc/include/Makefile.in
''')
        target.AutoBuild.configure (self)

    makeflags = ' doc_DATA= html_DATA='

    def compile_command (self):
        return (target.AutoBuild.compile_command (self)
                + self.makeflags)

    def install_command (self):
        return (target.AutoBuild.install_command (self)
                + self.makeflags)

class Libdbi_drivers_sqlite3__debian__arm (Libdbi_drivers_sqlite3):
    dependencies = ['sqlite3-dev', 'libdbi', 'libtool']

