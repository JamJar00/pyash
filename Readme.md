# Pyash
Hate shell scripting? Love Python! Meet the horrible Frankenstein of the two!

Pyash takes the best part of shell scripting, the ability to stream data through great chains of shell programs, and adds that ability to Python. In the process it retains the same familiar syntax but in a more Pythonic form!
```python
from pyash import cat, grep
cat(".gitignore") | grep("env") > "out.txt"
```

## Importing Shell Programs
Importing shell programs is as easy as
```python
from pyash import grep, find, bash
```
Pyash automatically searches your `PATH` variable and loads any executable programs it finds, making them available through import.

Try to avoid importing `*` as you'll find basic builtin functions like `print()` suddenly don't work!

## Running Shell Programs
Once you've imported the programs you want to import you can use them as you would any normal Python function splitting arguments or keeping them all together as you want:
```python
print(grep("-i", "-r", "env", "."))
print(grep("-i -r env ."))
```

**It's important to note that all programs are lazy evaluated**, i.e. a program only runs when Pyash knows where data is going.

For example, the above `grep` commands will only execute when you print their output.

That means that if you don't care about the output you'll need to make sure you call `run()` to make the program execute:
```python
kubectl("delete", "pod", "my-pod").run()
```

## Piping Data
Data can be piped between, to and from files using the same syntax you use in shell scripts:
```python
print(kubectl("get", "pods") | grep("postgres"))
echo("I'm a pretty butterfly") > butterfly.txt
echo("Flutter! Flutter! Flutter!") >> butterfly.txt
(docker("container", "stop") < "my_containers.txt").run()
```

Note that when you start piping a program's output somewhere else it begins execution, so the 2nd and 3rd examples don't need you to call `run()`.
