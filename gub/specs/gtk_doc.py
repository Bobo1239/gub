from gub import tools

class Gtk_doc__tools (tools.AutoBuild):
    source = 'ftp://ftp.gtk.org/pub/gtk-doc/gtk-doc-1.1.tar.gz'
        # Ugh, ugh: avoid [zlib: gzopen64] trouble
    dependencies = ['libxml2']
