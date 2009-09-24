from gub import build

class Root_image (build.NullBuild):
    source = 'url://host/root-image-1.0.tar.gz'
        busybox = [
            'dhcp',
            'psmisc',
            'tinylogin',
            ]
    dependencies = [
            'base-files',
            'base-passwd',
            'busybox',
            'dropbear',
            'sysvinit',
            ]
    def get_ipkg_dependencies (self):
        busybox = ['makedevs']
        return [
            'base-files',
            'base-passwd',
            'dev',
            'etc-rc',
            'etc-usr-share',
            'initscripts',
            'linux-hotplug',
            'module-init-tools-depmod',
            'modutils-depmod',
            'modutils-initscripts',
            'netbase',
            'nxpp-dvbh',
            'nxpp-esgplayer-autostart',
            'nxpp-pointercal',
            'nxpp-runme',
            'portmap',
            'setserial',
            'strace',
            'sysvinit-inittab',
            'tslib-conf',
            'update-rc.d',
            ]
    def get_subpackage_names (self):
        return ['']
    def install_ipkg (self, i):
        fakeroot_cache = self.builddir () + '/fakeroot.cache'
        self.fakeroot (self.expand (self.settings.fakeroot, locals ()))
        _v = '' # self.os_interface.verbose_flag ()
        def do_one (logger, fname):
            loggedos.system (logger, self.expand ('''
cd %(install_root)s && ar p %(fname)s data.tar.gz | tar%(_v)s -zxf -
''', locals ()))
        self.map_locate (do_one,
                         self.expand ('%(downloads)s/ipk/'),
                         i + '*.ipk')
        
    def install (self):
        build.NullBuild.install (self)
        for i in self.get_ipkg_dependencies ():
            self.install_ipkg (i)

class Root_image__linux__arm__vfp (Root_image):
    dependencies = (Root_image.dependencies
                + ['csl-toolchain-binary',
                   'phone'])
    
