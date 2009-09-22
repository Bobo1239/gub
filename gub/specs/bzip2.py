from gub import tools

class Bzip2__tools (tools.MakeBuild):
    source = 'http://www.bzip.org/1.0.5/bzip2-1.0.5.tar.gz'
    def compile_flags (self):
        return ' -f Makefile-libbz2_so'
    def compile_command (self):
        return tools.MakeBuild.compile_command (self) + self.compile_flags ()
    def install_command (self):
        return (tools.MakeBuild.install_command (self)
                + ' PREFIX=%(install_prefix)s')
    def install (self):
        tools.MakeBuild.install (self)
        self.system ('cp -pv %(builddir)s/libbz2.so* %(install_prefix)s/lib')
        # junk broken symlinks
        self.system ('cd %(install_prefix)s/bin && rm -f bzless bzfgrep bzegrep bzcmp')
