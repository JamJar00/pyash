import os, glob, subprocess

# Setting this true will ensure we don't overwrite any builtins like 'print' by appending 'pysh_'
BE_SAFE = False

class LazyInvocation():
    """Class returned when a shell application is 'run'. This allows us to do piping etc. through lazy execution of the program."""
    def __init__(self, executable_path, args):
        self.executable_path = executable_path
        self.args = args
        # We'll get this property once we actually do the evaluation
        self.output = None

    def __str__(self):
        """Returns the application's output, executing the application if not done so already."""
        _internal_print("Converting to string")
        self._execute_if_not_done_so_already()
        return self.output

    def __gt__(self, target):
        """Overrides the '>' to write the output to a file."""
        self._execute_if_not_done_so_already()
        _internal_print(f"Writing '{self.output}' to file '{target}.'")
        return self
    
    def __lt__(self, target):
        """Overrides the '<' to read in from a file."""
        self._execute_if_not_done_so_already()
        _internal_print(f"Reading from file '{target}.'")
        return self

    def __or__(self, target):
        """Overrides the '|' operator to do piping."""
        self._execute_if_not_done_so_already()
        _internal_print(f"Piping '{self.output}'!")
        return self

    def _execute_if_not_done_so_already(self):
        """Ensures that the application has been run at some point and that an output is available."""
        if self.output == None:
            process_string = self.executable_path + " " + " ".join(self.args)
            _internal_print(f"Executing '{process_string}'.")
            
            with subprocess.Popen(process_string, stdout=subprocess.PIPE) as process:
                (self.output, _) = process.communicate()

                if process.returncode != 0:
                    raise ProcessError(f"Process exited with a non-zero exit code ({process.returncode}).")

            self.output = self.output.decode("utf-8")

    def run(self):
        """Force runs the application in case you need to explicitly run it."""
        self._execute_if_not_done_so_already()
        return self.output

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
            name = "pysh_" + name

        escaped_executable_path = "\"" + executable_path.replace("\"","\\\"") + "\""

        globals()[name] = _create_proxy_function(escaped_executable_path)
