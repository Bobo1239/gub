from gub import misc
from gub import target
from gub import tools

class Freetype (target.AutoBuild):
    '''Software font engine
FreeType is a software font engine that is designed to be small,
efficient, highly customizable and portable while capable of producing
high-quality output (glyph images). It can be used in graphics
libraries, display servers, font conversion tools, text image generation
tools, and many other products as well.'''

    source = 'http://download.savannah.nongnu.org/releases/freetype/freetype-2.1.10.tar.gz&name=freetype'
    def __init__ (self, settings, source):
        target.AutoBuild.__init__ (self, settings, source)
        # Freetype stats /sbin, /usr/sbin and /hurd to determine if
        # build system is unix??
        # target.append_target_dict (self, {'LIBRESTRICT_ALLOW': '/sbin:/usr/sbin:/hurd'})
        if 'stat' in misc.librestrict ():
            target.add_target_dict (self, {'LIBRESTRICT_ALLOW': '/sbin:/usr/sbin:/hurd:${LIBRESTRICT_ALLOW-/foo}'})
    def license_files (self):
        return ['%(srcdir)s/docs/LICENSE.TXT']
    def _get_build_dependencies (self):
        return ['libtool-devel', 'zlib-devel', 'tools::autoconf']
    def get_subpackage_names (self):
        return ['devel', '']
    def configure (self):
#                self.autoupdate (autodir=os.path.join (self.srcdir (),
#                                                       'builds/unix'))
        self.system ('''
        rm -f %(srcdir)s/builds/unix/{unix-def.mk,unix-cc.mk,ftconfig.h,freetype-config,freetype2.pc,config.status,config.log}
''')
        target.AutoBuild.configure (self)
        self.file_sub ([('^LIBTOOL=.*', 'LIBTOOL=%(builddir)s/libtool --tag=CXX')], '%(builddir)s/Makefile')
    def munge_ft_config (self, file):
        self.file_sub ([('\nprefix=[^\n]+\n',
                         '\nlocal_prefix=yes\nprefix=%(system_prefix)s\n'),
                        ('\nhardcode_libdir_flag_spec=.*', '\nhardcode_libdir_flag_spec=')],
                       file, must_succeed=True)

    def install (self):
        target.AutoBuild.install (self)
        # FIXME: this is broken.  for a sane target development package,
        # we want /usr/bin/freetype-config must survive.
        # While cross building, we create an  <toolprefix>-freetype-config
        # and prefer that.
        self.system ('mkdir -p %(install_prefix)s%(cross_dir)s/bin/')
        self.system ('mv %(install_prefix)s/bin/freetype-config %(install_prefix)s%(cross_dir)s/bin/freetype-config')
        self.munge_ft_config ('%(install_prefix)s%(cross_dir)s/bin/freetype-config')

class Freetype__mingw (Freetype):
    def xxconfigure (self):
        Freetype.configure (self)
        self.dump ('''
# libtool will not build dll if -no-undefined flag is not present
LDFLAGS:=$(LDFLAGS) -no-undefined
''',
             '%(builddir)s/Makefile',
             mode='a')

class XFreetype__cygwin (Freetype):
    source = 'http://download.savannah.nongnu.org/releases/freetype/freetype-2.1.10.tar.gz&name=freetype'
    patches = ['freetype-libtool-no-version.patch']

    def __init__ (self, settings, source):
        Freetype.__init__ (self, settings, source)
        self.so_version = '6'

    def get_subpackage_definitions (self):
        d = dict (Freetype.get_subpackage_definitions (self))
        # urg, must remove usr/share. Because there is no doc package,
        # runtime iso '' otherwise gets all docs.
        d['runtime'] = [self.settings.prefix_dir + '/bin/*dll',
                        self.settings.prefix_dir + '/lib/*.la']
        return d

    def get_subpackage_names (self):
        #return ['devel', 'doc', '']
        return ['devel', 'runtime', '']

    def get_build_dependencies (self): #cygwin
        return ['libtool']
    
    def get_dependency_dict (self): #cygwin
        return {
            '': ['libfreetype26'],
            'devel': ['libfreetype26'],
            'runtime': ['zlib'],
            }

    def category_dict (self):
        return {'': 'Libs'}

    def configure_command (self):
        return (Freetype.configure_command (self)
                + ' --sysconfdir=/etc --localstatedir=/var')

    def install (self):
        target.AutoBuild.install (self)
        self.pre_install_smurf_exe ()

class Freetype__tools (tools.AutoBuild, Freetype):
    def _get_build_dependencies (self):
        return ['libtool']
    # FIXME, mi-urg?
    def license_files (self):
        return Freetype.license_files (self)
    def install (self):
        tools.AutoBuild.install (self)
        #self.munge_ft_config ('%(install_root)s/%(tools_prefix)s/bin/.freetype-config')
        self.munge_ft_config ('%(install_root)s/%(tools_prefix)s/bin/freetype-config')
