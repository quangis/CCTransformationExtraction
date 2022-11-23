from spacy.lang.en import English
import en_core_web_sm
import json
from word2number import w2n
from ner import core_concept_match
from geoparser import geo_parser
from transformations import write_trans

results = []
questionFilepath = 'corpus.txt'
sym = '" ? \n \t'  # remove these symbols from questions

errorQuestionFilePath = 'error.txt'
error_ques = open(errorQuestionFilePath, 'w+')


# [X]  customized a list of stopwords
class CustomEnglishDefaults(English.Defaults):
    # stop_words = set(["is", "are", "was", "were", "do", "does", "did", "have", "had"])
    stop_words = {"do", "did", "does", "a", "an", "the", "their", 'his', 'her', 'my'}


class CustomEnglish(English):
    lang = "custom_en"
    Defaults = CustomEnglishDefaults


nlp_en = CustomEnglish()  # [X] Load English stopwords
nlp = en_core_web_sm.load()


# [X] Convert numeric words into digit numbers
# Input sentence(string): 'What is average network distance for three thousand and five people to
# two hundred and twelve closest primary schools'.
# Output sentence(string): 'What is average network distance for 3005 people to 212 closest primary schools'.
# except for 'five star hotels'
def word2num(sentence):
    try:
        if 'five star' not in sentence:
            cur_doc = nlp(sentence)
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


def readfile(questionFilepath):
    with open(questionFilepath, encoding="utf-8") as questions:
        for question in questions:
            result = {}
            core_id = 0
            coreConTrans = {}  # final cctrans output
            result['question'] = question.strip(sym)
            doc = nlp_en(result['question'])

            # [X] Cleaning text: remove stopwords and save the tokens in a list
            # text = ' '.join([word for word in text if word not in string.punctuation])
            token_list = []
            for word in doc:
                if not word.is_stop and not word.is_punct or word.text == ',':
                    token_list.append(word)
            sen = ' '.join(word.text for word in token_list).strip()  # Question in string without stopwords
            sen_Clean = word2num(sen)  # Convert numeric words into digit numbers
            result['cleaned_Question'] = sen_Clean

            # [X] Identify Placename, Entity, Core Concepts
            re_CoreCon = core_concept_match(sen_Clean)  # parsed_Entities[1]: sentence
            result.update(re_CoreCon[0])  # re_CoreCon[0]: dictionary - Core Concepts
            result['ner_Question'] = re_CoreCon[1]

            #[X] Generate parser tree
            parsedQuestion = geo_parser(result, core_id, coreConTrans)
            if parsedQuestion[0]:
                result['parseTreeStr'] = parsedQuestion[0]
            if parsedQuestion[1] and coreConTrans:
                result['cctrans'] = write_trans(parsedQuestion)
            if parsedQuestion[4]:
                error_ques.write(parsedQuestion[3] + '\n')  # questions can not be parsed in the grammar

            print(parsedQuestion)
            results.append(result)

    with open('parse results.json', 'w') as outputFile:
        json.dump(results, outputFile)
    error_ques.close()



if __name__ == '__main__':
    readfile(questionFilepath)
