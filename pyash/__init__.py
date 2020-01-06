import os, glob
from .lazy_invocation import LazyInvocation

# Setting this true will ensure we don't overwrite any builtins like 'print' by appending 'pyash_'
BE_SAFE = False

def _internal_print(output):
    """Prints stuff, because we've probably just overwritten 'print()'..."""
    __builtins__["print"](output)

def _lazy_invoke_executable(executable_path, args):
    """Executes the specified program with the given args with lazy evaluation."""
    return LazyInvocation(executable_path, args)

def _create_proxy_function(executable_path):
    """Creates a function that when run will execute the specified program with arguments passed in."""
    return lambda *args, e=executable_path: _lazy_invoke_executable(e, args)

if __name__ != "__main__":
    loaded = []
    for path in os.environ["PATH"].split(";"):
        for executable_path in glob.glob(path + "\\*.exe"):
            name = os.path.splitext(os.path.basename(executable_path))[0]

            if (BE_SAFE and name in __builtins__.keys()):
                name = "pyash_" + name

            escaped_executable_path = "\"" + executable_path.replace("\"","\\\"") + "\""

            globals()[name] = _create_proxy_function(escaped_executable_path)
