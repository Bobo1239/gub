from gub import target

class Gtksourceview (target.AutoBuild):
    source = 'http://ftp.gnome.org/pub/gnome/sources/gtksourceview/2.11/gtksourceview-2.11.2.tar.gz'
    dependencies = [
        'gtk+-devel',
        ]
