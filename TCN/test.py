import subprocess
import sys
import os
import glob
# 第一个参数是要运行的ls命令，第二个参数是ls命令的参数
completed1 = subprocess.run(['ls', '-l'])
print('returncode:', completed1.returncode)


filepath = os.path.join("./test.txt")
output_file = open(filepath, "w")        # 重复写，并覆盖上次的内容
# completed2 = subprocess.run([sys.executable,'sub_test.py','3','4'],stdout=output_file)   #设置子进程的解释器为父进程在使用的解释器
completed2 = subprocess.run(['python','sub_test.py','3','4'],stdout=output_file)   # 子进程执行sub_test.py，并将print的输出内容重定向到test.txt中
print('returncode:', completed2.returncode)
print(os.getcwd())  # 获取当前工作目录

listT = []
listT.extend("Hello")
listT.extend("Pycha")
print(listT)

target = os.getcwd()
match = glob.glob(os.path.join(target,"*.py"))
print(os.path.join(target,"*.py"))
#print(match)
print(len(match))

import fnmatch
print(fnmatch.fnmatch(target+"test.py","*.py"))

