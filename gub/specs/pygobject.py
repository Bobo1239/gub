from gub import target
from gub import tools

class Pygobject (target.AutoBuild):
    source = 'http://ftp.gnome.org/pub/GNOME/sources/pygobject/2.16/pygobject-2.16.1.tar.gz'
    #source = 'http://ftp.gnome.org/pub/GNOME/sources/pygobject/2.21/pygobject-2.21.5.tar.gz'
    force_autoupdate = True
    config_cache_overrides = target.AutoBuild.config_cache_overrides + '''
ac_cv_setwakeupfd_ok=yes
'''
    def aclocal_path (self):
        return (target.AutoBuild.aclocal_path (self)
                + ['%(srcdir)s/m4', '%(srcdir)s'])
    python_version = tools.python_version
    configure_command = ('PYTHON=%(tools_prefix)s/bin/python PYTHON_INCLUDES=-I%(system_prefix)s/include/python%(python_version)s '
                         + target.AutoBuild.configure_command)
    patches = [
        'pygobject-cross.patch',
        ]
    dependencies = [
        'python',
        'glib',
        ]
    def compile (self):
        cflags = '-std=c9x'
        if self.settings.target_bits == '32':
            cflags += ' -m32'
        self.system ('''cd %(builddir)s/gobject && make generate_constants_LINK='gcc -o$@ %(cflags)s' CC=gcc CFLAGS="%(cflags)s" constants.py''', env=locals ())
        target.AutoBuild.compile (self)

class Pygobject__mingw (Pygobject):
    patches = Pygobject.patches + [
        'pygobject-mingw.patch',
        ]
    configure_variables = (Pygobject.configure_variables
                  + ' LDFLAGS="-L%(system_prefix)s/bin -lpython%(python_version)s"')
    config_cache_overrides = target.AutoBuild.config_cache_overrides + '''
ac_cv_setwakeupfd_ok=no
'''
    def patch (self):
        self.file_sub ([('have_giounix=true', 'have_giounix=false')], '%(srcdir)s/configure.ac', must_succeed=True)
        Pygobject.patch (self)
