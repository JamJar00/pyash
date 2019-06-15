import os, glob, subprocess, io

# Setting this true will ensure we don't overwrite any builtins like 'print' by appending 'pyash_'
BE_SAFE = False

class LazyInvocation():
    """Class returned when a shell application is 'run'. This allows us to do piping etc. through lazy execution of the program."""
    def __init__(self, executable_path, args):
        self.executable_path = executable_path
        self.args = args
        
        # We'll set this property once we actually do the evaluation
        self.have_run = False

        # These will get setup on the fly
        self.stdin = None
        self.stdout = None

    def __str__(self):
        """Returns the application's output, executing the application if not done so already."""
        
        # We want a string back so we'll need to setup a pipe we can read from to get the data
        (read_pipe, self.stdout) = os.pipe()

        self._execute()

        with open(read_pipe, "rb") as read_file:
            return read_file.read().decode("utf-8")

    # TODO >> and << operators

    def __gt__(self, target):
        """Overrides the '>' to write the output to a file."""
        self.stdout = open(target, "w")
        self._execute()
        return self
    
    def __lt__(self, target):
        """Overrides the '<' to read in from a file."""
        # TODO opening a file and never closing it!
        self.stdin = open(target, "r")
        return self

    def __or__(self, target):
        """Overrides the '|' operator to do piping."""
        
        # Create an OS pipe (returns (read, write) fiel descriptors) and set the processes to use those
        # TODO do we need to dispose of all these file descriptors? :|
        (target.stdin, self.stdout) = os.pipe()

        return target

    def _execute(self):
        """Ensures that the application has been run at some point and that an output is available."""
        if not self.have_run:
            process_string = self.executable_path + " " + " ".join(self.args)

            with subprocess.Popen(process_string, stdin=self.stdin, stdout=self.stdout, close_fds=True) as process:
                # TODO (From docs) Warning: This will deadlock when using stdout=PIPE and/or stderr=PIPE and the child process generates enough output to a pipe such that it blocks waiting for the OS pipe buffer to accept more data. Use communicate() to avoid that.
                process.wait()

                if process.returncode != 0:
                    raise ProcessError(f"Process exited with a non-zero exit code ({process.returncode}).")

            self.have_run = True
        else:
            raise ProcessError(f"Cannot rerun a process already invoked.")

    def run(self):
        """Force runs the application in case you need to explicitly run it."""
        self._execute()
        return self.__str__()

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
