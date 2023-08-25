import re

from HConcept import *
from KeyStatics import *
from FileManager import *
from Logger import *


class TQConverter:
    # [SC] load the rules for annotating with cct expressions
    convRules = FileManager.loadJsonP(FileManager.rulePath)

    # [SC] load the concept type hierachy
    hConceptHierarchy = {}
    HConcept.parseHiearchy(FileManager.loadJsonP(FileManager.chPath), hConceptHierarchy)

    # [SC] load the measurement hierachy
    measureHierarchy = {}
    HConcept.parseHiearchy(FileManager.loadJsonP(FileManager.mhPath), measureHierarchy)

    measureHierarchyCct = {}
    HConcept.parseHiearchy(FileManager.loadJsonP(FileManager.mhCPath), measureHierarchyCct)

    # [SC] constants indicating which types should be used to generate template rules
    ALL = 1         # [SC] use all types
    CCT_ONLY = 2    # [SC] use only types with annotated cct expressions
    EMPTY_ONLY = 3  # [SC] use only types with empty or no cct expressions

    # [SC] constructor
    def __init__(self):
        pass

    # [SC][TODO]
    def isRulesLoaded(self):
        methodName = "TQConverter.isRulesLoaded"

        if not TQConverter.convRules:
            return False
        return True

    # [SC][TODO]
    def isConsistentRules(self):
        methodName = "TQConverter.isConsistentRules"

        # [TODO]
        return True

    # [SC][TODO] cardinality of json objects with the same key is not considered (e.g., "type":"object","type":"field")
    # [SC] Sets qJson['valid'] to "T" if a question annotation has a valid structure and values, and to "F" otherwise.
    # @param    dictionary  qJson   A JSON object of the question annotation.
    # @return   void
    def isValidQJson(self, qJson):
        methodName = "TQConverter.isValidQJson"

        typeIds = []
        questionStr = "?"
        qJson[T.validK] = "T"

        if T.questionK not in qJson:
            Logger.cPrint(Logger.ERROR_TYPE, methodName
                          , f"'{T.questionK}' not found in '{qJson}'.")
            qJson[T.validK] = "F"
        else:
            questionStr = qJson[T.questionK]

        if T.cctransK not in qJson:
            Logger.cPrint(Logger.ERROR_TYPE, methodName
                          , f"'{T.cctransK}' not found in '{questionStr}'.")
            qJson[T.validK] = "F"
            return

        if T.typesK not in qJson[T.cctransK]:
            Logger.cPrint(Logger.ERROR_TYPE, methodName
                          , f"'{T.typesK}' not found in '{questionStr}'.")
            qJson[T.validK] = "F"
            return
        else:
            typesList = qJson[T.cctransK][T.typesK]
            if not typesList:
                Logger.cPrint(Logger.ERROR_TYPE, methodName
                              , f"'{T.typesK}' has empty value in '{questionStr}'.")
                qJson[T.validK] = "F"
            elif not isinstance(typesList, list):
                Logger.cPrint(Logger.ERROR_TYPE, methodName
                              , f"'{T.typesK}' is not a list in '{questionStr}'.")
                qJson[T.validK] = "F"
            else:
                for typeObj in typesList:
                    typeId = "?"
                    # [SC] validate 'id' in type object
                    if T.idK not in typeObj:
                        Logger.cPrint(Logger.ERROR_TYPE, methodName
                                      , f"'{T.idK}' is missing for type object in '{questionStr}'.")
                        qJson[T.validK] = "F"
                    elif not typeObj[T.idK]:
                        Logger.cPrint(Logger.ERROR_TYPE, methodName
                                      , f"'{T.idK}' has empty value for type object in '{questionStr}'.")
                        qJson[T.validK] = "F"
                    elif not isinstance(typeObj[T.idK], str):
                        Logger.cPrint(Logger.ERROR_TYPE, methodName
                                      , f"'{T.idK}' for a type object does not have a string value in '{questionStr}'.")
                        qJson[T.validK] = "F"
                    elif typeObj[T.idK] in typeIds:
                        Logger.cPrint(Logger.ERROR_TYPE, methodName
                                      , f"Duplicate 'id={typeObj[T.idK]}' for type object is found in '{questionStr}'.")
                        qJson[T.validK] = "F"
                    else:
                        typeIds.append(typeObj[T.idK])
                        typeId = typeObj[T.idK]

                    # [SC] validate 'type' in type object
                    if T.typeK not in typeObj:
                        Logger.cPrint(Logger.ERROR_TYPE, methodName
                                      ,
                                      f"'{T.typeK}' is missing for type object with id '{typeId}' in '{questionStr}'.")
                        qJson[T.validK] = "F"
                    elif not isinstance(typeObj[T.typeK], str):
                        Logger.cPrint(Logger.ERROR_TYPE, methodName
                                      ,
                                      f"'{T.typeK}' is not a string for type object with id '{typeId}' in '{questionStr}'.")
                        qJson[T.validK] = "F"
                    elif typeObj[T.typeK] not in TQConverter.hConceptHierarchy:
                        Logger.cPrint(Logger.ERROR_TYPE, methodName
                                      ,
                                      f"Invalid 'type={typeObj[T.typeK]}' for type object with id '{typeId}' in '{questionStr}'.")
                        qJson[T.validK] = "F"

                    # [SC] validate 'measureLevel' in type object
                    if T.measureK in typeObj:
                        if not isinstance(typeObj[T.measureK], str):
                            Logger.cPrint(Logger.ERROR_TYPE, methodName
                                          ,
                                          f"'{T.measureK}' is not a string for type object with id '{typeId}' in '{questionStr}'.")
                            qJson[T.validK] = "F"
                        elif typeObj[T.measureK] not in TQConverter.measureHierarchy:
                            Logger.cPrint(Logger.ERROR_TYPE, methodName
                                          ,
                                          f"Invalid 'measureLevel={typeObj[T.measureK]}' for type object with id '{typeId}' in '{questionStr}'.")
                            qJson[T.validK] = "F"

                    # [SC][TODO] check cct against all possible expression
                    # if 'cct' in typeObj:

        # [SC] validate 'extent'
        if T.extentK not in qJson[T.cctransK]:
            Logger.cPrint(Logger.WARNING_TYPE, methodName
                          , f"'{T.extentK}' not found in '{questionStr}'.")
            # qJson[T.validK] = "F"
        else:
            extentObj = qJson[T.cctransK][T.extentK]
            if not isinstance(extentObj, list):
                Logger.cPrint(Logger.WARNING_TYPE, methodName
                              , f"'{T.extentK}' is not a list in '{questionStr}'.")
                # qJson[T.validK] = "F"
            # [SC][TODO] still think there should be only one extent per questions
            # elif len(extentObj) != 1:
            #     Logger.cPrint(Logger.WARNING_TYPE, methodName
            #                   , f"'{T.extentK}' should have exactly one value in '{questionStr}'.")
            #     # qJson[T.validK] = "F"
            elif extentObj[0] not in typeIds:
                Logger.cPrint(Logger.WARNING_TYPE, methodName
                              , f"'{T.extentK}' has unknown id in '{questionStr}'.")
                # qJson[T.validK] = "F"

        # [SC] validate 'transformations'
        if T.transformK not in qJson[T.cctransK]:
            Logger.cPrint(Logger.ERROR_TYPE, methodName
                          , f"'{T.transformK}' not found for '{questionStr}'.")
            qJson[T.validK] = "F"
        elif not isinstance(qJson[T.cctransK][T.transformK], list):
            Logger.cPrint(Logger.ERROR_TYPE, methodName
                          , f"'{T.transformK}' is not a list in '{questionStr}'.")
            qJson[T.validK] = "F"
        elif len(qJson[T.cctransK][T.transformK]) == 0:
            Logger.cPrint(Logger.ERROR_TYPE, methodName
                          , f"'{T.transformK}' should have at least one transformation in '{questionStr}'.")
            qJson[T.validK] = "F"
        else:
            # [SC] validate each transformation object
            for trans in qJson[T.cctransK][T.transformK]:
                if T.beforeK not in trans:
                    Logger.cPrint(Logger.ERROR_TYPE, methodName
                                  , f"'{T.beforeK}' is missing for transformation in '{questionStr}'.")
                    qJson[T.validK] = "F"
                elif not isinstance(trans[T.beforeK], list):
                    Logger.cPrint(Logger.ERROR_TYPE, methodName
                                  , f"'{T.beforeK}' is not a list in '{questionStr}'.")
                    qJson[T.validK] = "F"
                elif len(trans[T.beforeK]) == 0:
                    Logger.cPrint(Logger.ERROR_TYPE, methodName
                                  , f"'{T.beforeK}' is an empty list in '{questionStr}'.")
                    qJson[T.validK] = "F"
                else:
                    for beforeId in trans[T.beforeK]:
                        if beforeId not in typeIds:
                            Logger.cPrint(Logger.ERROR_TYPE, methodName
                                          , f"'{T.beforeK}' has unknown 'id={beforeId}' in '{questionStr}'.")
                            qJson[T.validK] = "F"

                if T.afterK not in trans:
                    Logger.cPrint(Logger.ERROR_TYPE, methodName
                                  , f"'{T.afterK}' is missing for transformation in '{questionStr}'.")
                    qJson[T.validK] = "F"
                elif not isinstance(trans[T.afterK], list):
                    Logger.cPrint(Logger.ERROR_TYPE, methodName
                                  , f"'{T.afterK}' is not a list in '{questionStr}'.")
                    qJson[T.validK] = "F"
                elif len(trans[T.afterK]) != 1:
                    Logger.cPrint(Logger.ERROR_TYPE, methodName
                                  , f"'{T.afterK}' should have exactly one value in '{questionStr}'.")
                    qJson[T.validK] = "F"
                elif trans[T.afterK][0] not in typeIds:
                    Logger.cPrint(Logger.ERROR_TYPE, methodName
                                  , f"'{T.afterK}' has unknown 'id={trans[T.afterK][0]}' in '{questionStr}'.")
                    qJson[T.validK] = "F"

                if T.keyK in trans:
                    if not isinstance(trans[T.keyK], str):
                        Logger.cPrint(Logger.ERROR_TYPE, methodName
                                      , f"'{T.keyK}' is not a string for transformation '{trans}' in '{questionStr}'.")
                        qJson[T.validK] = "F"
                    elif trans[T.keyK] not in typeIds:
                        Logger.cPrint(Logger.ERROR_TYPE, methodName
                                      ,
                                      f"'{T.keyK}' has unknown 'id={trans[T.keyK]}' for transformation '{trans}' in '{questionStr}'.")
                        qJson[T.validK] = "F"

    # [SC] Returns True if two rules are identical (value-wise)
    # @param:  dictionary  ruleOne      A JSON object for the first rule.
    # @param:  dictionary  ruleTwo      A JSON object for the second rule.
    # @return: boolean                  True or False
    def sameRule(self, ruleOne, ruleTwo):
        methodName = "TQConverter.sameRule"

        if not (ruleOne and ruleTwo):
            return False

        if not self.sameLHS(ruleOne[T.lhsK], ruleTwo[T.lhsK]):
            return False

        # [SC] remove all white spaces before comparison
        if "".join(ruleOne[T.rhsK].split()) != "".join(ruleTwo[T.rhsK].split()):
            return False

        return True

    # [SC] Returns True if two LHS statements are identical (value-wise)
    # @param:  dictionary  qLhs        A JSON object for LHS created from a question type.
    # @param:  dictionary  ruleLhs     A JSON object of a rule's LHS.
    # @return: boolean                 True or False
    def sameLHS(self, qLhs, ruleLhs):
        methodName = "TQConverter.sameLHS"

        # [SC] compare types
        if qLhs[T.typeK].lower() != ruleLhs[T.typeK].lower():
            return False

        # [SC] compare measureLevel
        if T.measureK in qLhs and T.measureK not in ruleLhs:
            return False
        elif T.measureK not in qLhs and T.measureK in ruleLhs:
            return False
        elif T.measureK in qLhs and T.measureK in ruleLhs:
            if qLhs[T.measureK].lower() != ruleLhs[T.measureK].lower():
                return False

        # [SC] compare inputType
        if T.inputTypeK in qLhs and T.inputTypeK not in ruleLhs:
            return False
        elif T.inputTypeK not in qLhs and T.inputTypeK in ruleLhs:
            return False
        elif T.inputTypeK in qLhs and T.inputTypeK in ruleLhs:
            if len(qLhs[T.inputTypeK]) == len(ruleLhs[T.inputTypeK]):
                qLhs[T.inputTypeK].sort()
                ruleLhs[T.inputTypeK].sort()
                for indexVal in range(len(ruleLhs[T.inputTypeK])):
                    if qLhs[T.inputTypeK][indexVal].lower() != ruleLhs[T.inputTypeK][indexVal].lower():
                        return False
            else:
                return False

        # [SC] compare key
        if T.keyK in qLhs and T.keyK not in ruleLhs:
            return False
        elif T.keyK not in qLhs and T.keyK in ruleLhs:
            return False
        elif T.keyK in qLhs and T.keyK in ruleLhs:
            if qLhs[T.keyK].lower() != ruleLhs[T.keyK].lower():
                return False

        return True

    # [SC] From a given question type, creates dictionary object representing LHS statement of a rule
    # @param:  dictionary  parsedTypeObj   A JSON object of the question type.
    # @param:  dictionary  qJson           A JSON object of the question annotation.
    # @return: dictionary                  returns the created LHS object
    def createLhs(self, parsedTypeObj, qJson):
        methodName = "TQConverter.createLhs"

        if T.validK not in qJson:
            self.isValidQJson(qJson)
        if qJson[T.validK] != "T":
            Logger.cPrint(Logger.ERROR_TYPE, methodName
                          , f"Cannot create LHS statement. Invalid JSON structure. None returned.")
            return None

        # [SC] add type information; assumed that type contains exactly one value
        tempLhs = {T.typeK: parsedTypeObj[T.typeK]}

        # [SC] add measureLevel information if it exists in the question type annotation
        if T.measureK in parsedTypeObj:
            tempLhs[T.measureK] = parsedTypeObj[T.measureK]

        # [SC] add inputType information if the current type is an output
        inputTypes = []
        for transformation in qJson[T.cctransK][T.transformK]:
            # [SC] in after part, id with '_u' suffix is different from the id without the suffix,
            # that is, given {"before": ["2","3"],"after": ["3_u"]},
            # '2' and '3' are not considered as input for '3'

            # [SC] if true then this transformmation has the current type as the 'after' value
            if transformation[T.afterK][0] == parsedTypeObj[T.idK]:
                # [SC] iterate through the before Ids
                for beforeId in transformation[T.beforeK]:
                    # [SC] id with '_u' suffix is a valid input type
                    beforeId = beforeId.replace('_u', '')
                    for inputTypeObj in qJson[T.cctransK][T.typesK]:
                        if inputTypeObj[T.idK] == beforeId:
                            inputTypes.append(inputTypeObj[T.typeK])

                # [SC] if there is a 'key' json object then add it to the new LHS
                if T.keyK in transformation:
                    # [SC] extract key's type
                    for keyTypeObj in qJson[T.cctransK][T.typesK]:
                        if keyTypeObj[T.idK] == transformation[T.keyK]:
                            tempLhs[T.keyK] = keyTypeObj[T.typeK]
                            break
                    # [SC] sanity check; make sure the key's type was successfully extracted
                    if T.keyK not in tempLhs:
                        Logger.cPrint(Logger.ERROR_TYPE, methodName
                                      , f"Cannot find the type for the key '{transformation[T.keyK]}' " +
                                      f"of the type object '{parsedTypeObj}' in {qJson[T.questionK]}. " +
                                      "Assigning 'NA' value to the key's type.")
                        tempLhs[T.keyK] = 'NA'

        if inputTypes:
            tempLhs[T.inputTypeK] = inputTypes

        return tempLhs

    # [SC] Given question annotations, generates templates for rules using the types info in each question annotation.
    # @param:  list        parsedQuestions     A list of JSON objects annotating question.
    # @param:  dictionary  ruleTemplates       A JSON dictionary to which the new rules should be added
    # @param:  integer     method              Defines which types should be used to generate rules. The value should
    #                                          TQConverter.ALL, TQConverter.CCT_ONLY, or TQConverter.EMPTY_ONLY.
    # @return: void
    def generateRuleTemplates(self, parsedQuestions, ruleTemplates, method=ALL):
        methodName = "TQConverter.generateRuleTemplates"

        newRuleCount = 0

        for qJson in parsedQuestions:
            self.isValidQJson(qJson)

            if qJson[T.validK] != "T":
                Logger.cPrint(Logger.ERROR_TYPE, methodName
                              , f"Cannot generate rule template. Invalid JSON structure. "
                              + f"The question annotation is skipped. Annotation: {qJson}")
                continue

            # [SC] generate a rule for each type
            for parsedTypeObj in qJson[T.cctransK][T.typesK]:
                # [SC] extract the cct expression if it already exists
                rhsStr = ""
                if T.cctK in parsedTypeObj:
                    rhsStr = "".join(parsedTypeObj[T.cctK].split())

                # [SC] skip if only empty types should be used
                #       but the type already has cct
                if rhsStr and method == TQConverter.EMPTY_ONLY:
                    continue

                # [SC] skip if only types with annotated cct should be used
                #       but the type does not have cct
                if not rhsStr and method == TQConverter.CCT_ONLY:
                    continue

                # [SC] generate a LHS of a new rule
                newLhs = self.createLhs(parsedTypeObj, qJson)

                # [SC] generate the new rule
                ruleId = len(ruleTemplates) + 1
                if method == TQConverter.EMPTY_ONLY:
                    ruleId = f"Template-{ruleId}"
                newRule = {T.idK: ruleId
                             , T.descrK: qJson[T.questionK]
                             , T.lhsK: newLhs, T.rhsK: rhsStr}

                # [SC] make sure a rule with the same LHS does not already exist
                if self.addNewRule(newRule, ruleTemplates):
                    newRuleCount += 1

        Logger.cPrint(Logger.INFO_TYPE, methodName
                      , f"Generated {newRuleCount} new templates/rules. "
                        + f"Total of {len(ruleTemplates)} templates/rules in the list.")

    # [SC] Adds a new rule to the existing list of rules. Checks for duplicates and inconsistencies beforehand.
    # @param:   dictionary  newRule         The new rule to be added.
    # @param:   list        existingRules   A list of existing rules.
    # @return:  boolean     True if the new rule was successfully added. False otherwise.
    def addNewRule(self, newRule, existingRules):
        methodName = "TQConverter.addNewRule"

        duplicateRule = None
        for rule in existingRules:
            if self.sameLHS(rule[T.lhsK], newRule[T.lhsK]):
                duplicateRule = rule
                break

        if duplicateRule:
            # Logger.cPrint(Logger.WARNING_TYPE, methodName
            #               , f"Duplicate rule:"
            #               + f"\n\tnew rule: {json.dumps(newRule, indent=4)}"
            #               + f"\n\told rule: {json.dumps(duplicateRule, indent=4)}\n.")
            if not duplicateRule[T.rhsK] and newRule[T.rhsK]:
                duplicateRule[T.rhsK] = "".join(newRule[T.rhsK].split())
                Logger.cPrint(Logger.WARNING_TYPE, methodName
                              , f"Transfered RHS from the new to the old rule:"
                              + f"\nnew rule: {json.dumps(newRule, indent=4)}"
                              + f"\nold rule: {json.dumps(duplicateRule, indent=4)}\n.")
            elif duplicateRule[T.rhsK] and newRule[T.rhsK] \
                    and "".join(duplicateRule[T.rhsK].split()) != "".join(newRule[T.rhsK].split()):
                Logger.cPrint(Logger.WARNING_TYPE, methodName
                              , f"Inconsistent RHS found:"
                              + f"\nnew rule: {json.dumps(newRule, indent=4)}"
                              + f"\nold rule: {json.dumps(duplicateRule, indent=4)}\n.")
            return False
        else:
            existingRules.append(newRule)
            return True

    # [SC] Derives news rules from the rules in 'existingRules' based on subtypes of input types.
    #       The new rules are added to 'existingRules'.
    # @param    list    existingRules   List of existing rules from which to derive the new rules.
    # @return:  void
    def expandRulesByInputTypeHiearchy(self, existingRules):
        methodName = "TQConverter.expandRulesByInputTypeHiearchy"

        if not TQConverter.hConceptHierarchy:
            Logger.cPrint(Logger.ERROR_TYPE, methodName
                          , f"Cannot derive new rules. The concept hierarchy was not loaded.")
            return

        if not existingRules:
            Logger.cPrint(Logger.ERROR_TYPE, methodName
                          , f"Cannot derive new rules. Empty list of existing rules.")
            return

        # [SC] this list will temporarily contain new rules before they added to the master list
        newRules = []

        for rule in existingRules:
            lhsObj = rule[T.lhsK]

            if T.inputTypeK not in lhsObj:
                continue

            # [SC] generate a list of subtypes for each input type
            subTypeLists = []
            for mtype in lhsObj[T.inputTypeK]:
                typeObj = TQConverter.hConceptHierarchy[mtype]
                subTypes = [mtype]
                subTypes.extend(typeObj.getAllChildrenStr())
                subTypeLists.append(subTypes)

            # [SC] generate all combination of input types based on subtypes
            # [SC] note that duplicates such as [A,B] and [B,A] are possible
            inputTypeCombos = []
            self.getAllCombos(inputTypeCombos, [], 0, subTypeLists)

            # [SC] generate a new rule for each combination of subtypes
            for index in range(len(inputTypeCombos)):
                newRule = self.cloneRule(rule)
                newRule[T.lhsK][T.inputTypeK] = inputTypeCombos[index]
                newRule[T.idK] = f"{newRule[T.idK]}-IT{index}"
                newRule[T.descrK] = "Derived based on inputType subtypes"
                newRules.append(newRule)

        # [SC] before adding each new rule make sure a rule with the same LHS does not already exist
        # [SC] also ignores duplicates from 'inputTypeCombos'
        newRulesAdded = 0
        for newRule in newRules:
            if self.addNewRule(newRule, existingRules):
                newRulesAdded += 1

        Logger.cPrint(Logger.INFO_TYPE, methodName
                      , f"{newRulesAdded} new rules were derived. "
                        + f"Total of {len(existingRules)} rules in the list.")

    # [SC] Derives news rules from the rules in 'existingRules' based on supertypes of measurement levels.
    #      The new rules are added to 'existingRules'.
    # [H] It is assumed that the measurement level in the question parsing result is the most specific measurement possible.
    # @param    list    existingRules   List of existing rules from which to derive the new rules.
    # @return:  void
    def expandRulesByMeasureHiearchy(self, existingRules):
        methodName = "TQConverter.expandRulesByMeasureHiearchy"

        # regExp = re.escape("R\(\s*(?<rOneOne>[^*,)\s]+)\s*(\*\s*(?<rOneTwo>[^*,)\s]+)\s*)?,"
        #                     + "\s*(?<rTwoOne>[^*,)\s]+)\s*(\*\s*(?<rTwoTwo>[^*,)\s]+)\s*)?\)")

        if not TQConverter.measureHierarchy:
            Logger.cPrint(Logger.ERROR_TYPE, methodName
                          , f"Cannot derive new rules. The measure hierarchy was not loaded.")
            return

        if not TQConverter.measureHierarchyCct:
            Logger.cPrint(Logger.ERROR_TYPE, methodName
                          , f"Cannot derive new rules. The cct measure hierarchy was not loaded.")
            return

        if not existingRules:
            Logger.cPrint(Logger.ERROR_TYPE, methodName
                          , f"Cannot derive new rules. Empty list of existing rules.")
            return

        # [SC] this list will temporarily contain new rules before they added to the master list
        newRules = []

        for rule in existingRules:
            lhsObj = rule[T.lhsK]
            currCCT = None

            if T.measureK not in lhsObj:
                continue

            if lhsObj[T.measureK] not in TQConverter.measureHierarchy:
                Logger.cPrint(Logger.WARNING_TYPE, methodName
                              , f"Rule with 'id={rule[T.idK]}' has unrecognized measure '{lhsObj[T.measureK]}'. "
                                + "This rule is skipped.")
                continue

            if T.rhsK not in rule:
                Logger.cPrint(Logger.WARNING_TYPE, methodName
                              , f"Rule with 'id={rule[T.idK]}' does not have RHS. This rule is skipped.")
                continue

            if not rule[T.rhsK]:
                Logger.cPrint(Logger.WARNING_TYPE, methodName
                              , f"Rule with 'id={rule[T.idK]}' has empty RHS value. This rule is skipped.")
                continue

            # [SC] get the cct value (e.g., Nom, or Ratio) from the RHS cct expression of the base rule's measurement level
            #      it later will be used to change the cct expression according to the new measurement type
            for measObj in TQConverter.measureHierarchyCct.values():
                if rule[T.rhsK].find(measObj.conceptStr) != -1:
                    currCCT = measObj
                    break

            if not currCCT:
                Logger.cPrint(Logger.WARNING_TYPE, methodName
                              , f"Cannot identify measure in RHS '{rule[T.rhsK]}' of rule with 'id={rule[T.idK]}'. "
                                + "This rule is skipped.")
                continue

            # [SC] generate a list of supertypes for the measurement level
            supTypeLists = TQConverter.measureHierarchy[lhsObj[T.measureK]].getAllParentsStr()

            # [SC] generate a new rule for each subtypes
            for index in range(len(supTypeLists)):
                newRule = self.cloneRule(rule)
                newRule[T.lhsK][T.measureK] = supTypeLists[index]
                newRule[T.idK] = f"{newRule[T.idK]}-SuperML{index}"
                newRule[T.descrK] = "Derived based on measureLevel supertypes"

                # [SC] get the cct value (e.g., Nom, or Ratio) of the new rule's measurement level
                newCCT = TQConverter.measureHierarchyCct[TQConverter.measureHierarchy[supTypeLists[index]].cctStr]

                # [SC] update the RHS expression in the new rule
                if newCCT == currCCT:
                    newRules.append(newRule)
                elif newCCT.hasParent(currCCT.conceptStr):
                    newRules.append(newRule)
                elif newCCT.hasChild(currCCT.conceptStr):
                    newRule[T.rhsK] = rule[T.rhsK].replace(currCCT.conceptStr, newCCT.conceptStr)
                    newRules.append(newRule)
                else:
                    Logger.cPrint(Logger.WARNING_TYPE, methodName
                                  , f"Cannot derive a new rule with measurement level '{supTypeLists[index]}' \
                                    from the base rule 'id={rule[T.idK]}'. \
                                    Undefined relation between '{newCCT.conceptStr}' and '{currCCT.conceptStr}'.")

        # [SC] before adding each new rule make sure a rule with the same LHS does not already exist
        newRulesAdded = 0
        for newRule in newRules:
            if self.addNewRule(newRule, existingRules):
                newRulesAdded += 1

        Logger.cPrint(Logger.INFO_TYPE, methodName
                      , f"{newRulesAdded} new rules were derived. "
                      + f"Total of {len(existingRules)} rules in the list.")

    # [SC] Creates and returns a deep copy of a given rule.
    # @param:   dictionary  rule    The rule to be cloned.
    # @return:  dictionary          The deep copy rule.
    def cloneRule(self, rule):
        methodName = "TQConverter.cloneRule"

        clonedRule = {T.idK: rule[T.idK],
                      T.descrK: rule[T.descrK],
                      T.lhsK: {},
                      T.rhsK: rule[T.rhsK]}

        clonedRule[T.lhsK][T.typeK] = rule[T.lhsK][T.typeK]

        if T.measureK in rule[T.lhsK]:
            clonedRule[T.lhsK][T.measureK] = rule[T.lhsK][T.measureK]

        if T.keyK in rule[T.lhsK]:
            clonedRule[T.lhsK][T.keyK] = rule[T.lhsK][T.keyK]

        if T.inputTypeK in rule[T.lhsK]:
            clonedRule[T.lhsK][T.inputTypeK] = []
            for type in rule[T.lhsK][T.inputTypeK]:
                clonedRule[T.lhsK][T.inputTypeK].append(type)

        return clonedRule

    # [SC] Creates all possible combbinations of inputs types. All combos are added to 'allCombos' list.
    #       Note that [A,B] and [B,A] are considered as different combos.
    # @param:   list        allCombos       A list of lists. Each nested list is a combo of input types.
    # @param:   list        inputTypes      Contains the current combo of input types being created.
    # @param:   list        subTypeLists    A list of lists. Each nested list coressponds to one input
    #                                       and contains legible subtypes for that input.
    # @param:   integer     index           Index of a list in 'subTypeLists' that is being currently used
    #                                       to create a combo in 'inputTypes'.
    # @return:  void
    def getAllCombos(self, allCombos, inputTypes, index, subTypeLists):
        methodName = "TQConverter.getAllCombos"

        for type in subTypeLists[index]:
            cloneInputTypes = list(inputTypes)
            cloneInputTypes.append(type)
            if index < len(subTypeLists) - 1:
                self.getAllCombos(allCombos, cloneInputTypes, index + 1, subTypeLists)
            else:
                allCombos.append(cloneInputTypes)

    # [SC] annotates question's cctrans types with algebra expressions
    # @param:  dictionary  qJson   A JSON object of the question annotation.
    # @return: void
    def typesToCCT(self, qJson):
        # [SC][TODO] check if the rules were loaded
        # [SC][TODO] make sure every type is annotated with cct before returning True

        methodName = "TQConverter.typesToCCT"

        if T.validK not in qJson:
            self.isValidQJson(qJson)

        if qJson[T.validK] != "T":
            Logger.cPrint(Logger.ERROR_TYPE, methodName
                          , f"Cannot generate '{T.cctK}' for {qJson}. Invalid JSON structure.")
            qJson.pop(T.validK)
            return False
        qJson.pop(T.validK)

        # [SC] sanity check
        if not self.isRulesLoaded():
            Logger.cPrint(Logger.ERROR_TYPE, methodName
                          , f"Rules for annotating with algebra expressions are not loaded.")
            return False
        if not self.isConsistentRules():
            Logger.cPrint(Logger.ERROR_TYPE, methodName
                          , f"Rules for annotating with algebra expressions are not consistent.")
            return False

        # [SC] iterate through the question types
        for parsedTypeObj in qJson[T.cctransK][T.typesK]:
            # [SC] create LHS object for the question type and compare it with rules' LHSs
            tempLhs = self.createLhs(parsedTypeObj, qJson)

            annotatedF = False
            # [SC] iterate through the rules
            for convRule in TQConverter.convRules:
                if self.sameLHS(tempLhs, convRule[T.lhsK]):
                    # [SC] matching rule; add annotate with the algebra expression
                    parsedTypeObj[T.cctK] = convRule[T.rhsK]
                    annotatedF = True
                    break

            if not annotatedF:
                Logger.cPrint(Logger.WARNING_TYPE, methodName
                              , f"No matching rule to annotate '{parsedTypeObj}' in '{qJson[T.questionK]}'.")

        for parsedTypeObj in qJson[T.cctransK][T.typesK]:
            if T.cctK not in parsedTypeObj:
                Logger.cPrint(Logger.ERROR_TYPE, methodName
                              , f"'Not all types were annotated with algebra expression for '{qJson[T.questionK]}'.")
                return False

        return True

    # [SC] generates a JSON query based on 'cctrans' and 'cct'
    # @param:  dictionary   qJson       A JSON object of the question annotation.
    # @param:  boolean      validate    It True the question annotation is checked for a valid structure.
    # @param:  boolean      annotate    If True the types are annotated with 'cct' expressions.
    # @return: void                     adds 'query' object to qJson
    def cctToQuery(self, qJson, validate, annotate):
        methodName = "TQConverter.cctToQuery"

        if validate:
            self.isValidQJson(qJson)
            if qJson[T.validK] != "T":
                Logger.cPrint(Logger.ERROR_TYPE, methodName
                              , f"Cannot generate query for {qJson}. Invalid JSON structure.")
                qJson.pop(T.validK)
                return
            qJson.pop(T.validK)

        if annotate:
            # [SC] sanity check
            if not self.typesToCCT(qJson):
                Logger.cPrint(Logger.ERROR_TYPE, methodName
                              , f"Cannot generate query for '{qJson[T.questionK]}'. Not all types are annotated.")
                return

        for typeObj in qJson[T.cctransK][T.typesK]:
            if T.cctK not in typeObj:
                Logger.cPrint(Logger.ERROR_TYPE, methodName
                              , f"Cannot generate query for '{qJson[T.questionK]}'. Not all types are annotated.")
                return

        trans = qJson[T.cctransK][T.transformK]
        types = qJson[T.cctransK][T.typesK]
        # [SC] id of the type that is the final output of the transformations
        rootTypeId = None

        # [SC] this dictionary contains a JSON query block for each type
        # key is a type id and value is a JSON query block
        jsonQueryBlocks = {}
        for typeObj in types:
            jsonQueryBlocks[typeObj[T.idK]] = typeObj[T.cctK]

        # [SC] 1. add to 'jsonQueryBlocks' derived types with '_u' suffix
        # [SC] 2. collect IDs of all derived types
        derivedId = []
        for transObj in trans:
            afterId = transObj[T.afterK][0]
            # [SC] 1. add to 'jsonQueryBlocks' derived types with '_u' suffix
            if afterId not in jsonQueryBlocks.keys():
                afterIdAlias = afterId.replace('_u', '')
                if afterIdAlias in jsonQueryBlocks.keys():
                    jsonQueryBlocks[afterId] = jsonQueryBlocks[afterIdAlias]
                else:
                    jsonQueryBlocks[afterId] = ""
            # [SC] 2. collect IDs of all derived types
            derivedId.append(afterId)
        # [SC] change the list into a set
        derivedId = set(derivedId)

        while derivedId:
            # [SC] create json query parts for each transformation
            # that has its 'before' types has already been derived
            for transObj in trans:
                # [SC] check via intersection if any value in 'before' yet to be derived
                if not set(transObj[T.beforeK]) & derivedId:
                    # [SC] create a query JSON block
                    queryBlock = {
                        T.afterIdK: transObj[T.afterK][0],
                        T.afterK: jsonQueryBlocks[transObj[T.afterK][0]],
                        T.beforeK: []
                    }

                    # [SC] retrieve existing query blocks to construct the before part
                    for beforeId in transObj[T.beforeK]:
                        queryBlock[T.beforeK].append(jsonQueryBlocks[beforeId])

                    # [SC] update the query block dictionary with the new block
                    jsonQueryBlocks[queryBlock[T.afterIdK]] = queryBlock

                    # [SC] the last type to be derived is always the root type
                    if len(derivedId) == 1:
                        rootTypeId = queryBlock[T.afterIdK]

                    # [SC] remove the current type id from the to be derived list
                    derivedId.discard(queryBlock[T.afterIdK])

        # [SC] query block for the root type is always the compelte query
        finalQuery = jsonQueryBlocks[rootTypeId]
        qJson[T.queryK] = finalQuery

    # [SC] generates a JSON query based on 'cctrans' and 'cct'
    # @param:  dictionary   qJson       A JSON object of the question annotation.
    # @param:  boolean      validate    It True the question annotation is checked for a valid structure.
    # @param:  boolean      annotate    If True the types are annotated with 'cct' expressions.
    # @return: void                     adds 'query' object to qJson
    def cctToExpandedQuery(self, qJson, validate, annotate):
        methodName = "TQConverter.cctToExpandedQuery"

        if validate:
            self.isValidQJson(qJson)
            if qJson[T.validK] != "T":
                Logger.cPrint(Logger.ERROR_TYPE, methodName
                              , f"Cannot generate query for {qJson}. Invalid JSON structure.")
                qJson.pop(T.validK)
                return
            qJson.pop(T.validK)

        if annotate:
            # [SC] sanity check
            if not self.typesToCCT(qJson):
                Logger.cPrint(Logger.ERROR_TYPE, methodName
                              , f"Cannot generate query for '{qJson[T.questionK]}'. Not all types are annotated.")
                return

        for typeObj in qJson[T.cctransK][T.typesK]:
            if T.cctK not in typeObj:
                Logger.cPrint(Logger.ERROR_TYPE, methodName
                              , f"Cannot generate query for '{qJson[T.questionK]}'. Not all types are annotated.")
                return

        trans = qJson[T.cctransK][T.transformK]
        types = qJson[T.cctransK][T.typesK]

        # [SC] this dictionary contains a JSON query block for each type
        # key is a type id and value is a JSON query block
        jsonQueryBlocks = {}
        for typeObj in types:
            jsonQueryBlocks[typeObj[T.idK]] = {
                T.afterK: {
                    "id": typeObj[T.idK],
                    "cct": typeObj[T.cctK]
                }
            }

        # [SC] contains all ids that occure in 'before' and 'after' parts
        beforeIdList = []
        afterIdList = []
        # [SC] add 'before' parts to the query blocks
        for transObj in trans:
            outputQueryObj = jsonQueryBlocks[transObj[T.afterK][0]]

            # [SC] add 'before' query object
            beforeQueryObj = []
            for beforeId in transObj[T.beforeK]:
                beforeQueryObj.append(jsonQueryBlocks[beforeId])
            outputQueryObj[T.beforeK] = beforeQueryObj

            # [SC] add 'key' to the query block
            if T.keyK in transObj:
                outputQueryObj[T.afterK][T.keyK] = transObj[T.keyK]

            beforeIdList.extend(transObj[T.beforeK])
            afterIdList.extend(transObj[T.afterK])

        # [SC] find the root; root id is after id that is not among before ids
        for keyVal in jsonQueryBlocks.keys():
            if keyVal not in beforeIdList and keyVal in afterIdList:
                # [SC] query block for the root type is always the compelte query
                qJson[T.queryExK] = jsonQueryBlocks[keyVal]
