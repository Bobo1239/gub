from gub import misc
from gub import tools

python = misc.load_spec ('python-' + tools.python_version)

def get_conflict_dict (self):
    return {
        '': ['python-2.6', 'python-2.4'],
        'doc': ['python-2.6-doc', 'python-2.4-doc'],
        'devel': ['python-2.6-devel', 'python-2.4-devel'],
        'runtime': ['python-2.6-runtime', 'python-2.4-runtime'],
        }

def unver (dependencies):
    return [x.replace ('python-' + tools.python_version, 'python')
            for x in dependencies]

if tools.python_version == '2.4':
    class Python (python.Python_2_4):
        get_conflict_dict = get_conflict_dict
        dependencies = unver (python.Python_2_4.dependencies)
    class Python__mingw (python.Python_2_4__mingw):
        get_conflict_dict = get_conflict_dict
        dependencies = unver (python.Python_2_4__mingw.dependencies)
    class Python__linux__ppc (python.Python_2_4__linux__ppc):
        get_conflict_dict = get_conflict_dict
        dependencies = unver (python.Python_2_4__linux__ppc.dependencies)
    class Python__freebsd (python.Python_2_4__freebsd):
        get_conflict_dict = get_conflict_dict
        dependencies = unver (python.Python_2_4__freebsd.dependencies)
    class Python__tools (python.Python_2_4__tools):
        get_conflict_dict = get_conflict_dict
        dependencies = unver (python.Python_2_4__tools.dependencies)
elif tools.python_version == '2.6':
    class Python (python.Python_2_6):
        get_conflict_dict = get_conflict_dict
        dependencies = unver (python.Python_2_6.dependencies)
    class Python__mingw (python.Python_2_6__mingw):
        get_conflict_dict = get_conflict_dict
        dependencies = unver (python.Python_2_6__mingw.dependencies)
    class Python__linux__ppc (python.Python_2_6__linux__ppc):
        get_conflict_dict = get_conflict_dict
        dependencies = unver (python.Python_2_6__linux__ppc.dependencies)
    class Python__freebsd (python.Python_2_6__freebsd):
        get_conflict_dict = get_conflict_dict
        dependencies = unver (python.Python_2_6__freebsd.dependencies)
    class Python__tools (python.Python_2_6__tools):
        get_conflict_dict = get_conflict_dict
        dependencies = unver (python.Python_2_6__tools.dependencies)
else:
    raise Exception ('No such Python version:' + tools.python_version)
