from pyash import cat, grep, rm

# You can pipe from one process to another and out to file...
cat(".gitignore") | grep("env") > "out.txt"

# ...and even pipe from files just as you would in bash...
print(cat() < "out.txt")

# ...though if you just need to run an application you'll need to tell it that!
rm("out.txt").run()
