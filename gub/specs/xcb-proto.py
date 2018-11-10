from gub import target

class Xcb_proto (target.AutoBuild):
    source = 'https://xcb.freedesktop.org/dist/xcb-proto-1.3.tar.gz'
    dependencies = [
        'tools::libtool',
        'tools::python',
        ]
    def patch (self):
        self.file_sub ([('2[.]5', '2.4')], '%(srcdir)s/configure.ac', must_succeed=True)
        self.file_sub ([('2[.]5', '2.4')], '%(srcdir)s/configure', must_succeed=True)
    #force_autoupdate = True
