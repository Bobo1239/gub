from gub import build
from gub import context
from gub import misc
from gub import target

class Inkscape (target.AutoBuild):
    source = 'svn:https://inkscape.svn.sourceforge.net/svnroot/inkscape&module=inkscape&branch=trunk&revision=20605'
    branch = 'trunk'
    def __init__ (self, settings, source):
        target.AutoBuild.__init__ (self, settings, source)
        build.add_dict (self,
                        {'ACLOCAL_FLAGS': ' -I '.join ([''] + self.aclocal_path ()), })
        source.is_tracking = misc.bind_method (lambda x: True, source)
    def patch (self):
        target.AutoBuild.patch (self)
        self.file_sub ([('AC_PATH_PROG\(PKG_CONFIG,',
                         'AC_PATH_PROG(ARE_YOU_FREAKING_MAD__OVERRIDING_PKG_CONFIG,')],
                       '%(srcdir)s/configure.ac')
    def _get_build_dependencies (self):
        return [
            'tools::automake',
            'tools::gettext',
            'tools::intltool',
            'tools::pkg-config',
            'boost-devel',
            'glibmm-devel',
            'gtkmm-devel',
            'gtk+-devel',
            'gsl-devel',
            'lcms-devel',
            'poppler-devel',
            'popt-devel',
            'libgc-devel',
            'libpng-devel',
            'librsvg-devel',
            'libsig++-devel',
            'libxml2-devel',
            'libxslt-devel',
            ]
    def get_build_dependencies (self):
        return self._get_build_dependencies ()
    def get_dependency_dict (self):
        return {'': [x.replace ('-devel', '')
                     for x in self._get_build_dependencies ()
                     if 'tools::' not in x and 'cross/' not in x]
                + ['cross/gcc-c++-runtime']
                }
    def aclocal_path (self):
        return ['%(system_prefix)s/share/aclocal']
    def configure_command (self):
        return (target.AutoBuild.configure_command (self)
                + ' --enable-lcms'
#                + ' --disable-poppler-cairo'
                + ' --enable-binreloc=yes'
#                + ''' CXXFLAGS='-static-libgcc -lstdc++' '''
#                + ''' CXXLD='$(CC)' '''
                + ''' LDFLAGS='%(rpath)s' '''
                + ' CXXFLAGS=-fpermissive'
                )

class Inkscape__mingw (Inkscape):
    patches = ['inkscape-mingw-DATADIR.h.patch']
    def _get_build_dependencies (self):
        return [x for x in Inkscape._get_build_dependencies (self)
                if 'poppler' not in x]
    def configure_command (self):
        return (Inkscape.configure_command (self)
                + ' --disable-poppler-cairo')

''' poppler does not build for mingw
 i686-mingw32-g++ -mwindows -mms-bitfields -DHAVE_CONFIG_H -I. -I/home/janneke/vc/gub/target/mingw/src/poppler-0.10.3/poppler -I.. -I/home/janneke/vc/gub/target/mingw/src/poppler-0.10.3 -I/home/janneke/vc/gub/target/mingw/src/poppler-0.10.3/goo -I/home/janneke/vc/gub/target/mingw/root/usr/include/cairo -I/home/janneke/vc/gub/target/mingw/root/usr/include/libxml2 -I/home/janneke/vc/gub/target/mingw/root/usr/include/freetype2 -I/home/janneke/vc/gub/target/mingw/root/usr/include -Wall -Wno-write-strings -g -O2 -MT SplashOutputDev.lo -MD -MP -MF .deps/SplashOutputDev.Tpo -c /home/janneke/vc/gub/target/mingw/src/poppler-0.10.3/poppler/SplashOutputDev.cc  -DDLL_EXPORT -DPIC -o .libs/SplashOutputDev.o
In file included from /home/janneke/vc/gub/target/mingw/src/poppler-0.10.3/poppler/GlobalParams.h:35,
                 from /home/janneke/vc/gub/target/mingw/src/poppler-0.10.3/poppler/SplashOutputDev.cc:37:
/home/janneke/vc/gub/target/mingw/src/poppler-0.10.3/poppler/poppler-config.h:80:1: warning: "CDECL" redefined
In file included from /home/janneke/vc/gub/target/mingw/root/usr/include/windows.h:48,
                 from /home/janneke/vc/gub/target/mingw/src/poppler-0.10.3/goo/gfile.h:37,
                 from /home/janneke/vc/gub/target/mingw/src/poppler-0.10.3/poppler/SplashOutputDev.cc:36:
/home/janneke/vc/gub/target/mingw/root/usr/include/windef.h:111:1: warning: this is the location of the previous definition
/home/janneke/vc/gub/target/mingw/root/usr/include/jmorecfg.h:161: error: conflicting declaration 'typedef long int INT32'
/home/janneke/vc/gub/target/mingw/root/usr/include/basetsd.h:52: error: 'INT32' has a previous declaration as 'typedef int INT32'
/home/janneke/vc/gub/target/mingw/root/usr/include/jmorecfg.h:227: error: conflicting declaration 'typedef int boolean'
/home/janneke/vc/gub/target/mingw/root/usr/include/rpcndr.h:52: error: 'boolean' has a previous declaration as 'typedef unsigned char boolean'
'''

class Inkscape__freebsd (Inkscape):
    def configure_command (self):
        return (Inkscape.configure_command (self)
                + ' CFLAGS=-pthread'
                + ' CXXFLAGS="-fpermissive -pthread"')
    def get_dependency_dict (self):
        return {'': (Inkscape.get_dependency_dict (self)['']
                     + ['cross/gcc-runtime']) }

class Inkscape__freebsd__x86 (Inkscape__freebsd):
    patches = ['inkscape-isfinite.patch', 'inkscape-wstring.patch',
               #'inkscape-round.patch',
               'inkscape-round-2.patch',
               ]
    def patch (self):
        Inkscape__freebsd.patch (self)
        self.file_sub ([
                ('wchar_t', 'char'),
                ('WCHAR_T', 'CHAR'),
                ],
                       '%(srcdir)s/src/util/ucompose.hpp')
    def configure (self):
        Inkscape__freebsd.configure (self)
        self.file_sub ([
                ('(/[*] config.h.  Generated)', r'''
#ifndef C99_ROUND
#define C99_ROUND
#ifdef __cplusplus
extern "C" {
#endif
double floor (double);
int sscanf(const char *str, const char *format, ...);
#ifdef __cplusplus
}
#endif
static inline double
round (double x)
{
  return (floor (x - 0.5) + 1.0);
}
static inline long long
atoll (char const *s)
{
    long long _l = 0LL;
    sscanf(s, "%%lld", &_l);
    return _l;
}
#define fmin(x,y) (x<y? x : y)
#define fmax(x,y) (x>y? x : y)
#define INFINITY (__builtin_inff())
#endif /* C99_ROUND */
\1'''),],
                       '%(builddir)s/config.h')

class Inkscape__darwin (Inkscape):
    def _get_build_dependencies (self):
        return [x for x in Inkscape._get_build_dependencies (self)
                if x.replace ('-devel', '') not in [
                'libxml2', # Included in darwin-sdk, hmm?
                ]]
