from gub import target
from gub import tools

class Pygtk (target.AutoBuild):
    source = 'http://ftp.gnome.org/pub/GNOME/sources/pygtk/2.16/pygtk-2.16.0.tar.gz'
    #source = 'http://ftp.gnome.org/pub/GNOME/sources/pygtk/2.17/pygtk-2.17.0.tar.gz'
    config_cache_overrides = target.AutoBuild.config_cache_overrides + '''
ac_cv_setwakeupfd_ok=yes
'''
    force_autoupdate = True
    def aclocal_path (self):
        return (target.AutoBuild.aclocal_path (self)
                + ['%(srcdir)s/m4', '%(srcdir)s'])
    python_version = tools.python_version
    configure_command = ('PYTHON_INCLUDES=-I%(system_prefix)s/include/python%(python_version)s '
                         + target.AutoBuild.configure_command)
    patches = [
        'pygtk-cross.patch',
        ]
    dependencies = [
        'python',
        'pygobject',
        'gtk+',
#        'glade',
        'libglade',
        'pycairo',
        ]

class Pygtk__mingw (Pygtk):
    patches = Pygtk.patches + [
        'pygtk-mingw.patch',
        ]
    config_cache_overrides = target.AutoBuild.config_cache_overrides + '''
ac_cv_setwakeupfd_ok=no
'''
    configure_variables = (Pygtk.configure_variables
                  + ' LDFLAGS="-L%(system_prefix)s/bin -lpython%(python_version)s"')
