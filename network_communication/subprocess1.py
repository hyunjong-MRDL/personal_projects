import subprocess

def dir():
    result = subprocess.run(['gedit'], capture_output=True, text=True, shell=True)
    print("Output of 'gedit' command:")
    print(result.stdout)

def calculator():
    result = subprocess.run(['gnome-calculator'], capture_output=True, text=True, shell=True)
    print("Output of 'calculator' command:")
    print(result.stdout)

def pbrush():
    result = subprocess.run(['code'], capture_output=True, text=True, shell=True)
    print("Output of 'vscode' command:")
    print(result.stdout)

if __name__ == "__main__":
    dir()
    calculator()
    pbrush()