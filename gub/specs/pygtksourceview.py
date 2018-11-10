from gub import misc
from gub import target
from gub import tools

class Pygtksourceview (target.AutoBuild):
    source = 'http://ftp.gnome.org/pub/gnome/sources/pygtksourceview/2.10/pygtksourceview-2.10.1.tar.gz'
    python_version = tools.python_version
    configure_command = (misc.join_lines ('''
PYTHON=%(tools_prefix)s/bin/python
PYTHON_HOME=%(system_prefix)s
PYTHON_VERSION=%(python_version)s
PYTHON_GTK_DIR=%(system_prefix)s/lib/python%(python_version)s/site-packages
PYTHON_INCLUDES=-I%(system_prefix)s/include/python%(python_version)s
PYTHON_LIBS="-L%(system_prefix)s/bin -lpython%(python_version)s"
PYTHON_PKG_DIR=%(prefix_dir)s/lib/python%(python_version)s/site-packages
''')
                         + target.AutoBuild.configure_command)
    dependencies = [
        'gtksourceview',
        'pygtk',
        ]
