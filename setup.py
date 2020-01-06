import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyash",
    version="0.1.0",
    author="Jamie Read",
    author_email="jamie@darkriftnetworking.com",
    description="Shell scripting... but in glorious Python! ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JamJar00/pyash",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)