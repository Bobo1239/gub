#
from gub import context
from gub import misc
from gub import target
from gub.specs import lilypond

class LilyPond_doc (lilypond.LilyPond_base):
    dependencies = (lilypond.LilyPond_base.dependencies
                + [
                'tools::netpbm',
                'tools::imagemagick',
                'tools::rsync', # ugh, we depend on *rsync* !?
                #'tools::texlive',
                ])
    makeflags = misc.join_lines ('''
CROSS=no
DOCUMENTATION=yes
WEB_TARGETS="offline online"
TARGET_PYTHON=/usr/bin/python
''')
    @context.subst_method
    def build_number (self):
        print 'FIXME Buildnum'
        return '0'
    
    @context.subst_method
    def doc_ball (self):
        return '%(uploads)s/lilypond-%(version)s-HEAD.documentation.tar.bz2'
    @context.subst_method
    def web_ball (self):
        return '%(uploads)s/lilypond-%(version)s-HEAD.webdoc.tar.bz2'
    def compile_command (self):
        return (lilypond.LilyPond_base.compile_command (self)
                + ' top-doc all doc')

    def install_flags (self):
        return (self.makeflags
                + 'prefix= '
                + 'infodir=/share/info '
                + 'DESTDIR=%(install_root)s '
                + 'mandir=/share/man ')
    def install_command (self):
        return (lilypond.LilyPond_base.install_command (self)
                .replace (' install', ' install-doc install-help2man')
                + self.install_flags ())
    def install (self):
        target.AutoBuild.install (self) 
        self.system ('''
LD_PRELOAD= cp -f sourcefiles/dir %(install_root)s/share/info/dir
cd %(install_root)s/share/info && %(doc_relocation)s install-info --info-dir=. lilypond.info
LD_PRELOAD= tar -C %(install_root)s -cjf %(doc_ball)s .
LD_PRELOAD= tar --exclude '*.signature' -C %(builddir)s/out-www/online-root -cjf %(web_ball)s .
''')

Lilypond_doc = LilyPond_doc
