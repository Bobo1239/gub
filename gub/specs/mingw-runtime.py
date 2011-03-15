from gub import build

class Mingw_runtime (build.BinaryBuild, build.SdkBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/mingw/mingw-runtime-3.14.tar.gz&strip=0'
    def install (self):
        self.system ('''
mkdir -p %(install_prefix)s/share
cd %(srcdir)s && tar -C %(srcdir)s/ -cf - . | tar -C %(install_prefix)s -xf -
mkdir -p %(install_prefix)s/include/sys
#cp -p %(sourcefiledir)s/mingw-headers/wait.h %(install_prefix)s/include/sys
mv %(install_prefix)s/doc %(install_prefix)s/share
''', locals ())
