Set objShell = CreateObject("WScript.Shell")
objShell.CurrentDirectory = "C:\Users\{username}\Desktop\Python Main\Pc Utils"
objShell.Run "python main.py", 0, False
