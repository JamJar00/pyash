import os, glob

# Setting this true will ensure we don't overwrite any builtins like 'print' by appending 'pysh_'
BE_SAFE = False

def _execute(escaped_executable_path, args):
    return os.popen(escaped_executable_path + " " + " ".join(args)).read()

def _create_proxy_function(executable_path):
    escaped_executable_path = "\"" + executable_path.replace("\"","\\\"") + "\""
    
    return lambda *args, e=escaped_executable_path: _execute(e, args)

loaded = []
for path in os.environ["PATH"].split(";"):
    for executable_path in glob.glob(path + "\\*.exe"):
        name = os.path.splitext(os.path.basename(executable_path))[0]

        if (BE_SAFE and name in __builtins__.keys()):
            name = "pysh_" + name

        globals()[name] = _create_proxy_function(executable_path)
