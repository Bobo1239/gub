from gub import build
from gub import commands
from gub import misc
from gub import tools

class Jade__tools (tools.AutoBuild):
    source = 'ftp://ftp.jclark.com/pub/jade/jade-1.2.1.tar.gz'
    srcdir_build_broken = True
    dependencies = ['tools::autoconf', 'tools::libtool']
    def autoupdate (self):
        self.system ('cd %(srcdir)s && cp -f config/configure.in .')
        self.system ('cd %(srcdir)s && libtoolize --force --copy || :')
        self.runner._execute (commands.ForcedAutogenMagic (self))
    def configure_command (self):
        return (build.AutoBuild.configure_command (self)
                + misc.join_lines ('''
CFLAGS=-I%(system_prefix)s/include
LDFLAGS=-L%(system_prefix)s/lib
LD_LIBRARY_PATH=%(system_prefix)s/lib
'''))
    def configure_binary (self):
        return '%(builddir)s/configure'
    def configure (self):
        tools.AutoBuild.configure (self)
        self.system ('cd %(builddir)s; for i in $(ls -1dF * |grep /); do make -C $i -f ../Makefile.lib Makefile.lt; done || :')
    def makeflags (self):
        return 'top_builddir=%(builddir)s'
