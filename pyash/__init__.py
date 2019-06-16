import os, glob, subprocess, sys

# Setting this true will ensure we don't overwrite any builtins like 'print' by appending 'pyash_'
BE_SAFE = False

class LazyInvocation():
    """Class returned when a shell application is 'run'. This allows us to do piping etc. through lazy execution of the program."""
    def __init__(self, executable_path, args):
        self._executable_path = executable_path
        self._args = args

        # These will get setup on the fly
        self._stdin = None
        self._stdout = None
        self._process = None
        self._previous = None

    def __str__(self):
        """Returns the application's output, executing the application if not done so already."""
        
        self._stdout = subprocess.PIPE

        self._start_execute()
        self._process.wait()

        return self._process.communicate()[0].decode("utf-8")

    def __gt__(self, target):
        """Overrides the '>' to write the output to a file."""
        with open(target, "w") as outfile:
            self._stdout = outfile
            self._start_execute()
            self._process.wait()

        return self
    
    def __lt__(self, target):
        """Overrides the '<' to read in from a file."""
        # We need to pipe into the first in the chain so recurse through
        if self._previous != None:
            self._previous.__lt__()
        else:
            # TODO opening a file and never closing it!
            self._stdin = open(target, "r")

        return self

    def __rshift__(self, target):
        """Overrides the '>' to write the output to a file."""
        with open(target, "a") as outfile:
            self._stdout = outfile
            self._start_execute()
            self._process.wait()

        return self

    def __or__(self, target):
        """Overrides the '|' operator to do piping."""
        
        self._stdout = subprocess.PIPE
        self._start_execute()
        target._stdin = self._process.stdout

        return target

    def _start_execute(self):
        process_string = self._executable_path + " " + " ".join(self._args)

        self._process = subprocess.Popen(process_string, stdin=self._stdin, stdout=self._stdout, stderr=sys.stderr, close_fds=True)

    def run(self):
        """Force runs the application in case you need to explicitly run it."""
        self._start_execute()
        self._process.wait()

class ProcessError(Exception):
    """Exception raised when a process exits with a non-zero exit code."""

    def __init__(self, message):
        self.message = message

def _internal_print(output):
    """Prints stuff, because we've probably just overwritten 'print()'..."""
    __builtins__["print"](output)

def _lazy_invoke_executable(executable_path, args):
    """Executes the specified program with the given args with lazy evaluation."""
    return LazyInvocation(executable_path, args)

def _create_proxy_function(executable_path):
    """Creates a function that when run will execute the specified program with an arguments passed in."""
    return lambda *args, e=executable_path: _lazy_invoke_executable(e, args)

loaded = []
for path in os.environ["PATH"].split(";"):
    for executable_path in glob.glob(path + "\\*.exe"):
        name = os.path.splitext(os.path.basename(executable_path))[0]

        if (BE_SAFE and name in __builtins__.keys()):
            name = "pyash_" + name

        escaped_executable_path = "\"" + executable_path.replace("\"","\\\"") + "\""

        globals()[name] = _create_proxy_function(escaped_executable_path)
