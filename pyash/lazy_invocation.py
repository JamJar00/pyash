import subprocess, sys
from .process_error import ProcessError
from .expression_already_completed_error import ExpressionAlreadyCompletedError

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

        self.run()

        return self._process.communicate()[0].decode("utf-8")

    def __gt__(self, target):
        """Overrides the '>' to write the output to a file."""
        self._stdout = open(target, "w")
        
        self.run()

        return self
    
    def __lt__(self, target):
        """Overrides the '<' to read in from a file."""
        # We need to pipe into the first in the chain so recurse through
        if self._previous != None:
            self._previous.__lt__(target)
        else:
            self._stdin = open(target, "r")

        return self

    def __rshift__(self, target):
        """Overrides the '>>' to append the output to a file."""
        self._stdout = open(target, "a")
        
        self.run()

        return self

    def __or__(self, target):
        """Overrides the '|' operator to do piping."""
        
        self._stdout = subprocess.PIPE
        self._start_execute()
        target._stdin = self._process.stdout

        return target

    def _start_execute(self):
        """Starts executing this expression."""
        if self._process:
            raise ExpressionAlreadyCompletedError("The expression has already completed and cannot be run again.")
        
        process_string = self._executable_path + " " + " ".join(self._args)

        self._process = subprocess.Popen(process_string, stdin=self._stdin, stdout=self._stdout, stderr=sys.stderr, close_fds=True)

    def run(self):
        """Runs the expression if not already run."""
        if self._process:
            return self
        
        self._start_execute()
        return_code = self._process.wait()

        if hasattr(self._stdin, 'close'):
            self._stdin.close()
        if hasattr(self._stdout, 'close'):
            self._stdout.close()

        if return_code != 0:
            raise ProcessError("A process returned a non-zero exit code. Exit code: " + return_code)

        return self
