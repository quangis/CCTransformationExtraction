from Logger import *
from KeyStatics import *


class HConcept:
    def __init__(self, conceptStrP, cctStrP=None):
        # [SC] a unique string identfier of this node # [TODO] getter/setter
        self.conceptStr = conceptStrP
        # [SC] list of direct parent objects, instances of HConcept class
        self.parents = []
        # [SC] list of direct child objects, instances of HConcept class
        self.children = []
        # [SC] cct expression of this concept # [TODO] getter/setter
        self.cctStr = cctStrP

    # [SC] getter method for 'conceptStr' field
    # @return   string  Value of conceptStr
    # def getConceptStr(self):
    #     return self.conceptStr

    # [SC] setter method for 'cctStr' field
    # @param    string  cctStrP     New value for cctStrP
    # @return   void
    # def setCCT(self, cctStrP):
    #     self.cctStr = cctStrP

    # [SC] getter method for 'cctStr' field
    # @return   string  Value of cctStr
    # def getCCT(self):
    #     return self.cctStr

    # [SC] returns true if there is a parent with given string identifier
    # @param    string  conceptStrP     identifier of the parent concept
    # @return   boolean                 True if a matching parent is found, False otherwise
    def hasParent(self, conceptStrP):
        if self.hasDirectParent(conceptStrP):
            return True
        else:
            for parent in self.parents:
                if parent.hasParent(conceptStrP):
                    return True
        return False

    # [SC] returns true if there is a direct parent with given string identifier
    # @param    string  conceptStrP     identifier of the parent concept
    # @return   boolean                 True if a matching direct parent is found, False otherwise
    def hasDirectParent(self, conceptStrP):
        for parent in self.parents:
            if parent.conceptStr.lower() == conceptStrP.lower():
                return True
        return False

    # [SC] returns true if there is a child with given string identifier
    # @param    string  conceptStrP     identifier of the child concept
    # @return   boolean                 True if a matching child is found, False otherwise
    def hasChild(self, conceptStrP):
        if self.hasDirectChild(conceptStrP):
            return True
        else:
            for child in self.children:
                if child.hasChild(conceptStrP):
                    return True
        return False

    # [SC] returns true if there is a direct child with given string identifier
    # @param    string  conceptStrP     identifier of the child concept
    # @return   boolean                 True if a matching direct child is found, False otherwise
    def hasDirectChild(self, conceptStrP):
        for child in self.children:
            if child.conceptStr.lower() == conceptStrP.lower():
                return True
        return False

    # [SC] Returns a list of string identifiers of all parents of this node
    # @return   list    A list with string identifiers
    def getAllParentsStr(self):
        parentsStr = []
        for parent in self.parents:
            parentsStr.append(parent.conceptStr)
            parentsStr.extend(parent.getAllParentsStr())
        return list(set(parentsStr))

    # [SC] Returns a list of string identifiers of all children of this node
    # @return   list    A list with string identifiers
    def getAllChildrenStr(self):
        childrenStr = []
        for child in self.children:
            childrenStr.append(child.conceptStr)
            childrenStr.extend(child.getAllChildrenStr())
        return list(set(childrenStr))

    # [SC] Custom static printing method.
    # @param    json object     hierarchyJson   Message type (ERROR, WARNING, INFO, etc).
    # @param    dictionary      hiearchyDict    Name of the method that call this method.
    # @return   void
    @staticmethod
    def parseHiearchy(hierarchyJson, hiearchyDict):
        methodName = "parseHiearchy"

        if not hierarchyJson:
            Logger.cPrint(Logger.ERROR_TYPE, methodName
                          , f"Cannot create concept hierarchy. 'hierarchyJson' is empty.")
            return

        if not isinstance(hiearchyDict, dict):
            Logger.cPrint(Logger.ERROR_TYPE, methodName
                          , f"Cannot create concept hierarchy. 'hiearchyDict' is not dictionary.")
            return

        for term in hierarchyJson[T.termsK]:
            if term[T.conceptK] not in hiearchyDict:
                hiearchyDict[term[T.conceptK]] = HConcept(term[T.conceptK], term[T.cctK])
            else:
                Logger.cPrint(Logger.ERROR_TYPE, methodName
                              , f"Cannot create concept hierarchy. Duplicate concept '{term[T.conceptK]}' found.")
                return

        for relation in hierarchyJson[T.hierarchyK]:
            if relation[T.superK] not in hiearchyDict:
                Logger.cPrint(Logger.ERROR_TYPE, methodName
                              , f"Cannot create concept hierarchy. '{relation[T.superK]}' not found among terms.")
                return

            if relation[T.subK] not in hiearchyDict:
                Logger.cPrint(Logger.ERROR_TYPE, methodName
                              , f"Cannot create concept hierarchy. '{relation[T.subK]}' not found among terms.")
                return

            superC = hiearchyDict[relation[T.superK]]
            subC = hiearchyDict[relation[T.subK]]

            superC.children.append(subC)
            subC.parents.append(superC)
