import download
import targetpackage

class Zlib (targetpackage.Target_package):
    def __init__ (self, settings):
        targetpackage.Target_package.__init__ (self, settings)
	self.with (version='1.2.2',
                   mirror='http://heanet.dl.sourceforge.net/sourceforge/libpng/zlib-1.2.2.tar.gz')
        
    def patch (self):
        targetpackage.Target_package.patch (self)
        self.system ('cd %(srcdir)s && patch -p1 < %(patchdir)s/zlib-1.2.2-windows.patch')
        self.file_sub ([("='/bin/true'", "='true'"),
                        ('mgwz','libz'),
                        ],
                       '%(srcdir)s/configure')
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')

    def compile_command (self):
        return targetpackage.Target_package.compile_command (self) + ' ARFLAGS=r '
    
    def configure_command (self):
        zlib_is_broken = 'SHAREDTARGET=libz.so.1.2.2'

        ### UGH.
        if self.settings.platform.startswith ('mingw'):
            zlib_is_broken = 'target=mingw'

        ## doesn't use autoconf configure.
        return zlib_is_broken + ' %(srcdir)s/configure --shared '

    def install_command (self):
        return targetpackage.Target_package.broken_install_command (self)


