from gub.specs.cross import gcc as cross_gcc
from gub import misc

class Gcc__freebsd (cross_gcc.Gcc):
    configure_flags = (cross_gcc.Gcc.configure_flags
                + misc.join_lines ('''
--program-prefix=%(toolchain_prefix)s
--disable-libcilkrts
--disable-__cxa_atexit
'''))
    configure_variables = (cross_gcc.Gcc.configure_variables 
                + misc.join_lines ('''
MAKEINFO=missing
'''))
