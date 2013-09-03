import os
#
from gub.specs.cross import gcc as cross_gcc
from gub import loggedos
from gub import cross
from gub import misc

class Gcc__darwin (cross_gcc.Gcc):
    dependencies = ['tools::gmp', 'tools::mpfr', 'tools::mpc', 'odcctools']
    patches = cross_gcc.Gcc.patches + [
        'gcc-4.8.2-darwin-fixinc.patch',
        'gcc-4.8.2-darwin-libgcc.patch',
    ]
    configure_flags = (cross_gcc.Gcc.configure_flags
                       + ' --disable-libcilkrts'
    )
    def languages (self):
        # objective-c is used for quartz's Carbon/Carbon.h in pango, gtk+
        return cross_gcc.Gcc.languages (self) + ['objc', 'obj-c++']
    def rewire_gcc_libs (self):
        # FIXME: why do we skip, please document?
        # I get
        '''
/home/janneke/vc/gub/target/darwin-x86/root/usr/cross/bin/i686-apple-darwin8-ld: warning can't open dynamic library: /home/janneke/vc/gub/target/darwin-x86/root/home/janneke/vc/gub/target/darwin-x86/root/usr/cross/i686-apple-darwin8/lib/libgcc_s.1.dylib referenced from: /home/janneke/vc/gub/target/darwin-x86/root/usr/lib/libstdc++.dylib (checking for undefined symbols may be affected) (No such file or directory, errno = 2)
'''
        # let's try adding libstdc++.dylib?, nah, let's not
        skip_libs = [
            'libgcc_s.10.',
            'libgcc_s_',
            'libgcc_ext.10.'
        ] #, 'libstdc++']

        def rewire_one (logger, file):
            found_skips = [s for s in skip_libs if file.find (s) >= 0]
            if found_skips:
                return
            id = loggedos.read_pipe (logger,
                                     self.expand ('%(toolchain_prefix)sotool -L %(file)s', 
                                                 locals ()),
                                     env=self.get_substitution_dict ()).split ()[1]
            id = os.path.split (id)[1]
            loggedos.system (logger, 
                             self.expand ('%(toolchain_prefix)sinstall_name_tool -id /usr/lib/%(id)s %(file)s',
                                          locals ()),
                             env=self.get_substitution_dict ())
        self.map_locate (rewire_one,
                         self.expand ('%(install_prefix)s/lib/'),
                         '*.dylib')
    def get_subpackage_definitions (self):
        d = cross.AutoBuild.get_subpackage_definitions (self)
        prefix_dir = self.settings.prefix_dir
        d['c++-runtime'] = [
            prefix_dir + '/lib/libstdc++.6.dylib',
            prefix_dir + '/lib/libgcc_s.1.dylib',
        ]
        return d
    def install (self):
        cross_gcc.Gcc.install (self)
        # conflicts with darwin-SDK
        self.system ('mv %(install_prefix)s/lib/libsupc++.a %(install_prefix)s/lib/libsupc++.a-')
        self.rewire_gcc_libs ()

class Gcc__darwin__ppc (Gcc__darwin):
    configure_flags = (Gcc__darwin.configure_flags
                       + ' --disable-libitm'
    )
