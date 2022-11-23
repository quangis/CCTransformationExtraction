# [X] import nlp packages for placename and entities recognition
import en_core_web_sm
from spacy.matcher import PhraseMatcher
import nltk
import nltk.tokenize as nt
from allennlp.predictors.predictor import Predictor  # For using ELMo-based NER & Fine Grained NER

predictorELMo = Predictor.from_path(
    "https://storage.googleapis.com/allennlp-public-models/ner-elmo.2021-02-12.tar.gz")  # Allennlp Elmo-based NER

pos = []
units = {'db', 'dB', 'decibel', 'meters'}
humanWords = {'people', 'population', 'children'}
compR = ['lower than', 'larger than', 'at least', 'less than', 'more than', 'greater than',
             'greater than or equal to', 'smaller than', 'equal to']
cn = {'least cost route', 'least cost path', 'least costly route', 'least costly path', 'driving time',
          'high school students', 'senior high schools',
          'travel time', 'forest areas', 'for sale', 'open at', 'shortest network based paths', 'tram station',
          'tram stations', 'senior high school district',
          'hot spots and cold spots', 'shortest path', 'cesium 137 concentration', 'PM2.5 concentration',
          'potentially deforested areas'}
removeWords = {'what', 'where', 'which', 'how', 'for', 'each', 'when', 'who', 'why', 'new', 'no', 'similar',
                   'nearest', 'most', 'to', 'at', 'low', 'high', 'aged'}


# Read place type for place NER
ptypePath = 'Dictionary/place_type.txt'
pt_set = set(line.strip() for line in open(ptypePath, encoding="utf-8"))


# [X] Read Core concepts.txt into a dictionary.
def load_ccdict(filePath):
    coreCon = {}
    text = []
    tag = []
    meaLevel = []  # measurement level
    with open(filePath, encoding="utf-8") as coreConcepts:
        for line in coreConcepts:
            cur = line.strip().split('\t')
            text.append(cur[0].lower())
            tag.append(cur[1].lower())
            if len(cur) == 3:
                meaLevel.append(cur[2].lower())
            else:
                meaLevel.append('NULL')
    coreCon['text'] = text
    coreCon['tag'] = tag
    coreCon['measureLevel'] = meaLevel

    return coreCon

corePath = 'Dictionary/coreConceptsML.txt'
networkPath = 'Dictionary/network.txt'
coreCon_dict = load_ccdict(corePath)
networkSet = set(l.strip() for l in open(networkPath, encoding="utf-8"))


# load en_core_web_sm of English for NER, noun chunks
nlp = en_core_web_sm.load()
matcher = PhraseMatcher(nlp.vocab)  # add noun phrases when doing noun_chunks
patterns = [nlp('bus stops'), nlp('driving time'), nlp('grid cell'), nlp('grid cells'), nlp('off street paths'),
            nlp('mean direction'), nlp('degree of clustering'), nlp('degree of dispersion'), nlp('fire call'),
            nlp('fire calls'), nlp('slope'), nlp('wetlands'), nlp('house totals'), nlp('fire hydrant'),
            nlp('fire scene'), nlp('fire scenes'), nlp('walkability'), nlp('owner occupied houses'),
            nlp('temperature in celsius'), nlp('police beat'), nlp('police beats'), nlp('mean center'),
            nlp('tornado touchdowns'), nlp('nurse practitioner services'), nlp('priority rankings'),
            nlp('tram stations'), nlp('tram station'), nlp('plumbing'), nlp('political leaning'),
            nlp('predicted probability surface'), nlp('fire accidents'), nlp('for sale'), nlp('open at'),
            nlp('predicted distribution probability'), nlp('senior high schools'), nlp('floodplain'),
            nlp('income of households'), nlp('interpolated surface'), nlp('average cost per acre'),
            nlp('high school students'), nlp('wind farm proposals'), nlp('planned commercial district'),
            nlp('protected region'), nlp('pc4 area'), nlp('aspect'), nlp('monthly rainfall'),
            nlp('hot spots and cold spots'), nlp('ski pistes'), nlp('outpatient services'),
            nlp('per household online loan application rates'), nlp('windsurfing spot'), nlp('accident'),
            nlp('census tract'), nlp('mean annual PM 2.5 concentration'), nlp('PM 2.5 concentration'),
            nlp('cesium 137 concentration'), nlp('aquifer')]
# phrases missed by noun_chunks, add manually
matcher.add("PHRASES", patterns)


def is_left_inside(string, list):
    cur_list = []
    for l in list:
        if l.lower().strip().startswith(string):
            cur_list.append(l)
    return cur_list

# [X] Identify Place names(e.g., ) in questions
# input string sentence:
# 'What buildings are within 1 minute of driving time from a fire station for
# Multifunctional Urban Area in Fort Worth in US
# output tuple:
# (['Multifunctional Urban Area', 'Fort Worth', 'US'],
# 'What buildings are within 1 minute of driving time from a fire station
# for each PlaceName0 in PlaceName1 in PlaceName3')
def place_ner(sentence):
    pred = predictorELMo.predict(sentence)

    PlaceName = []
    loc = 0
    for i in range(0, len(pred['tags'])):
        # place name is a single word, such as Utrecht
        # unsolved question: Which urban areas are within 150 miles of the Ogallala aquifer, have precipitation lower than 10 inches, and intersect with the irrigation regions in Ogallala (High Plains) Aquifer, US
        if pred['tags'][i] == 'U-LOC' or pred['tags'][i] == 'U-PER':
            if not pred['words'][i] == 'PC4':
                PlaceName.append(pred['words'][i])
                sentence = sentence.replace(pred['words'][i], 'PlaceName' + str(loc))
                loc += 1
        elif pred['tags'][i] == 'B-LOC':  # When place name is a phrase, such as Happy Valley
            place = pred['words'][i]
        elif pred['tags'][i] == 'I-LOC' or pred['tags'][i] == 'L-LOC':
            place = place + ' ' + pred['words'][i]
            if i + 1 == len(pred['tags']):
                PlaceName.append(place)
                sentence = sentence.replace(place, 'PlaceName' + str(loc))
                place = ''
            elif pred['tags'][i + 1] == 'O':  # 'O' not a place name
                PlaceName.append(place)
                sentence = sentence.replace(place, 'PlaceName' + str(loc))
                loc += 1
                place = ''

    #  allennlp fail to capture Oleander as city name
    cur_words2 = sentence.strip().split(' ')
    if 'Oleander' in cur_words2:
        sentence = sentence.replace('Oleander', 'PlaceName' + str(len(PlaceName)))
        PlaceName.append('Oleander')

    # Solve place name + place type, such as PlaceName0 area(PC4 area) -> PlaceName0(PC4 area)...
    cur_words = sentence.strip().split(' ')
    for i in range(0, len(cur_words)):
        if cur_words[i].startswith('PlaceName'):
            if i + 1 < len(cur_words):
                if not len(is_left_inside(cur_words[i + 1],
                                          pt_set)) == 0:  # PlaceName0 ski resort(Happy Valley ski resort) -> PlaceName0
                    if i + 2 < len(cur_words):
                        cur_pt = cur_words[i + 1] + ' ' + cur_words[i + 2]
                        if cur_pt in is_left_inside(cur_words[i + 1], pt_set):
                            cur_index = int(cur_words[i][9:])  # PlaceName0 -> 0
                            PlaceName[cur_index] = PlaceName[cur_index] + ' ' + cur_pt
                            sentence = sentence.replace(' ' + cur_pt, '')
                        elif i + 3 < len(cur_words):
                            cur_pt = ' '.join(cur_words[i + 1:i + 4])
                            if cur_pt in is_left_inside(cur_words[i + 1], pt_set):
                                cur_index = int(cur_words[i][9:])
                                PlaceName[cur_index] = PlaceName[cur_index] + ' ' + cur_pt
                                sentence = sentence.replace(' ' + cur_pt, '')
                            elif cur_words[i + 1] in pt_set:
                                cur_index = int(cur_words[i][9:])
                                PlaceName[cur_index] = PlaceName[cur_index] + ' ' + cur_words[i + 1]
                                sentence = sentence.replace(' '.join(cur_words[i:i + 2]), cur_words[i])
                elif cur_words[i + 1] in pt_set:  # PlaceName0(Happy Valley) resort -> PlaceName0(Happy Valley resort)
                    cur_index = int(cur_words[i][9:])  # PlaceName0 -> 0
                    PlaceName[cur_index] = PlaceName[cur_index] + ' ' + cur_words[i + 1]
                    sentence = sentence.replace(' '.join(cur_words[i:i + 2]), cur_words[i])

    # print(sentence)
    # print(PlaceName)
    return PlaceName, sentence

# [X] Identify Date, Time, Quantity, Percent
# input string sentence:
# 'What buildings are within 1 minute, 2 minutes and 3 minutes of driving time from 3 fire stations that are
# within 60 meters of rivers and located at areas that has slope larger than 10 percent for each PlaceName1 in
# PlaceName2 between 1990 and 2000'
# output tuple:
# ({'Time': [1 minute, 2 minutes, 3 minutes], 'Quantity': [60 meters],
# 'Percent': [larger than 10 percent], 'Date': [between 1990 and 2000]},
# 'What buildings are within ETime0, ETime1, and ETime2 of driving time from 3 fire stations that are within
# EQuantity0 of rivers and located at areas that has slope EPercent1 for each PlaceName0 in PlaceName1 EDate0')
def entity_ner(sentence):
    entities = []
    enti_dict = {}
    Date = []
    Time = []
    Quantity = []
    Percent = []

    cur_sen = ''
    if 'each' in sentence:  # {'Quantity': [each 50 square km]} -> {'Quantity': [50 square km]}
        cur_sen = sentence.replace(' each', '')
    else:
        cur_sen = sentence

    cur_doc = nlp(cur_sen)
    # entities = [(i.text, i.label_) for i in cur_doc.ents]
    # e.g., tuple entities = [(1 minute, 'TIME'), (between 1990 and 2000, 'DATE')]
    # remove compareR from entities. [('larger than 15 percent', 'PERCENT')] -> [('15 percent', 'PERCENT')]
    for i in cur_doc.ents:
        compBool = [word in i.text for word in compR]
        if True in compBool:
            tin = compBool.index(True)
            en_text = i.text.replace(compR[tin] + ' ', '')
            entities.append((en_text, i.label_))
        else:
            ilist = i.text.split(' ')
            if ilist[-1] == 'by':
                entities.append((i.text.replace(' by', ''), i.label_))
            else:
                entities.append((i.text, i.label_))

    # print(entities)

    D_loc = 0
    T_loc = 0
    Q_loc = 0
    P_loc = 0

    cardinal_sen = sentence.strip().split(' ')
    for i in range(0, len(entities)):
        if entities[i][1] == 'TIME':
            Time.append(entities[i][0])
            sentence = sentence.replace(entities[i][0], 'ETime' + str(T_loc))
            T_loc += 1
        elif entities[i][1] == 'QUANTITY':
            Quantity.append(entities[i][0])
            sentence = sentence.replace(entities[i][0], 'EQuantity' + str(Q_loc))
            Q_loc += 1
        elif entities[i][1] == 'CARDINAL' and entities[i][0].isnumeric() and cardinal_sen.index(
                entities[i][0]) + 1 < len(cardinal_sen) and \
                cardinal_sen[cardinal_sen.index(entities[i][0]) + 1] in units:  # 70 db
            quan_words = entities[i][0] + ' ' + cardinal_sen[cardinal_sen.index(entities[i][0]) + 1]
            Quantity.append(quan_words)
            sentence = sentence.replace(quan_words, 'EQuantity' + str(Q_loc))
            Q_loc += 1
        elif entities[i][1] == 'CARDINAL' and any(
                x in entities[i][0].split(' ') for x in units):  # [('between 700 and 2000 meters', 'CARDINAL')]
            Quantity.append(entities[i][0])
            sentence = sentence.replace(entities[i][0], 'EQuantity' + str(Q_loc))
            Q_loc += 1
        elif entities[i][1] == 'PERCENT':
            Percent.append(entities[i][0])
            sentence = sentence.replace(entities[i][0], 'EPercent' + str(P_loc))
            P_loc += 1
        elif entities[i][1] == 'DATE' and not entities[i][0] == 'annual' and not entities[i][0] == 'monthly' \
                and not entities[i][0].startswith('PlaceName'):
            Date.append(entities[i][0])
            sentence = sentence.replace(entities[i][0], 'EDate' + str(D_loc))
            D_loc += 1

    cur_w = sentence.strip().split(' ')
    cur_quan = ''
    for w in cur_w:
        if w.startswith('meter') or w.startswith('millimeter'):
            cur_quan = cur_w[cur_w.index(w) - 1] + ' ' + w
            Quantity.append(cur_quan)
            sentence = sentence.replace(cur_quan, 'EQuantity' + str(Q_loc))
            Q_loc += 1
        elif w.isnumeric() and cur_w.index(w) < len(cur_w) - 3 and cur_w[cur_w.index(w) + 1] == 'per' and cur_w[
            cur_w.index(w) + 2] == 'square' and cur_w[cur_w.index(w) + 3].startswith(
            'kilometer'):  # 300 per square kilometer
            cur_quan = w + ' per square ' + cur_w[cur_w.index(w) + 3]
            Quantity.append(cur_quan)
            sentence = sentence.replace(cur_quan, 'EQuantity' + str(Q_loc))
            Q_loc += 1
        elif w == 'per' and cur_w.index(w) < len(cur_w) - 3 and cur_w[cur_w.index(w) - 1].isnumeric() and cur_w[
            cur_w.index(w) + 1].isnumeric():  # 500 per 1000000 people
            cur_quan = ' '.join(cur_w[cur_w.index(w) - 1: cur_w.index(w) + 3])
            Quantity.append(cur_quan)
            sentence = sentence.replace(cur_quan, 'EQuantity' + str(Q_loc))
            Q_loc += 1
        elif w.isnumeric() and cur_w[int(cur_w.index(w) - 1)] == 'over' and cur_w[
            int(cur_w.index(w) - 2)] in humanWords:
            Date.append('over ' + w)
            sentence = sentence.replace('over ' + w, 'EDate' + str(D_loc))
            D_loc += 1
        elif w.isnumeric() and cur_w[int(cur_w.index(w) - 1)] == 'than' and cur_w[
            int(cur_w.index(w) - 3)] in humanWords:
            cur_date = ' '.join(cur_w[cur_w.index(w) - 2: cur_w.index(w) + 1])
            Date.append(cur_date)
            sentence = sentence.replace(cur_date, 'EDate' + str(D_loc))
            D_loc += 1

    cur_words = sentence.strip().split(' ')
    if not len(Time) == 0:
        enti_dict['time'] = Time
    if not len(Quantity) == 0:
        for w in cur_words:
            if w.startswith('EQuantity'):
                i = cur_words.index(w)
                if cur_words[i - 1] == 'by' and cur_words[
                    i - 2].isnumeric():  # 2 by Quantity0(2 km) grid cell -> Quantity0 grid cell
                    Quantity[int(w[9])] = ' '.join(cur_words[i - 2:i]) + ' ' + Quantity[int(w[9])]
                    sentence = sentence.replace(' '.join(cur_words[i - 2:i]) + ' ' + w, w)
                    enti_dict['quantity'] = Quantity
                elif cur_words[i - 1] == 'from':  # from Quantity0(60 to 600 meters) -> Quantity0
                    Quantity[int(w[9])] = 'from ' + Quantity[int(w[9])]
                    sentence = sentence.replace('from ' + w, w)
                    enti_dict['quantity'] = Quantity
                elif cur_words[i - 1] == 'to' and cur_words[i - 2].isnumeric() and cur_words[
                    i - 3] == 'from':  # from 300 to Quantity0(900 meters) -> Quantity0
                    Quantity[int(w[9])] = ' '.join(cur_words[i - 3:i]) + ' ' + Quantity[int(w[9])]
                    sentence = sentence.replace(' '.join(cur_words[i - 3:i]) + ' ' + w, w)
                    enti_dict['quantity'] = Quantity
                elif cur_words[i - 1] == 'and' and cur_words[i - 2].isnumeric() and cur_words[
                    i - 3] == 'between':  # between 700 and Quantity0(2000 meters) -> Quantity0
                    Quantity[int(w[9])] = ' '.join(cur_words[i - 3:i]) + ' ' + Quantity[int(w[9])]
                    sentence = sentence.replace(' '.join(cur_words[i - 3:i]) + ' ' + w, w)
                    enti_dict['quantity'] = Quantity
                elif cur_words[i + 1] == 'per' and cur_words[i + 2] == 'second':
                    Quantity[int(w[9])] = Quantity[int(w[9])] + ' ' + ' '.join(cur_words[i + 1:i + 3])
                else:
                    enti_dict['quantity'] = Quantity
    if not len(Percent) == 0:
        enti_dict['percent'] = Percent
    if not len(Date) == 0:
        for w in cur_words:
            if w.startswith('EDate'):
                i = cur_words.index(w)
                if cur_words[i - 2].isnumeric() and cur_words[i - 1] == 'to':  # from 2000 to Date0 -> Date0
                    Date[int(w[5])] = ' '.join(cur_words[i - 3:i]) + ' ' + Date[int(w[5])]
                    sentence = sentence.replace(' '.join(cur_words[i - 3:i]) + ' ' + w, w)
                    enti_dict['date'] = Date
                elif i + 2 < len(cur_words) and cur_words[i + 2].isnumeric() and cur_words[
                    i + 1] == 'to':  # from Date0 to 1994
                    Date[int(w[5])] = cur_words[i - 1] + ' ' + Date[int(w[5])] + ' ' + ' '.join(cur_words[i + 1:i + 3])
                    sentence = sentence.replace(cur_words[i - 1] + ' ' + w + ' ' + ' '.join(cur_words[i + 1:i + 3]), w)
                    enti_dict['date'] = Date
                elif cur_words[i - 1] == 'from' and i + 1 == len(cur_words):  # from Date0 (1997 to 2004)
                    Date[int(w[5])] = 'from ' + Date[int(w[5])]
                    sentence = sentence.replace('from ' + w, w)
                    enti_dict['date'] = Date
                elif cur_words[i - 1] == 'from' and i + 1 < len(cur_words) and not cur_words[
                                                                                       i + 1] == 'to':  # from Date0 (1997 to 2004) in Utrecht
                    Date[int(w[5])] = 'from ' + Date[int(w[5])]
                    sentence = sentence.replace('from ' + w, w)
                    enti_dict['date'] = Date
                elif cur_words[i - 1] == 'from' and cur_words[i + 1] == 'to' and cur_words[i + 2].startswith(
                        'Date') and i + 2 < len(cur_words):  # from date0 to date1 -> date0
                    Date[int(w[5])] = 'from ' + Date[int(w[5])] + ' to ' + Date[int(cur_words[i + 2][5])]
                    Date.remove(Date[int(cur_words[i + 2][5])])
                    sentence = sentence.replace('from ' + w + ' to ' + cur_words[i + 2], w)
                    enti_dict['date'] = Date
                elif cur_words[i - 1] == 'over':  # over 65 years
                    Date[int(w[5])] = 'over ' + Date[int(w[5])]
                    sentence = sentence.replace('over ' + w, w)
                    enti_dict['date'] = Date
                else:
                    enti_dict['date'] = Date

    # print(enti_dict)
    # print(sentence)

    return enti_dict, sentence

# [X] Clean noun_phrases after noun chunks recognition, remove superlatives and comparatives, placenames, entities...
def noun_phrases_correct(noun_phrases_list):
    noun_phrases_CleanList = []

    for cur_noun in noun_phrases_list:
        if 'each' in cur_noun:
            cur_noun = cur_noun.replace('each ', '')
        if cur_noun in cn:
            noun_phrases_CleanList.append(cur_noun)
            # print('noun_phrases_CleanList:', noun_phrases_CleanList)
        else:
            cur_p = nt.sent_tokenize(cur_noun)
            tokenized_sen = [nt.word_tokenize(p) for p in cur_p]  # [['nearest', 'supermarket']]
            if (any('area' in m for m in tokenized_sen[0]) and not any(
                    'equantity' in n for n in tokenized_sen[0])) or not any(
                    'area' in m for m in tokenized_sen[0]):  # remove 'equantity0 area of road'
                cur_pos = [nltk.pos_tag(cur_sen) for cur_sen in tokenized_sen][
                    0]  # [('nearest', 'JJS'), ('supermarket', 'NN')]
                for e in cur_pos:
                    pos.append(e)
                res = [sub[0] for sub in cur_pos if
                       ('JJS' in sub[1] and not sub[0] == 'west') or 'JJR' in sub[1] or 'RBS' in sub[1] or 'RBR' in sub[
                           1]]  # ['longest', 'more', 'most']

                if 'most' in res or 'more' in res:  # most intense, also remove intense; more than, also remove than
                    mostIndex = [cur_pos.index(sub) for sub in cur_pos if sub[0] == 'most' or sub[0] == 'more']
                    nextIndex = mostIndex[0] + 1
                    if cur_pos[nextIndex][1] == 'JJ' or cur_pos[nextIndex][0] == 'than':
                        res.append(cur_pos[nextIndex][0])

                nounStr_Clean = [ele for ele in tokenized_sen[0] if ele not in res and ele.lower() not in removeWords
                                 and not ele.startswith('placename') and not ele.startswith('edate') and not
                                 ele.startswith('equantity') and not ele.startswith('etime') and not ele.startswith(
                    'epercent')
                                 and not ele.startswith(
                    'outside') and not ele.isnumeric() and not ele == ',' or ele == '911']
                # print('nounStr_Clean:', nounStr_Clean)

                cur_noun_Clean = ' '.join(text for text in nounStr_Clean).strip()
                # print('cur_noun_Clean:', cur_noun_Clean)

                # [X] remove 'areas' in 'what areas', 'many' in 'how many'...'how many buildings'->'buildings'
                if cur_noun_Clean.startswith('areas'):
                    cur_noun_Clean = cur_noun_Clean.replace('areas', '')
                # if cur_noun_Clean.startswith('area'):
                #     cur_noun_Clean = cur_noun_Clean.replace('area', '')
                if cur_noun_Clean.startswith('many'):
                    cur_noun_Clean = cur_noun_Clean.replace('many', '')
                if cur_noun_Clean.startswith('much'):
                    cur_noun_Clean = cur_noun_Clean.replace('much', '')

                if cur_noun_Clean:
                    noun_phrases_CleanList.append(cur_noun_Clean.strip())

    return noun_phrases_CleanList

# [X] Identify Core concepts: field, object, event, network, contentAmount, coverageAmount, conProportion, proportion
# input string sentence: What is number of crime cases for each police district in PlaceName0 in Date0
# output string sentence: what is conamount0 era of event0 for each object0 in placename0 in date0
# output tuple: {'Object': ['police district'], 'Event': ['crime cases'], 'ConAmount': ['number']}
def core_concept_match(sentence):

    coreConcept_dect = {}

    after_place = place_ner(sentence)
    coreConcept_dect['placename'] = after_place[0]

    after_entity = entity_ner(after_place[1])
    coreConcept_dect.update(after_entity[0])

    # [X] Noun chunks recognition, and remove Entity tags from detected noun chunks
    cur_sen = after_entity[1].lower()
    cur_doc = nlp(cur_sen)
    cur_matches = matcher(cur_doc)
    match_phrases = [cur_doc[start: end].text for mat_id, start, end in cur_matches]
    for cur_ph in match_phrases:
        cur_sen = cur_sen.replace(cur_ph + ' ', '')
    cur_doc2 = nlp(cur_sen)
    noun_list = [noun.text for noun in cur_doc2.noun_chunks]
    if not len(match_phrases) == 0:
        for cur_phr in match_phrases:
            noun_list.append(cur_phr)
    # print('noun_list:', noun_list)

    noun_list_Clean = noun_phrases_correct(noun_list)
    # print('noun_list_Clean:', noun_list_Clean)

    # [X] Identify core concepts from noun chunks
    field = []
    object = []
    objectQuality = []
    event = []
    eventQuality = []
    network = []
    networkQuality = []
    quality = []
    conAmount = []
    objConAmount = []
    eveConAmount = []
    covAmount = []
    conConPro = []
    objConobjConPro = []
    eveConobjConPro = []
    conCovPro = []
    objConobjCovPro = []
    eveConobjCovPro = []
    covPro = []
    proportion = []

    fie_loc = 0
    obj_loc = 0
    objQ_loc = 0
    eve_loc = 0
    eveQ_loc = 0
    net_loc = 0
    netQ_loc = 0
    qua_loc = 0
    conA_loc = 0
    objConA_loc = 0
    eveConA_loc = 0
    covA_loc = 0
    objConobjConP_loc = 0
    eveconobjconP_loc = 0
    conconP_loc = 0
    objConobjCovP_loc = 0
    eveConobjCovP_loc = 0
    concovP_loc = 0
    covpro_loc = 0
    pro_loc = 0

    cur_sentence = after_entity[1].lower()

    for cur_noun in noun_list_Clean:
        cur_w = cur_noun.split(' ')
        # print('cur_w:', cur_w)
        if cur_noun in coreCon_dict['text'] and not cur_noun == 'population':
            cur_index = coreCon_dict['text'].index(cur_noun)
            if coreCon_dict['tag'][cur_index] == 'field':
                field.append(cur_noun)
                cur_sentence = cur_sentence.replace(cur_noun,
                                            'field' + str(fie_loc) + ' ' + coreCon_dict['measureLevel'][
                                                cur_index])
                fie_loc += 1
            elif coreCon_dict['tag'][cur_index] == 'object':
                object.append(cur_noun)
                cur_sentence = cur_sentence.replace(cur_noun, 'object' + str(obj_loc))
                obj_loc += 1
            elif coreCon_dict['tag'][cur_index] == 'object quality':
                objectQuality.append(cur_noun)
                cur_sentence = cur_sentence.replace(cur_noun,
                                            'objectquality' + str(objQ_loc) + ' ' +
                                            coreCon_dict['measureLevel'][
                                                cur_index])
                objQ_loc += 1
            elif coreCon_dict['tag'][cur_index] == 'event':
                event.append(cur_noun)
                cur_sentence = cur_sentence.replace(cur_noun, 'event' + str(eve_loc))
                eve_loc += 1
            elif coreCon_dict['tag'][cur_index] == 'event quality':
                eventQuality.append(cur_noun)
                cur_sentence = cur_sentence.replace(cur_noun,
                                            'eventquality' + str(eveQ_loc) + ' ' + coreCon_dict['measureLevel'][
                                                cur_index])
                eveQ_loc += 1
            elif coreCon_dict['tag'][cur_index] == 'network':
                cur_ns = cur_noun.split(' ')[0]
                cur_i = [x for x, y in enumerate(pos) if y[0] == cur_ns]
                if len(cur_i) >= 1 and (pos[cur_i[0] - 1][1] == 'JJS' or pos[cur_i[0] - 1][1] == 'RBS'):
                    cur_np = pos[cur_i[0] - 1][0] + ' ' + cur_noun
                    network.append(cur_np)
                    cur_sentence = cur_sentence.lower().replace(cur_np, 'network' + str(net_loc))
                    net_loc += 1
                else:
                    network.append(cur_noun)
                    cur_sentence = cur_sentence.lower().replace(cur_noun, 'network' + str(net_loc))
                    net_loc += 1
            elif coreCon_dict['tag'][cur_index] == 'network quality':
                networkQuality.append(cur_noun)
                cur_sentence = cur_sentence.replace(cur_noun,
                                            'networkquality' + str(eveQ_loc) + ' ' + coreCon_dict['measureLevel'][
                                                cur_index])
                netQ_loc += 1
            elif coreCon_dict['tag'][cur_index] == 'quality':
                quality.append(cur_noun)
                cur_sentence = cur_sentence.replace(cur_noun,
                                            'quality' + str(qua_loc) + ' ' + coreCon_dict['measureLevel'][
                                                cur_index])
                qua_loc += 1
            elif coreCon_dict['tag'][cur_index] == 'covamount':
                covAmount.append(cur_noun)
                cur_sentence = cur_sentence.replace(cur_noun,
                                            'covamount' + str(covA_loc) + ' ' + coreCon_dict['measureLevel'][
                                                cur_index])
                covA_loc += 1
            elif coreCon_dict['tag'][cur_index] == 'conamount':
                conAmount.append(cur_noun)
                cur_sentence = cur_sentence.replace(cur_noun,
                                            'conamount' + str(conA_loc) + ' ' + coreCon_dict['measureLevel'][
                                                cur_index])
                conA_loc += 1
            elif coreCon_dict['tag'][cur_index] == 'object conamount':
                objConAmount.append(cur_noun)
                cur_sentence = cur_sentence.replace(cur_noun,
                                            'objconamount' + str(objConA_loc) + ' ' + coreCon_dict['measureLevel'][
                                                cur_index])
                objConA_loc += 1
            elif coreCon_dict['tag'][cur_index] == 'event conamount':
                eveConAmount.append(cur_noun)
                cur_sentence = cur_sentence.replace(cur_noun,
                                            'eveconamount' + str(eveConA_loc) + ' ' + coreCon_dict['measureLevel'][
                                                cur_index])
                eveConA_loc += 1
            elif coreCon_dict['tag'][cur_index] == 'objconobjconpro':
                objConobjConPro.append(cur_noun)
                cur_sentence = cur_sentence.replace(cur_noun,
                                            'objconobjconpro' + str(conconP_loc) + ' ' + coreCon_dict['measureLevel'][
                                                cur_index])
                objConobjConP_loc += 1
            elif coreCon_dict['tag'][cur_index] == 'eveconobjconpro':
                eveConobjConPro.append(cur_noun)
                cur_sentence = cur_sentence.replace(cur_noun,
                                            'eveconobjconpro' + str(conconP_loc) + ' ' + coreCon_dict['measureLevel'][
                                                cur_index])
                eveconobjconP_loc += 1
            elif coreCon_dict['tag'][cur_index] == 'conconpro':
                conConPro.append(cur_noun)
                cur_sentence = cur_sentence.replace(cur_noun,
                                            'conconpro' + str(conconP_loc) + ' ' + coreCon_dict['measureLevel'][
                                                cur_index])
                conconP_loc += 1
            elif coreCon_dict['tag'][cur_index] == 'objconobjcovpro':
                objConobjCovPro.append(cur_noun)
                cur_sentence = cur_sentence.replace(cur_noun,
                                            'objconobjcovpro' + str(concovP_loc) + ' ' + coreCon_dict['measureLevel'][
                                                cur_index])
                objConobjCovP_loc += 1
            elif coreCon_dict['tag'][cur_index] == 'eveconobjcovpro':
                eveConobjCovPro.append(cur_noun)
                cur_sentence = cur_sentence.replace(cur_noun,
                                            'eveconobjcovpro' + str(concovP_loc) + ' ' + coreCon_dict['measureLevel'][
                                                cur_index])
                eveConobjCovP_loc += 1
            elif coreCon_dict['tag'][cur_index] == 'concovpro':
                conCovPro.append(cur_noun)
                cur_sentence = cur_sentence.replace(cur_noun,
                                            'concovpro' + str(concovP_loc) + ' ' + coreCon_dict['measureLevel'][
                                                cur_index])
                concovP_loc += 1
            elif coreCon_dict['tag'][cur_index] == 'covpro':
                covPro.append(cur_noun)
                cur_sentence = cur_sentence.replace(cur_noun,
                                            'covpro' + str(covpro_loc) + ' ' + coreCon_dict['measureLevel'][
                                                cur_index])
                covpro_loc += 1
            elif coreCon_dict['tag'][cur_index] == 'proportion':
                proportion.append(cur_noun)
                cur_sentence = cur_sentence.replace(cur_noun,
                                            'proportion' + str(pro_loc) + ' ' + coreCon_dict['measureLevel'][
                                                cur_index])
                pro_loc += 1
        elif cur_w[0] == 'average' or cur_w[0] == 'median' or cur_w[0] == 'total':  # average Euclidean distance
            cur_r = ' '.join(cur_w[1:])  # 'Euclidean' 'distance' -> 'Euclidean distance'
            if cur_r in coreCon_dict['text']:
                cur_in = coreCon_dict['text'].index(cur_r)
                if coreCon_dict['tag'][cur_in] == 'field':
                    field.append(cur_r)
                    cur_sentence = cur_sentence.replace(cur_r,
                                                'field' + str(fie_loc) + ' ' + coreCon_dict['measureLevel'][cur_in])
                    fie_loc += 1
                elif coreCon_dict['tag'][cur_in] == 'object':
                    object.append(cur_r)
                    cur_sentence = cur_sentence.replace(cur_r, 'object' + str(obj_loc))
                    obj_loc += 1
                elif coreCon_dict['tag'][cur_in] == 'object quality':
                    objectQuality.append(cur_r)
                    cur_sentence = cur_sentence.replace(cur_r,
                                                'objectquality' + str(objQ_loc) + ' ' + coreCon_dict['measureLevel'][
                                                    cur_in])
                    objQ_loc += 1
                elif coreCon_dict['tag'][cur_in] == 'event':
                    event.append(cur_r)
                    cur_sentence = cur_sentence.replace(cur_r, 'event' + str(eve_loc))
                    eve_loc += 1
                elif coreCon_dict['tag'][cur_in] == 'event quality':
                    eventQuality.append(cur_r)
                    cur_sentence = cur_sentence.replace(cur_r,
                                                'eventquality' + str(eveQ_loc) + ' ' + coreCon_dict['measureLevel'][
                                                    cur_in])
                    eveQ_loc += 1
                elif coreCon_dict['tag'][cur_in] == 'network':
                    network.append(cur_r)
                    cur_sentence = cur_sentence.lower().replace(cur_r, 'network' + str(net_loc))
                    net_loc += 1
                elif coreCon_dict['tag'][cur_in] == 'network quality':
                    networkQuality.append(cur_r)
                    cur_sentence = cur_sentence.lower().replace(cur_r, 'networkquality' + str(netQ_loc) + ' ' +
                                                        coreCon_dict['measureLevel'][
                                                            cur_in])
                    netQ_loc += 1
                elif coreCon_dict['tag'][cur_in] == 'quality':
                    quality.append(cur_r)
                    cur_sentence = cur_sentence.replace(cur_r,
                                                'quality' + str(qua_loc) + ' ' + coreCon_dict['measureLevel'][cur_in])
                    qua_loc += 1
                elif coreCon_dict['tag'][cur_in] == 'covamount':
                    covAmount.append(cur_r)
                    cur_sentence = cur_sentence.replace(cur_r, 'covamount' + str(covA_loc) + ' ' + coreCon_dict['measureLevel'][
                        cur_in])
                    covA_loc += 1
                elif coreCon_dict['tag'][cur_in] == 'conamount':
                    conAmount.append(cur_r)
                    cur_sentence = cur_sentence.replace(cur_r, 'conamount' + str(conA_loc) + ' ' + coreCon_dict['measureLevel'][
                        cur_in])
                    conA_loc += 1
                elif coreCon_dict['tag'][cur_in] == 'object conamount':
                    objConAmount.append(cur_r)
                    cur_sentence = cur_sentence.replace(cur_r,
                                                'objconamount' + str(objConA_loc) + ' ' + coreCon_dict['measureLevel'][
                                                    cur_in])
                    objConA_loc += 1

    if 'population' in cur_sentence:
        objConAmount.append('population')
        cur_sentence = cur_sentence.replace('population', 'objconamount' + str(objConA_loc) + ' ' + 'era')
        objConA_loc += 1

    # [X] 'local road' is network in 'What is the potential accessibility by local road for each 2 by 2 km grid cell
    # in Finland'; 'roads' is object in 'Which roads are intersected with forest areas in UK'
    for cur_noun in noun_list_Clean:
        if cur_noun in networkSet:
            if 'network' in cur_sentence or 'access' in cur_sen or 'connectivity' in cur_sen:
                network.append(cur_noun)
                cur_sentence = cur_sentence.lower().replace(cur_noun, 'network' + str(net_loc))
                net_loc += 1
            else:
                object.append(cur_noun)
                cur_sentence = cur_sentence.replace(cur_noun, 'object' + str(obj_loc))
                obj_loc += 1

    if not field == []:
        coreConcept_dect['field'] = field
    if not object == []:
        coreConcept_dect['object'] = object
    if not objectQuality == []:
        coreConcept_dect['objectquality'] = objectQuality
    if not event == []:
        coreConcept_dect['event'] = event
    if not eventQuality == []:
        coreConcept_dect['eventquality'] = eventQuality
    if not network == []:
        coreConcept_dect['network'] = network
    if not networkQuality == []:
        coreConcept_dect['networkquality'] = networkQuality
    if not quality == []:
        coreConcept_dect['quality'] = quality
    if not conAmount == []:
        coreConcept_dect['conamount'] = conAmount
    if not len(objConAmount) == 0:
        coreConcept_dect['objconamount'] = objConAmount
    if not len(eveConAmount) == 0:
        coreConcept_dect['eveconamount'] = eveConAmount
    if not covAmount == []:
        coreConcept_dect['covamount'] = covAmount
    if not conConPro == []:
        coreConcept_dect['conconpro'] = conConPro
    if not objConobjConPro == []:
        coreConcept_dect['objconobjconpro'] = objConobjConPro
    if not eveConobjConPro == []:
        coreConcept_dect['eveconobjconpro'] = eveConobjConPro
    if not conCovPro == []:
        coreConcept_dect['concovpro'] = conCovPro
    if not objConobjCovPro == []:
        coreConcept_dect['objconobjcovpro'] = objConobjCovPro
    if not eveConobjCovPro == []:
        coreConcept_dect['eveconobjcovpro'] = eveConobjCovPro
    if not covPro == []:
        coreConcept_dect['covpro'] = covPro
    if not proportion == []:
        coreConcept_dect['proportion'] = proportion

    # print(coreConcept_dect)
    # print(cur_sentence)

    return coreConcept_dect, cur_sentence.lower()


