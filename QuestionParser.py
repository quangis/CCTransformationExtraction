import re

from spacy.lang.en import English
import en_core_web_sm
from word2number import w2n

from ner import ConceptTypeAnn  # only include core concept recognition, place name and entity are recognized by blockly interface
from geoparser import Geoparser
from transformations import TransformHandler

# [X]  customized a list of stopwords
class CustomEnglishDefaults(English.Defaults):
    # stop_words = set(["is", "are", "was", "were", "do", "does", "did", "have", "had"])
    stop_words = {'do', 'did', 'does', 'a', 'an', 'the', 'their', 'his', 'her', 'my', 'your'}


class CustomEnglish(English):
    lang = "custom_en"
    Defaults = CustomEnglishDefaults


class QuestionParser:
    nlp_en = CustomEnglish()  # [X] Load English stopwords
    nlp = en_core_web_sm.load()

    def __init__(self):
        self.conceptAnnI = ConceptTypeAnn()
        self.geoparserI = Geoparser()
        self.transHandI = TransformHandler()


    # [X] Convert numeric words into digit numbers
    # Input sentence(string): 'What is average network distance for three thousand and five people to
    # two hundred and twelve closest primary schools'.
    # Output sentence(string): 'What is average network distance for 3005 people to 212 closest primary schools'.
    # except for 'five star hotels'
    def word2num(self, sentence):
        try:
            # [SC][TODO] what is five star? why is it hardcoded?
            if 'five star' not in sentence:
                cur_doc = QuestionParser.nlp(sentence)
                numWords = ''
                numDig = ''
                for cur_i in range(0, len(cur_doc)):
                    if cur_doc[cur_i].pos_ == 'NUM':
                        numWords = numWords + ' ' + cur_doc[cur_i].text
                        cur_i += 1
                    elif cur_doc[cur_i].text == 'and' and cur_doc[cur_i - 1].pos_ == 'NUM':
                        numWords = numWords + ' and'
                        cur_i += 1
                    elif numWords and not cur_doc[cur_i].pos_ == 'NUM':
                        numDig = w2n.word_to_num(numWords.strip())
                        # print(numWords)
                        # print(numDig)
                        sentence = sentence.replace(numWords.strip(), str(numDig))
                        numWords = ''
        except:
            return sentence

        return sentence


    def parseQuestionBlock(self, result):
        coreConTrans = {}
        coreTypeDict = {}
        core_id = 0
        result['question'] = ' '.join(result['question'].split())  # remove extra whitespaces in string
        result['replaceQ'] = ' '.join(result['replaceQ'].split()).replace('-', ' ').replace('?', '')

        # [X] loop every key in result and replace keywords with its tag
        for key, value in result.items():
            if (key != 'question' or key != 'replaceQ') and isinstance(value, list) and value:
                for i, item in enumerate(value):
                    if item == 'in':
                        rq_list = result['replaceQ'].split()
                        rq_list[rq_list.index('in')] = key + str(i)
                        result['replaceQ'] = ' '.join(rq_list)
                    else:
                        result['replaceQ'] = result['replaceQ'].replace(item, f"{key}{i}")

        # [X] print entities and placenames
        entity = {}
        for key, value in result.items():
            if (key != 'question' or key != 'replaceQ') and isinstance(value, list) and value:
                entity[key] = result[key]
        # print('entity\n', entity)

        # [X] Cleaning text: remove stopwords and save the tokens in a list
        doc = QuestionParser.nlp_en(result['replaceQ'])
        token_list = []
        for word in doc:
            if not word.is_stop and not word.is_punct or word.text == ',':
                token_list.append(word)
        sen = ' '.join(word.text for word in token_list).strip()  # Question in string without stopwords
        sen_Clean = self.word2num(sen)  # Convert numeric words into digit numbers
        result['replaceQ'] = re.sub('\s+', ' ', sen_Clean).strip()
        # print('replaceQ\n', result['replaceQ'])

        # [X] Identify Core Concepts
        re_CoreCon = self.conceptAnnI.core_concept_match(result['replaceQ'].lower())  # parsed_Entities[1]: sentence
        result.update(re_CoreCon[0])  # re_CoreCon[0]: dictionary - Core Concepts
        result['ner_Question'] = re_CoreCon[1]
        # print('ner_Question\n', result['ner_Question'])
        # print('result\n', result)

        # [X] Generate parser tree
        parsedQuestion = self.geoparserI.geo_parser(result, core_id, coreTypeDict, coreConTrans)
        if parsedQuestion[0]:
            result['parseTreeStr'] = parsedQuestion[0]
        if coreTypeDict and coreConTrans:
            result['cctrans'] = self.transHandI.write_trans(parsedQuestion)
        # print(parsedQuestion)

        return result