from cx_Freeze import setup, Executable
import sys

# Redirect stdout and stderr to a file
sys.stdout = open("stdout.txt", "w")
sys.stderr = open("stderr.txt", "w")

setup(
    name="MyExecutable",
    version="1.0",
    description="My Python Executable",
    executables=[Executable("your_script.py")]
)

