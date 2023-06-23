from pathlib import Path
import json

from Logger import *


# [SC] FileManager class manages loading and parsing all local files
class FileManager:
    # [SC] static variables for the root directory
    rootPath = Path(__file__).parent

    ###########################################################
    ### [SC][TODO] eventually these paths and filenames should be moved to a config file, and not hardcoded
    ruleDir = rootPath / "Rules"

    rulePath = ruleDir / "conversionRules.json"
    chPath = ruleDir / "hConceptHierarchy.json"
    mhPath = ruleDir / "measureHierarchy.json"
    mhCPath = ruleDir / "measureHierarchyCct.json"

    dictDir = rootPath / "Dictionary"

    corePath = dictDir / 'coreConceptsML.txt'
    networkPath = dictDir / 'network.txt'
    extfilePath = dictDir / "extremaTrans.txt"

    ### [SC]
    ###########################################################


    # [SC] Static method for loading a json file.
    # @param    pathlib.Path    filePath    Path to the file.
    # @return   json object
    @staticmethod
    def loadJsonP(filePath):
        methodName = "FileManager.loadJsonP"

        jsonObj = {}

        if filePath.is_file():
            try:
                jsonObj = json.load(open(filePath))
            except Exception as e:
                Logger.cPrint(Logger.ERROR_TYPE, methodName
                              , f"Cannot parse the json file '{filePath}.'\n{e}")
        else:
            Logger.cPrint(Logger.ERROR_TYPE, methodName
                          , f"Cannot load the json file '{filePath}.' The file does not exist.")

        return jsonObj


    # [SC] Static method for loading a json file.
    # @param    string      filename    Name of the json file.
    # @param    string      dirName     Sub-directory containing the json file.
    #                                   If not specified assumes that the json file
    #                                   is located in the root directory.
    # @return   json object
    @staticmethod
    def loadJsonF(filename, dirName=None):
        methodName = "FileManager.loadJsonF"

        if dirName:
            return FileManager.loadJsonP(FileManager.rootPath / dirName / filename)
        else:
            return FileManager.loadJsonP(FileManager.rootPath / filename)


    # [SC] Static method for loading a json file.
    # @param    pathlib.Path    filePath    Path to the file.
    # @param    boolean         lines       If true individual lines are parsed.
    # @param    string          enc         Encoding type.
    # @return   list                        If lines=False then returns a list with a single element
    #                                       containing the entire content of the file. If lines=True,
    #                                       then returns a list where each element is a separate line in the file.
    @staticmethod
    def loadFileP(filePath, lines=True, enc="utf-8"):
        methodName = "FileManager.loadFileP"

        if filePath.is_file():
            try:
                with open(filePath, 'r', encoding=enc) as f:
                    if lines:
                        return f.readlines()
                    else:
                        return [f.read()]
            except Exception as e:
                Logger.cPrint(Logger.ERROR_TYPE, methodName
                              , f"Cannot load the file '{filePath}.'\n{e}")
        else:
            Logger.cPrint(Logger.ERROR_TYPE, methodName
                          , f"Cannot load the file '{filePath}.' The file does not exist.")

        return None


    # [SC] Static method for loading the content of a file.
    # @param    string      filename    Name of the file.
    # @param    string      dirName     Sub-directory containing the file;
    #                                   If not specified assumes that the file
    #                                   is located in the root directory.
    # @param    boolean     lines       If true individual lines are parsed.
    # @param    string      enc         Encoding type.
    # @return   list                    If lines=False then returns a list with a single element
    #                                   containing the entire content of the file. If lines=True,
    #                                   then returns a list where each element is a separate line in the file.
    @staticmethod
    def loadFile(filename, dirName=None, lines=True, enc="utf-8"):
        methodName = "FileManager.loadFile"

        if dirName:
            return FileManager.loadFileP(FileManager.rootPath / dirName / filename, lines, enc)
        else:
            return FileManager.loadFileP(FileManager.rootPath / filename, lines, enc)
