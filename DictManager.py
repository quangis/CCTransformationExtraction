from FileManager import *


class DictManager:
    # [X] Read Core concepts.txt into a dictionary.
    @staticmethod
    def load_ccdict():
        coreCon = {}
        text = []
        tag = []
        meaLevel = []  # measurement level

        # [SC] load the core concept dictionary file as a list of lines
        coreConcepts = FileManager.loadFileP(FileManager.corePath)

        for line in coreConcepts:
            cur = line.strip().split('\t')
            text.append(cur[0].lower())
            tag.append(cur[1].lower())
            if len(cur) == 3:
                meaLevel.append(cur[2].lower())
            else:
                meaLevel.append('null')

        coreCon['text'] = text
        coreCon['tag'] = tag
        coreCon['measureLevel'] = meaLevel

        sorted_coreCon = sorted(zip(coreCon['text'], coreCon['tag'], coreCon['measureLevel']),
                                key=lambda x: len(x[0]), reverse=True)

        return sorted_coreCon

    # [X] network dictionary into networkSet
    @staticmethod
    def loadNetDict():
        networkConcepts = FileManager.loadFileP(FileManager.networkPath)
        networkSet = set(l.strip().lower() for l in networkConcepts)
        sorted_networkSet = sorted(networkSet, key=len, reverse=True)
        return sorted_networkSet

    # [X] Read extremaTrans.txt into a dictionary.
    @staticmethod
    def readExtremaR():
        extreR = {}

        keyword = []
        tType = []  # types may involve in transformations
        cctag = []  # core concept type
        ml = []  # measurement level

        extR = FileManager.loadFileP(FileManager.extfilePath)

        for line in extR:
            cur_ext = line.strip().split('\t')
            keyword.append(cur_ext[0].lower())
            tType.append(cur_ext[1].lower())
            cctag.append(cur_ext[2].lower())
            if len(cur_ext) == 4:
                ml.append(cur_ext[3].lower())
            else:
                ml.append('null')

        extreR['keyword'] = keyword
        extreR['tType'] = tType
        extreR['cctag'] = cctag
        extreR['ml'] = ml

        return extreR
