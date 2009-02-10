import os
import re
import optparse
#
from gub.syntax import printf
from gub import build
from gub import build_platform
from gub import context
from gub import misc
from gub import sources
from gub import loggedos
from gub import logging

platforms = {
    'debian': 'i686-linux',
    'debian-arm': 'arm-linux',
    'debian-mipsel': 'mipsel-linux',
    'debian-x86': 'i686-linux',
    'cygwin': 'i686-cygwin',
    'darwin-ppc': 'powerpc-apple-darwin7',
    'darwin-x86': 'i686-apple-darwin8',

    'freebsd4-x86': 'i686-freebsd4',
    'freebsd6-x86': 'i686-freebsd6',

    'freebsd-x86': 'i686-freebsd4',
    'freebsd-64': 'x86_64-freebsd6',

    'linux-arm': 'arm-linux',
    'linux-arm-softfloat': 'armv5te-softfloat-linux',
    'linux-arm-vfp': 'arm-linux',

    'linux-mipsel': 'mipsel-linux',

    'linux-x86': 'i686-linux',
    'linux-64': 'x86_64-linux',
    'linux-ppc': 'powerpc-linux',
    'tools': 'tools',
    'mingw': 'i686-mingw32',
}

distros = ('cygwin')

class UnknownPlatform (Exception):
    pass

def get_platform_from_dir (settings, dir):
    m = re.match ('.*?([^/]+)(' + settings.root_dir + ')?/*$', dir)
    if m:
        return m.group (1)
    return None

class Settings (context.Context):
    def __init__ (self, platform=None):
        context.Context.__init__ (self)

        # TODO: tools-prefix, target-prefix, cross-prefix?
        self.prefix_dir = '/usr'
        self.root_dir = '/root'
        self.cross_dir = '/cross'

        self.build_platform = build_platform.machine ().strip ()
        if not self.build_platform:
            build_platform.plain_machine ().strip ()
        self.build_architecture = platforms[self.build_platform]
        self.build_cpu = self.build_architecture.split ('-')[0]
        self.build_os = re.sub ('[-0-9].*', '', self.build_platform)
        self_build_bits = '32'
        if self.build_platform.endswith ('64'):
            self_build_bits = '64'
        
        if not platform:
            platform = self.build_platform
        self.target_platform = platform
        if self.target_platform not in list (platforms.keys ()):
            raise UnknownPlatform (self.target_platform)

        self.target_architecture = platforms[self.target_platform]
        self.target_os = re.sub ('[-0-9].*', '', self.target_platform)
        self.target_cpu = self.target_architecture.split ('-')[0]
        self_target_bits = '32'
        if self.target_platform.endswith ('64'):
            self_target_bits = '64'

        # Hmm
        self.platform = self.target_platform
        self.architecture = self.target_architecture
        self.cpu = self.target_cpu
        self.os = self.target_os
        self_bits = self_target_bits

        GUB_TOOLS_PREFIX = os.environ.get ('GUB_TOOLS_PREFIX')
        
        # config dirs

        if self.platform == 'tools' and GUB_TOOLS_PREFIX:
            self.prefix_dir = ''

        # gubdir is top of `installed' gub repository
        self.gubdir = os.path.abspath (os.path.dirname (os.path.dirname (__file__)))
        if not self.gubdir:
            self.gubdir = os.getcwd ()

        # workdir is top of writable build stuff
        self.workdir = os.getcwd ()
        
        # gubdir based: fixed repository layout
        self.patchdir = self.gubdir + '/patches'
        self.sourcefiledir = self.gubdir + '/sourcefiles'
        self.specdir = self.gubdir + '/gub/specs'
        self.nsisdir = self.gubdir + '/nsis'

        # workdir based; may be changed
        self.downloads = self.workdir + '/downloads'
        self.alltargetdir = self.workdir + '/target'
        self.targetdir = self.alltargetdir + '/' + self.platform
        self.logdir = self.targetdir + '/log'

        self.system_root = self.targetdir + self.root_dir
        if self.platform == 'tools' and GUB_TOOLS_PREFIX:
            self.system_root = GUB_TOOLS_PREFIX
        self.system_prefix = self.system_root + self.prefix_dir

        ## Patches are architecture dependent, 
        ## so to ensure reproducibility, we unpack for each
        ## architecture separately.
        self.allsrcdir = self.targetdir + '/src'
        self.allbuilddir = self.targetdir + '/build'
        self.statusdir = self.targetdir + '/status'
        self.packages = self.targetdir + '/packages'

        self.uploads = self.workdir + '/uploads'
        self.platform_uploads = self.uploads + '/' + self.platform

        # FIXME: rename to cross_root?
        ##self.cross_prefix = self.system_prefix + self.cross_dir
        self.cross_prefix = self.targetdir + self.root_dir + self.prefix_dir + self.cross_dir
        self.installdir = self.targetdir + '/install'
        self.tools_root = self.alltargetdir + '/tools' + self.root_dir
        self.tools_prefix = self.tools_root + self.prefix_dir
        if GUB_TOOLS_PREFIX:
            self.tools_root = GUB_TOOLS_PREFIX
            self.tools_prefix = GUB_TOOLS_PREFIX

        self.cross_packages = self.packages + self.cross_dir
        self.cross_allsrcdir = self.allsrcdir + self.cross_dir
        self.cross_statusdir = self.statusdir + self.cross_dir

        self.core_prefix = self.cross_prefix + '/core'
        # end config dirs

        self.target_gcc_flags = '' 
        if self.platform == 'darwin-ppc':
            self.target_gcc_flags = '-D__ppc__'
        elif self.platform == 'mingw':
            self.target_gcc_flags = '-mwindows -mms-bitfields'

        self.build_source = False #URGURGURGRGU
        self.is_distro = (self.platform in distros
                          or self.platform.startswith ('debian'))

        self.gtk_version = '2.8'
        self.toolchain_prefix = self.target_architecture + '-'
        
        if self.target_architecture.startswith ('x86_64'):
            self.package_arch = 'amd64'
            self.debian_branch = 'unstable'
        else:
            self.package_arch = re.sub ('-.*', '', self.target_architecture)
            self.package_arch = re.sub ('i[0-9]86', 'i386', self.package_arch)
            self.package_arch = re.sub ('arm.*', 'arm', self.package_arch)
#            self.package_arch = re.sub ('powerpc.*', 'ppc', self.package_arch)
            self.debian_branch = 'stable'
        
        self.keep_build = False
        self.use_tools = False

        self.fakeroot_cache = '' # %(builddir)s/fakeroot.save'
        self.fakeroot = 'fakeroot -i%(fakeroot_cache)s -s%(fakeroot_cache)s '
        self.create_dirs ()

        try:
            self.cpu_count_str = '%d' % os.sysconf ('SC_NPROCESSORS_ONLN')
        except ValueError:
            self.cpu_count_str = '1'

        self_build_hardware_bits = self_build_bits
        try:
            cpuinfo = open ('/proc/cpuinfo').read ()
            cpu_flags = re.search ('(?m)^flags\s+:(.*)',
                                   cpuinfo).group (1).split ()
            if 'lm' in cpu_flags:
                self_build_hardware_bits = '64'
        except:
            pass
        try:
            cpu = misc.read_pipe ('sysctl -b hw.machine', logger=logging.default_logger.harmless)
            if cpu in ('amd64', 'ia64'):
                self_build_hardware_bits = '64'
        except:
            pass

        if self_build_bits == '32' and self_build_hardware_bits == '64':
            # 32 bit OS running on 64 bit hardware, help configure
            self.ABI = self_target_bits
            os.environ['ABI'] = self_target_bits

        ## make sure we don't confuse build or target system.
        self.LD_LIBRARY_PATH = '%(system_root)s'
        
    def create_dirs (self): 
        for a in (
            'allsrcdir',
            'core_prefix',
            'cross_prefix',
            'downloads',
            'gubdir',
            'tools_prefix',
            'logdir',
            'packages',
            'specdir',
            'statusdir',
            'system_root',
            'targetdir',
            'uploads',

            'cross_packages',
            'cross_statusdir',
            'cross_allsrcdir',
            ):
            dir = self.__dict__[a]
            if not os.path.isdir (dir):
                loggedos.makedirs (logging.default_logger, dir)
        
    def dependency_url (self, string):
        # FIXME: read from settings.rc, take platform into account
        name = string.replace ('-', '_')
        return misc.most_significant_in_dict (sources.__dict__, name, '__')

def get_cli_parser ():
    p = optparse.OptionParser ()

    p.usage = '''settings.py [OPTION]...

Print settings and directory layout.

'''
    p.description = 'Grand Unified Builder.  Settings and directory layout.'

    # c&p #10?
    #import gub_options
    #gub_options.add_common_options (platform,branch,verbose)?
    p.add_option ('-p', '--platform', action='store',
                  dest='platform',
                  type='choice',
                  default=None,
                  help='select target platform',
                  choices=list (platforms.keys ()))
    p.add_option ('-B', '--branch', action='append',
                  dest='branches',
                  default=[],
                  metavar='NAME=BRANCH',
                  help='select branch')
    return p

def as_variables (settings):
    lst = []
    for k in list (settings.__dict__.keys ()):
        v = settings.__dict__[k]
        if type (v) == type (str ()):
            lst.append ('%(k)s=%(v)s' % locals ())
    return lst
    
def clean_environment ():
    return dict ([(x, os.environ[x]) for x in 
                  ('EMAIL',
                   'GUB_TOOLS_PREFIX',
                   'HOME',
                   'HOSTNAME',
                   #'IFS',
                   'PATH',
                   'PKG_CONFIG_PATH',
                   'PWD',
                   'SHELL',
                   'UID',
                   'USER',
                   'USERNAME',)
                  if os.environ.get (x) != None])

def main ():
    cli_parser = get_cli_parser ()
    (options, files) = cli_parser.parse_args ()
    if not options.platform or files:
        raise Exception ('barf')
        sys.exit (2)
    settings = Settings (options.platform)
    printf ('\n'.join (as_variables (settings)))

if __name__ == '__main__':
    main ()
