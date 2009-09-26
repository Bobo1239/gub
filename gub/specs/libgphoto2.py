from gub import octal
from gub import target


sf = 'http://surfnet.dl.sourceforge.net/sourceforge/%(name)s/%(name)s-%(ball_version)s.tar.%(format)s'
sf_gphoto = 'http://surfnet.dl.sourceforge.net/sourceforge/gphoto/%(name)s-%(ball_version)s.tar.%(format)s'

class Libgphoto2 (target.AutoBuild):
# -lltdl build problem
#    source = mirrors.with_template (name='libgphoto2', version='2.3.0', mirror=sf_gphoto)
# needs libexif >= 0.6.13, which we currently cannot compile/install
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/gphoto/libgphoto2-2.3.1.tar.gz'
# Does not compile
#    source = mirrors.with_template (name='libgphoto2', version='2.1.6', mirror=sf_gphoto)
    dependencies = ['libexif-devel', 'libjpeg-devel', 'libusb-devel']
    def wrap_pkg_config (self):
        self.dump ('''#! /bin/sh
/usr/bin/pkg-config\
  --define-variable prefix=%(system_prefix)s\
  --define-variable includedir=%(system_prefix)s/include\
  --define-variable libdir=%(system_prefix)s/lib\
  "$@"
''',
                   '%(srcdir)s/pkg-config')
        self.chmod ('%(srcdir)s/pkg-config', octal.o755)
    def wrap_libusb_config (self):
        self.dump ('''#! /bin/sh
/usr/bin/libusb-config\
  --prefix=%(system_prefix)s\
  "$@"
''',
                   '%(srcdir)s/libusb-config')
        self.chmod ('%(srcdir)s/libusb-config', octal.o755)
    def patch (self):
        self.wrap_pkg_config ()
        self.wrap_libusb_config ()
    configure_command = ('PATH=%(srcdir)s:$PATH '
                + target.AutoBuild.configure_command)
    make_flags = """ libgphoto2_port_la_DEPENDENCIES='$(top_srcdir)/gphoto2/gphoto2-port-version.h $(top_srcdir)/gphoto2/gphoto2-port-library.h $(srcdir)/libgphoto2_port.sym' libgphoto2_la_DEPENDENCIES='$(top_srcdir)/gphoto2/gphoto2-version.h $(srcdir)/libgphoto2.sym'"""

