import os
#
from gub import cross
from gub import misc
from gub import tools

class Nsis (tools.SConsBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/nsis/nsis-2.45-src.tar.bz2'
    #source = ':pserver:anonymous@nsis.cvs.sourceforge.net:/cvsroot/nsis&module=NSIS&tag=HEAD'
    def __init__ (self, settings, source):
        tools.AutoBuild.__init__ (self, settings, source)
        if 'x86_64-linux' in self.settings.build_architecture:
            cross.change_target_package_x86 (self, self.add_mingw_env ())
    def add_mingw_env (self):
        # Do not use 'root', 'usr', 'cross', rather use from settings,
        # that enables changing system root, prefix, etc.
        mingw_dir = (self.settings.alltargetdir + '/mingw'
                     + self.settings.root_dir)
        mingw_bin = (mingw_dir
                     + self.settings.prefix_dir
                     + self.settings.cross_dir
                     + '/bin')
        tools_dir = (self.settings.alltargetdir + '/tools'
                     + self.settings.root_dir)
        tools_bin = (tools_dir
                     + self.settings.prefix_dir
                     + '/bin')
        return {'PATH': mingw_bin + ':' + tools_bin + ':' + os.environ['PATH'] }
    def _get_build_dependencies (self):
        lst = ['mingw::cross/gcc']
        if 'x86_64-linux' in self.settings.build_architecture:
            lst += ['linux-x86::glibc']
        return lst
    def patch (self):
        self.system ('mkdir -p %(allbuilddir)s', ignore_errors=True)
        self.system ('ln -s %(srcdir)s %(builddir)s')
        if 'x86_64-linux' in self.settings.build_architecture:
            self.file_sub ([('''^Export\('defenv'\)''', '''
import os
defenv['CC'] = os.environ['CC']
defenv['CXX'] = os.environ['CXX']
defenv['C_INCLUDE_PATH'] = ''
defenv['CPLUS_INCLUDE_PATH'] = ''
defenv['CFLAGS'] = ''
Export('defenv')
''')],
                       '%(srcdir)s/SConstruct')
    def compile_command (self):
        relax = ''
        if 'stat' in misc.librestrict ():
            relax = 'LIBRESTRICT_IGNORE=%(tools_prefix)s/bin/python '
        return (relax
                + tools.SConsBuild.compile_command (self)
                + misc.join_lines ('''
DEBUG=yes
NSIS_CONFIG_LOG=yes
SKIPUTILS="NSIS Menu"
'''))

    # this method is overwritten for x86-64_linux
    def build_environment (self):
        return self.add_mingw_env ()
    def compile (self):
        self.system ('cd %(builddir)s && %(compile_command)s',
                     self.build_environment ())
    def install (self):
        self.system ('cd %(builddir)s && %(install_command)s ',
                     self.build_environment ())
        self.system ('cp -p %(nsisdir)s/FontName.dll %(install_root)s%(system_prefix)s/share/nsis/Plugins')
