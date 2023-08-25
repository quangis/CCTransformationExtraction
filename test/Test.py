## [SC][TODO] ignore loc while deriving new rules based on measures
## [SC][TODO] expand rules based on shared parent concept

import sys
sys.path.append('..')
import json
from QuestionParser import *

# ======================================================================================== #
# ==== [SC] testing parsing

def doOOParserTest(blocklyFile, baseResults, outFile):
    # [SC] parse the blockly outputs
    jsonBlocks = json.load(open(f"../Data/{blocklyFile}"))
    qp = QuestionParser()
    results = []
    for qBlock in jsonBlocks:
        results.append(qp.parseQuestionBlock(qBlock))

    # [SC] store the parse results
    with open(f"output/{outFile}", "w") as outputFile:
            json.dump(results, outputFile, indent=4)

    # [SC] compare the parse results with the base (expected) results
    resultsBase = json.load(open(f"../Data/{baseResults}"))
    for index in range(len(resultsBase)):
        newStr = json.dumps(results[index])
        baseStr = json.dumps(resultsBase[index])
        if not newStr == baseStr:
            print(f"MISMATCH: new: {results[index]['question']}, base: {resultsBase[index]['question']}")

print("============================== TESTING retrieval dataset")
doOOParserTest("blocklyoutput_retri.json", "retri_parser_results.json", "retri_parser_results_test.json")
print("============================== TESTING GeoAnQu dataset")
doOOParserTest("blocklyoutput_GeoAnQu.json", "GeoAnQu_parser_results.json", "geoanqu_parser_results_test.json")
print("============================== TESTING MS student dataset")
doOOParserTest("blocklyoutput_Leticia.json", "Leticia_parser_results.json", "student_parser_results_test.json")


# ======================================================================================== #
# ==== [SC] testing rule generation

from TypesToQueryConverter import *

def testRuleGeneration():
    tqConv = TQConverter()

    rules = []

    # [SC] generate rules from types with manually annotated cct expressions
    for corpusFileName in ["retri_parser_results_0608_cct_update.json", "GeoAnQu_extended_cct_Simon_remquesmark_update.json"]:
        parsedQuestions = json.load(open(f"../manualData/{corpusFileName}"))
        tqConv.generateRuleTemplates(parsedQuestions, rules, method=TQConverter.CCT_ONLY)
    # [SC] expand the rules using the core concept type hiearchy
    tqConv.expandRulesByInputTypeHiearchy(rules)
    # [SC] expand the rules using the measurement hiearchy
    tqConv.expandRulesByMeasureHiearchy(rules)
    # [SC] save the rules
    with open(f"output/conversionRules.json", "w") as outputFile:
        json.dump(rules, outputFile, indent=4)

    # [SC] annotate the question types with cct expressions and generate queries
    corpora = {"GeoAnQu_parser_results.json": "GeoAnQu_parser_results_annotatedCCT.json",
               "retri_parser_results.json": "retri_parser_results_annotatedCCT.json",
                "Leticia_parser_results.json": "Leticia_parser_results_annotatedCCT.json"}
    # [SC] replace default rules with the newly generated rules
    TQConverter.convRules = rules
    # [SC] stores templates rules generated from types which were not annotated with cct expressions
    templateRules = []
    for corpusFileName in corpora.keys():
        print("\n###################################################################################")
        print(f"###### ANNOTATING {corpusFileName}")
        qJsonArray = json.load(open(f"../Data/{corpusFileName}"))

        # [SC] annotate the question types with cct expressions and generate a query
        for qJson in qJsonArray:
            # tqConv.cctToQuery(qJson, validate=True, annotate=True)
            tqConv.cctToExpandedQuery(qJson, validate=True, annotate=True)
        # [SC] save annotated types in a separate file
        with open(f"output/{corpora[corpusFileName]}", "w") as outputFile:
            json.dump(qJsonArray, outputFile, indent=4)

        # [SC] generate template rules from any types that failed to be annotated with cct expression
        tqConv.generateRuleTemplates(qJsonArray, templateRules, method=TQConverter.EMPTY_ONLY)
    # [SC] save template rules into a file
    with open(f"output/templateRules.json", "w") as outputFile:
        json.dump(templateRules, outputFile, indent=4)
#testRuleGeneration()


