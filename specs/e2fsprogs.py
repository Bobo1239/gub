import download
import targetpackage

class E2fsprogs (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_tarball (mirror=download.sf, version='1.38')
    def install_command (self):
        return (targetpackage.TargetBuildSpec.install_command (self)
                + ' install-libs')