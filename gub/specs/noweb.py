from gub import target

class Noweb (target.AutoBuild):
    '''A WEB-like literate-programming tool
Noweb is designed to meet the needs of literate programmers while
remaining as simple as possible.  Its primary advantages are
simplicity, extensibility, and language-independence.
'''
    source = 'http://www.eecs.harvard.edu/~nr/noweb/dist/noweb-2.11b.tgz'
    def __init__ (self, settings, source):
        target.TarBall.__init__ (self, settings, source)
        self.BIN='%(install_prefix)s/bin'
        self.LIB='%(install_prefix)s/lib'
        self.MAN='%(install_prefix)s/share/man'
        self.TEXINPUTS='%(install_prefix)s/share/tex/inputs'
    def category_dict (self):
        return {'': 'Text Science'}
    make_flags = 'BIN=%(install_prefix)s/bin LIB=%(install_prefix)s/lib MAN=%(install_prefix)s/share/man TEXINPUTS=%(install_prefix)s/share/tex/inputs'
    def configure (self):
        self.shadow_tree ('%(srcdir)s/src', '%(builddir)s')
    def get_subpackage_names (self):
        return ['']
    def install_command (self):
        from gub import misc
        return misc.join_lines ('''
mkdir -p %(install_prefix)s/bin %(install_prefix)s/lib %(install_prefix)s/share/man/man1 %(install_prefix)s/share/tex/inputs
&& make %(compile_flags)s DESTDIR=%(install_root)s install
''')
    def license_files (self):
        return ['%(srcdir)s/src/COPYRIGHT']
