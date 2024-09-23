import minecraft_launcher_lib
import subprocess
import sys
import logging
import os

#version = "1.12.2"
#username = "ShLKV"

minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()

print("===veLauncher by ShLKV=== (alpha v0.1)\n ")

version = input("version: ")
username = input("username: ")


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end=printEnd)
    if iteration == total:
        print()

def maximum(max_value, value):
    max_value[0] = value


def start():
    print('=======================================================================================')
    max_value = [0]
    callback = {
            "setStatus": lambda text: print(text, end='r'),
            "setProgress": lambda value: printProgressBar(value, max_value[0]),
            "setMax": lambda value: maximum(max_value, value)
    }


    minecraft_launcher_lib.install.install_minecraft_version(versionid=version, minecraft_directory=minecraft_directory, callback=callback)

    options = {
        'username': username,
    }
    subprocess.call(minecraft_launcher_lib.command.get_minecraft_command(version=version, minecraft_directory=minecraft_directory, options=options))
start()


