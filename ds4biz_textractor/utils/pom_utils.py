import os
import json

def find_file(name:str,path=".",recursive=True):
    """It returns the absolute path of a file. If recursive is True it searches in all the parents directories"""
    p=os.path.join(path,name)
    if os.path.exists(p):
        return p
    else:
        if recursive and path!="/":
            return find_file(name,os.path.dirname(os.path.abspath(path)))
        else:
            raise Exception("File %s not found (in parent directories)"%name)
        
        

def strip_major_minor(version:str):
    return version.rsplit(".",1)[0]


def get_full_version():
    ppom=json.load(open(find_file("ppom.json")))
    return ppom['version']

def get_pom_major_minor():
    return strip_major_minor(get_full_version())
    

