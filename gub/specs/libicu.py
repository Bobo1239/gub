from gub import context
from gub import loggedos
from gub import misc
from gub import octal
from gub import target
from gub import tools

class Libicu (target.AutoBuild):
    source = 'http://download.icu-project.org/files/icu4c/3.8.1/icu4c-3_8_1-src.tgz'
    #http://download.icu-project.org/files/icu4c/4.0/icu4c-4_0-src.tgz
    patches = ['libicu-3.8.1-cross.patch']
    def __init__ (self, settings, source):
        target.AutoBuild.__init__ (self, settings, source)
        source._version = '3.8.1'
    def stages (self):
        return misc.list_insert_before (target.AutoBuild.stages (self),
                                        'configure',
                                        ['configure_native', 'compile_native'])
#    def autodir (self):
#        return '%(srcdir)s/source'
    def makeflags (self):
        return misc.join_lines ('''
BINDIR_FOR_BUILD='$(BINDIR)-native'
LIBDIR_FOR_BUILD='$(LIBDIR)-native'
PKGDATA_INVOKE_OPTS="TARGET='lib\$\$(LIBNAME).so' BINDIR_FOR_BUILD='\$\$(BINDIR)-native' LIBDIR_FOR_BUILD='\$\$(LIBDIR)-native'"
''')
    @context.subst_method
    def makeflags_native (self):
        return misc.join_lines ('''
BINDIR='$(top_builddir)/bin-native'
LIBDIR='$(top_builddir)/lib-native'
PKGDATA_INVOKE_OPTS="BINDIR='\$\$(top_builddir)/bin-native' LIBDIR='\$\$(top_builddir)/lib-native'"
''')
    def compile_native (self):
        target.AutoBuild.compile_native (self)
        def rm (logger, file):
            loggedos.system (logger, 'rm -f %(file)s' % locals ())
        # ugh, should add misc.find () as map_find () to context interface
        # self.map_locate (rm, '%(builddir)s', '*.so.*')
        # self.map_locate (rm, '%(builddir)s', '*.so')
        self.map_locate (rm, '%(builddir)s', '*.o')
        self.get_substitution_dict = misc.bind_method (target.AutoBuild.get_substitution_dict, self)

class Libicu__mingw (Libicu):
    patches = Libicu.patches + ['libicu-3.8.1-uintptr-t.patch', 'libicu-3.8.1-cross-mingw.patch', 'libicu-3.8.1-mingw.patch']
    configure_flags = (Libicu.configure_flags
                + misc.join_lines ('''
--disable-threads
'''))
    def configure (self):
        Libicu.configure (self)
        self.dump ('''
#define S_IROTH S_IREAD
#define S_IXOTH S_IXUSR
''',
                   '%(builddir)s/common/unicode/platform.h', mode='a')
    def compile_native (self):
        Libicu.compile_native (self)
        self.system ('cd %(builddir)s/bin-native && mv pkgdata pkgdata.bin')
        self.dump ('''\
#! /bin/sh
dir=$(dirname $0)
if test "$dir" = "."; then
   dir=$(dirname $(which $0))
fi
$dir/$(basename $0).bin "$@" | sed -e 's/lib$(LIBNAME).so/$(LIBNAME).dll/g'
''',
             '%(builddir)s/bin-native/pkgdata',
                   permissions=octal.o755)

class Libicu__tools (tools.AutoBuild, Libicu):
    source = 'http://download.icu-project.org/files/icu4c/4.1/icu4c-4_1_3-src.tgz'
    #source = 'http://download.icu-project.org/files/icu4c/4.0/icu4c-4_0-src.tgz'
    patches = []
    def __init__ (self, settings, source):
        target.AutoBuild.__init__ (self, settings, source)
        source._version = '4.1.3'
        #source._version = '4.0'
    def stages (self):
        return tools.AutoBuild.stages (self)
