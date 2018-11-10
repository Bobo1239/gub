from gub import tools

class Zip__tools (tools.AutoBuild):
    source = 'ftp://ftp.info-zip.org/pub/infozip/src/zip30.tgz&version=3.0'
    srcdir_build_broken = True
#    configure_binary = '%(srcdir)s/unix/configure'
    def configure (self):
        self.shadow ()
#    compile_command = 'make -f unix/Makefile generic'
    make_flags = tools.AutoBuild.make_flags + '-f unix/Makefile generic'
    install_flags = tools.AutoBuild.install_flags + ' prefix=%(install_root)s%(system_prefix)s'
