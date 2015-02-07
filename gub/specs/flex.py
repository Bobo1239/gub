#
from gub import misc
from gub import target
from gub import tools

class Flex (target.AutoBuild):
    source = 'http://sourceforge.net/projects/flex/files/flex/flex-2.5.35/flex-2.5.35.tar.gz'
#    if 'stat' in misc.librestrict (): # too broken to fix
#        # configure [gettext, flex] blindly look for /USR/include/libi*
#        configure_variables = (target.configure_variables
#                               + ' --without-libiconv-prefix'
#                               + ' --without-libintl-prefix')
    def patch (self):
        target.AutoBuild.patch (self)
        self.file_sub ([('-I@includedir@', '')], '%(srcdir)s/Makefile.in')
    config_cache_overrides = target.AutoBuild.config_cache_overrides + '''
ac_cv_func_malloc_0_nonnull=yes
ac_cv_func_realloc_0_nonnull=yes
'''

class Flex__mingw (Flex):
    dependencies = ['regex']
    configure_variables = (Flex.configure_variables
                           + ' CPPFLAGS=-I%(srcdir)s'
                           + ' LIBS=-lregex')
    def patch (self):
        self.system ('''
mkdir -p %(srcdir)s/sys
LD_PRELOAD= cp %(sourcefiledir)s/mingw-headers/wait.h %(srcdir)s/sys
''')
        Flex.configure (self)

class Flex__darwin__ppc (Flex):
    patches = ['flex-2.5.35-iostream-inside-extern-c++.patch']

class Flex__tools (tools.AutoBuild):
    source = Flex.source
