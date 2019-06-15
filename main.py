from pyash import echo

print(echo("Hello World!"))

echo() < "in.txt"
echo("I'm writing text!") > "out.txt"

print()

echo("Some text") | echo() > "out.txt"
