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
                meaLevel.append('null')
    coreCon['text'] = text
    coreCon['tag'] = tag
    coreCon['measureLevel'] = meaLevel

    return coreCon


# [X] load core concept dictionary in coreCon_dict, and network dictionary into networkSet
corePath = 'Dictionary/coreConceptsML.txt'
networkPath = 'Dictionary/network.txt'
coreCon_dict = load_ccdict(corePath)
networkSet = set(l.strip().lower() for l in open(networkPath, encoding="utf-8"))

# [X] zip the three lists in coreCon_dict together and sort coreCon_dict['text'] by descending string length
sorted_coreCon = sorted(zip(coreCon_dict['text'], coreCon_dict['tag'], coreCon_dict['measureLevel']),
                        key=lambda x: len(x[0]), reverse=True)
sorted_networkSet = sorted(networkSet, key = len, reverse=True)

removeWords = ['what areas', 'what area']


# [X] Identify Core concepts: field, object, event, network, contentAmount, coverageAmount, conProportion, proportion
# input string sentence: What is density of street intersections support extent
# output string sentence:
# output tuple: {'Object': ['police district'], 'Event': ['crime cases'], 'ConAmount': ['number']}
def core_concept_match(sentence):
    cur_sen = sentence
    coreConcept_dect = {}
    tag_count = {}

    # [X] remove 'what areas', avoid annotating 'areas' as field in 'what areas'
    addword = ''
    for word in removeWords:
        if word in cur_sen:
            cur_sen = cur_sen.replace(word, '')
            addword = word

    for ele in sorted_coreCon:
        if ele[0] in cur_sen:
            for netW in sorted_networkSet:
                if ele[0] in netW and netW in cur_sen and cur_sen.index(ele[0]) >= cur_sen.index(
                        netW) and cur_sen.index(ele[0]) + len(ele[0]) <= cur_sen.index(netW) + len(netW):
                    break
            else:
                if ele[1] not in coreConcept_dect:
                    coreConcept_dect[ele[1]] = []
                    tag_count[ele[1]] = 0
                coreConcept_dect[ele[1]].append(ele[0])
                if ele[2] == 'null':
                    cur_sen = cur_sen.replace(ele[0], ele[1] + str(tag_count[ele[1]]))
                else:
                    cur_sen = cur_sen.replace(ele[0], ele[1] + str(tag_count[ele[1]]) + ' ' + ele[2])
                tag_count[ele[1]] += 1

    # [X] 'local road' is network in 'What is the potential accessibility by local road for each 2 by 2 km grid cell
    # in Finland'; 'roads' is object in 'Which roads are intersected with forest areas in UK'
    for net_ele in sorted_networkSet:
        if net_ele in cur_sen:
            if 'network' in cur_sen or ('objectquality' in cur_sen and (any('access' in e for e in coreConcept_dect['objectquality']) or any('connectivity' in e for e in coreConcept_dect['objectquality']))):
                if 'network' not in coreConcept_dect:
                    coreConcept_dect['network'] = []
                    tag_count['network'] = 0
                coreConcept_dect['network'].append(net_ele)
                cur_sen = cur_sen.replace(net_ele, 'network' + str(tag_count['network']))
                tag_count['network'] += 1
            else:
                if 'object' not in coreConcept_dect:
                    coreConcept_dect['object'] = []
                    tag_count['object'] = 0
                coreConcept_dect['object'].append(net_ele)
                cur_sen = cur_sen.replace(net_ele, 'object' + str(tag_count['object']))
                tag_count['object'] += 1

    # [X] add 'what areas' to cur_sen
    if addword:
        cur_sen = addword + cur_sen

    # print('sentence\n', sentence)
    # print('cur_sen\n', cur_sen)
    # print('coreConcept_dect\n', coreConcept_dect)

    return coreConcept_dect, cur_sen.lower()
