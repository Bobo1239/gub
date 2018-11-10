from gub import target
from gub import tools

class Pypoppler (target.AutoBuild):
    # for poppler-glib 0.12
    # source = 'http://launchpad.net/poppler-python/trunk/development/+download/pypoppler-0.12.1.tar.gz'
    # "pycairo >= 1.8.4"
    # source = 'http://launchpad.net/poppler-python/trunk/development/+download/pypoppler-0.10.1.tar.gz'
    # poppler.c:1707: error: 'POPPLER_TYPE_ANNOT_TEXT_ICON' undeclared (first use in this function)
    source = 'http://launchpad.net/poppler-python/trunk/development/+download/pypoppler-0.8.0.tar.gz'
    patches = [
        # FIXME: AM_CHECK_PYTHON_HEADERS fixed, port fix to python.m4
        # and other py*py packages and upstream
        'pypoppler-cross.patch',
        ]
    dependencies = [
        'python',
        'poppler',
        ]
    force_autoupdate = True
    python_version = tools.python_version
    configure_command = ('PYTHON=%(tools_prefix)s/bin/python PYTHON_INCLUDES=-I%(system_prefix)s/include/python%(python_version)s '
                         + target.AutoBuild.configure_command)
    def autoupdate (self):
        self.file_sub ([(r'pkg-config ', r'$PKG_CONFIG ')], '%(srcdir)s/configure.ac')
        self.file_sub ([('glib/poppler.h', 'poppler.h')], '%(srcdir)s/poppler.override')
        self.file_sub ([('glib/poppler.h', 'poppler.h')], '%(srcdir)s/popplermodule.c')
        target.AutoBuild.autoupdate (self)
        # pkg-config is such a brilliant tool, why do these auto*
        # people break its cross compiling features?
        self.file_sub ([(r'(^\s*)PKG_CONFIG=', r'\1XPKG_CONFIG=')], '%(srcdir)s/configure')

class Pypoppler__mingw (Pypoppler):
    configure_variables = (Pypoppler.configure_variables
                  + ' LDFLAGS="-L%(system_prefix)s/bin -lpython%(python_version)s"')
