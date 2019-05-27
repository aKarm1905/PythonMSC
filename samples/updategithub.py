"""This script copies files and definitions from package fodler to github folder."""
import shutil
import os


def copyFiles(nodesrc=False, nodes=False, ladybug=False, ladybugx=False,
              pkgFolder=None, githubFolder=None, githubFolderX=None):
    """Update github repository.

    Args:
        nodesrc: Set to True to copy source code of nodes (srcFolder/extra/nodes/*.py)
        nodes: Set to True to copy dyf files (srcFolder/dyf/*.dyf)
        ladybug: Set to True to copy ladybug source files (srcFolder/extra/ladybugx/ladybug)
        ladybugx: Set to True to copy ladybugx source files (srcFolder/extra/ladybugx)
    """
    targetPyFolder = githubFolderX + r"\plugin\source"
    if nodesrc:
        # copy py files
        pyFolder = pkgFolder + r"\extra\nodesrc"
        for f in os.listdir(pyFolder):
            if f.lower().endswith(".py"):
                shutil.copyfile(pyFolder + "\\" + f, targetPyFolder + "\\" + f)

    targetNodeFolder = githubFolderX + r"\plugin\nodes"
    if nodes:
        nodeFolder = pkgFolder + r"\dyf"
        for f in os.listdir(nodeFolder):
            if f.lower().endswith(".dyf"):
                shutil.copyfile(nodeFolder + "\\" + f, targetNodeFolder + "\\" + f)

    # copy ladybugdynamo libraries and ladybug libraries to dynamo folder
    srcLadybugFolder = pkgFolder + r"\extra\ladybugdynamo\\ladybug"
    srcDyanomFolder = pkgFolder + r"\extra\ladybugdynamo"
    targetDyanmoFolder = githubFolderX + "\ladybugdynamo"
    targetLadybugDynamoFolder = githubFolderX + "\ladybugdynamo\ladybug"

    if ladybug:
        for f in os.listdir(srcLadybugFolder):
            if f.endswith(".py"):
                shutil.copyfile(srcLadybugFolder + "\\" + f, githubFolder + "\\" + f)
                shutil.copyfile(srcLadybugFolder + "\\" + f, targetLadybugDynamoFolder + "\\" + f)

    if ladybug:
        for f in os.listdir(srcDyanomFolder):
            if f.endswith(".py"):
                shutil.copyfile(srcDyanomFolder + "\\" + f, targetDyanmoFolder + "\\" + f)


if __name__ == "__main__":
    copyFiles(nodesrc=True, nodes=True, ladybug=True, ladybugx=True,
              pkgFolder=r"C:\Users\Administrator\AppData\Roaming\Dynamo\Dynamo Revit\1.0\packages\Ladybug",
              githubFolder=r"C:\Users\Administrator\Documents\GitHub\ladybug\ladybug",
              githubFolderX=r"C:\Users\Administrator\Documents\GitHub\ladybug-dynamo")
