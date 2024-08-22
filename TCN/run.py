# Kay Hutchinson 2/18/2022
# Script to automate TCN experiments for MICCAI
# Runs preprocess.py, tune.py, and train_test_val.py for combinations
# of dataset, labeltype, and valtype and saves results.

import os
import sys
import subprocess
from datetime import datetime
import shutil


# Model options
#Tasks including S(suturing)、NP(Needle Passing)、KT(Knotting Typing
#JIGSAWS:S(suturing)、NP(Needle Passing)、KT(Knotting Typing;
#
sets = ["S", "NP", "KT", "PT", "PoaP", "PaS", "SNP", "JIGSAWS", "ROSMA", "PTPaS", "All"]   # 11
vars = ["velocity", "orientation", "all", "vis", "vis2"]                                   # 5, 常用设置为前两个
labeltypes = ["MPbaseline", "MPleft", "MPright", "gesture", "MPcombined", "MPexchange", "MPleftX", "MPrightX", "MPleftE", "MPrightE"]
valtypes = ["LOSO", "LOUO", "LOTO", "random"]

# 交叉验证的方式
#LOUO:Leave-One-User-Out       # 类比留一交叉验证理解
#LOTO:Leave-One-Task-Out
#LOSO:Leave-One-Supertrial-Out  supertrail ith is defined at the ith trial from all subjects


# print(sys.executable)     # 所使用解释器的路径

virtualenvPythonPath = sys.executable
print(type(virtualenvPythonPath))

# Create folder for results
dir = os.getcwd()          # 获取当前工作目录---->运行文件所处的当前目录
print('working on dir: ', dir)
resultsDir = os.path.join(dir, "Results")
if not os.path.exists(resultsDir):
    os.mkdir(resultsDir)


# Iterate through each combination of settings
for set in sets[7:8]:
    for var in vars[0:1]:
        for labeltype in labeltypes[3:4]:
            for valtype in valtypes[1:2]:

                # Create folder named by current time and config
                now = datetime.now()
                timeNow = now.strftime("%Y_%m_%d_%H_%M_%S")        #月_日_年_小时_分钟
                logFolder = set +"_"+ var +"_"+ labeltype +"_"+ valtype +"_run_"+ timeNow
                logDir =  os.path.join(resultsDir, logFolder)
                os.mkdir(logDir)      #只创建最后一级不存在的目录，如果最后一次目录的上层目录不存在，则会报错

                print("---------Results will be stored in: " + logDir)
                # Copy config file over first
                # path to config file
                configPath = os.path.join(dir, "config.json")
                shutil.copy2(configPath, logDir)           # 复制源文件，并保留源文件(深拷贝)



                # Preprocess
                # File to pipe outputs to:
                print("Preprocessing " + set + " " + var + " " + labeltype + " " + valtype)
                prepOutPath = os.path.join(logDir, "prep.txt")
                prepOutFile = open(prepOutPath,"w")
                #preprocessTask = "python preprocess.py " + set + " " + var + " " + labeltype + " " + valtype + " > " + prepOut
                # subprocess.call(preprocessTask, shell=True)
                preprocessTask = "preprocess.py"
                print("execute commandline :python "+preprocessTask+" "+set + " " + var + " " + labeltype + " " + valtype + " > " + prepOutPath)

                subp1 = subprocess.run([virtualenvPythonPath, preprocessTask,set,var,labeltype,valtype],stdout =prepOutFile)        # 为子进程的指定运行的虚拟环境
                print('subp1 returncode:', subp1.returncode)

                # Tune
                # File to pipe outputs to
                print("Tuning " + set + " " + var + " " + labeltype + " " + valtype)
                tuneOutPath = os.path.join(logDir, "tune.txt")
                #tuneTask = "python tune.py " + set + " " + var + " " + labeltype + " " + valtype + " > " + tuneOut
                #print(tuneTask)
                #subprocess.call(tuneTask, shell=True)

                tuneTask = "tune.py"
                tuneOutFile = open(tuneOutPath, "w")
                print("execute commandline :python " + tuneTask + " " + set + " " + var + " " + labeltype + " " + valtype + " > " + tuneOutPath)
                subp2 = subprocess.run([virtualenvPythonPath, tuneTask,set,var,labeltype,valtype],stdout =tuneOutFile)
                # print('subp2 returncode:', subp2.returncode) # for debug

                # Train
                # File to pipe outputs to
                print("Training " + set + " " + var + " " + labeltype + " " + valtype)
                trainOutPath = os.path.join(logDir, "train.txt")
                #trainTask = "python train_test_val.py " + set + " " + var + " " + labeltype + " " + valtype + " > " + trainOut
                #print(trainTask)
                #subprocess.call(trainTask, shell=True)

                trainTask = "train_test_val.py"
                trainOutFile = open(trainOutPath,"w")
                print("execute commandline :python " + trainTask + " " + set + " " + var + " " + labeltype + " " + valtype + " > " + trainOutPath)
                subp3 = subprocess.run([virtualenvPythonPath, trainTask, set, var, labeltype, valtype], stdout=trainOutFile)
                # print('subp3 returncode:', subp3.returncode) # for debug
print("Done!")



























# EOF
