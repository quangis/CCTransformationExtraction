import numpy as np

# global functional roles
supis = []
meais = []
con_meais = []
mea1is = []

# [X] Read extremaTrans.txt into a dictionary.
def readExtremaR(extfilePath):
    extreR = {}

    keyword = []
    tType = []  # types may involve in transformations
    cctag = []  # core concept type
    ml = []  # measurement level

    with open(extfilePath, encoding="utf-8") as extR:
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

extfilePath = 'Dictionary/extremaTrans.txt'
extre_Dict = readExtremaR(extfilePath)

# [X] Add core concept type of for extremaR and compareR
def addext_type(e_keyword):
    global core_id

    e_index = extre_Dict['keyword'].index(e_keyword)

    ext_type = {'type': extre_Dict['cctag'][e_index], 'id': str(core_id),
                'keyword': extre_Dict['tType'][e_index]}
    if extre_Dict['ml'][e_index] != 'null':
        ext_type['measureLevel'] = extre_Dict['ml'][e_index]

    return ext_type


# [X] Generate type for a subset of a concept. only change id, while keywords and type remain the same.
def new_type(curid):
    global core_id
    global coreConTrans

    newtype = {}

    if type(curid) == list:
        curid = curid[-1]

    if type(curid) == str:
        newtype_index = [i for i, j in enumerate(coreConTrans['types']) if j['id'] == curid][
            0]  # find index for the subset transcross_condi['after']
        newtype = coreConTrans['types'][newtype_index].copy()  # copy type for the subset
        newtype['id'] = str(core_id)  # update id for the subset
    else:
        print("Error: input is not a string in new_type()")

    return newtype


# [X] Generate type for a generated amount that transformed from a object, event, field, support, extent into amount.
# c_coreC: concept name, can be object, event, field, support
def newAmount_type(c_coreC, keywd):
    global core_id
    global coreConTrans

    newAmoutType = {}

    if c_coreC == 'object' or c_coreC == 'event':
        newAmoutType = {'type': 'amount', 'id': str(core_id), 'keyword': keywd if keywd!= None else '', 'measureLevel': 'era_'}
    elif c_coreC == 'field' or c_coreC == 'region' or c_coreC == 'boolfield' or c_coreC == 'support' or c_coreC == 'extent':
        newAmoutType = {'type': 'covamount', 'id': str(core_id), 'keyword': keywd if keywd!= None else '', 'measureLevel': 'era_'}
    elif c_coreC == 'networkquality':
        newAmoutType = {'type': 'objectquality', 'id': str(core_id), 'keyword': keywd if keywd!= None else '', 'measureLevel': 'rat_'}
    elif c_coreC == 'network':
        newAmoutType = {'type': 'object', 'id': str(core_id), 'keyword': keywd if keywd!= None else ''}
    elif c_coreC == 'visibility':
        newAmoutType = {'type': 'field', 'id': str(core_id), 'keyword': keywd if keywd != None else '', 'measureLevel': 'nom_'}
    elif c_coreC == 'distance':
        newAmoutType = {'type': 'networkquality', 'id': str(core_id), 'keyword': keywd if keywd != None else '',
                        'measureLevel': 'rat_'}

    return newAmoutType


# [X] Generate transformations
# cur_input: list
# cur_output: list
# cur_key: string or None
def gen_trans(cur_input, cur_output, cur_key):
    cur_trans = {}

    for i in range(0, len(cur_input)):
        if type(cur_input[i]) == list:
            cur_input[i] = cur_input[i][-1]

    for j in range(0, len(cur_output)):
        if type(cur_output[j]) == list:
            cur_output[j] = cur_output[j][-1]

    if type(cur_input) == list and type(cur_output) == list:
        cur_trans['before'] = cur_input
        cur_trans['after'] = cur_output
    else:
        print("Error: input or output is not a list in gen_trans(). {}".format(cur_input))

    if type(cur_key) == str:
        cur_trans['key'] = cur_key
    elif cur_key == None:
        pass
    else:
        print("Error: key is not a string in gen_trans(). {}".format(cur_key))

    return cur_trans


# [X] Add new types in coreConTrans
def update_coreType(cur_type):
    global coreConTrans

    if type(cur_type) == dict:
        coreConTrans.setdefault('types', []).append(cur_type)
    elif type(cur_type) == list:
        coreConTrans.setdefault('types', []).extend(cur_type)

    return coreConTrans


# [X] Add new transformations in coreConTrans
def update_coreTrans(cur_tran):
    global coreConTrans

    if type(cur_tran) == dict:
        coreConTrans.setdefault('transformations', []).append(cur_tran)
    elif type(cur_tran) == list:
        coreConTrans.setdefault('transformations', []).extend(cur_tran)

    return coreConTrans

# update next_TypeDict['id'] for next trans inside comR_trans() and extR_trans()
def update_nextid(nextTypeDict):
    global core_id
    global mea1is

    if 'pro' in nextTypeDict['text'][-1] and len(nextTypeDict['text']) == 2 and not mea1is:
        nextTypeDict['tag'].insert(0, 'coreC')
        nextTypeDict['text'].insert(0, nextTypeDict['text'][0])
        nextTypeDict['id'].insert(0, str(core_id))
    else:
        nextTypeDict['id'][0] = str(core_id)

    return nextTypeDict


# [X] Update core_id
def update_id():
    global core_id

    core_id += 1

    return core_id


# remove id of distfield and boolfield
def remove_boolid(conTypeDict):
    global coreConTrans

    dist_index = [i for i in range(0, len(coreConTrans['types'])) if coreConTrans['types'][i]['type'] == 'distfield'][0]
    # bool_index = [i for i in range(0, len(coreConTrans['types'])) if coreConTrans['types'][i]['type'] == 'boolfield'][0]

    del coreConTrans['types'][dist_index]
    del coreConTrans['types'][dist_index]


def merge_aggConAmount(mergeTypeDict):
    global coreConTrans
    c_index = None

    a_index = [i for i in range(0, len(coreConTrans['types'])) if coreConTrans['types'][i]['id'] == mergeTypeDict['id'][-1]][0]
    a_keywd = coreConTrans['types'][a_index]['keyword']

    if mergeTypeDict['tag'] == ['coreC', 'aggre'] and a_keywd == 'total':
        c_index = [i for i in range(0, len(coreConTrans['types'])) if coreConTrans['types'][i]['id'] == mergeTypeDict['id'][0]][0]
    elif mergeTypeDict['tag'] == ['coreC', 'coreC', 'aggre'] and a_keywd == 'total':
        c_index = [i for i in range(0, len(coreConTrans['types'])) if coreConTrans['types'][i]['id'] == mergeTypeDict['id'][1]][0]

    if c_index != None:
        coreConTrans['types'][c_index]['keyword'] = a_keywd + ' ' + coreConTrans['types'][c_index]['keyword']
        coreConTrans['types'].pop(a_index)
        mergeTypeDict['tag'].pop()
        mergeTypeDict['text'].pop()
        mergeTypeDict['id'].pop()

    return mergeTypeDict


# [X] Generate transformation for comparison condition and sub-condition
# allTypeDict: coreTypeDict, include functional roles and their types
# index of current functional role in coreTypeDict['funcRole']
# index of the next functional role (which involve in transformations sometimes)
def comR_trans(c_index, n_index):
    global core_id
    global coreTypeDict

    cur_TypeDict = coreTypeDict['types'][c_index]
    next_TypeDict = coreTypeDict['types'][n_index]

    re_comp = cur_TypeDict.copy()
    re_comp['text'] = [t for i, t in enumerate(re_comp['text']) if re_comp['tag'][i] != 'compareR']
    re_comp['tag'] = list(filter(lambda x: x != 'compareR', re_comp['tag']))

    if len(re_comp['tag']) == 0:  # {'tag': ['compareR', 'compareR'], 'text': ['older than', 'younger than']}
        if all(ct in extre_Dict['keyword'] for ct in cur_TypeDict['text']):
            # quality/pro/amount + next_TypeDict['id'][0] -> new next_TypeDict['id'][0]
            # core_id is the id of the concept describing compareR. next_TypeDict['id'][0] is a list when it is origin or destination
            input0 = [next_TypeDict['id'][0] if type(next_TypeDict['id'][0]) != list else next_TypeDict['id'][0][-1], str(core_id)]
            update_coreType(addext_type(cur_TypeDict['text'][0]))  # update the type describing compareR
            update_id()  # update core_id for output
            trans_c0 = gen_trans(input0, [str(core_id)], None)
            update_coreTrans(trans_c0)
            update_coreType(new_type(next_TypeDict['id'][0] if type(next_TypeDict['id'][0]) != list else next_TypeDict['id'][0][-1]))
            # update next_TypeDict['id'] for next trans
            next_TypeDict = update_nextid(next_TypeDict)
            # update core_id += 1 for next trans
            update_id()
    elif (re_comp['tag'][-1] == 'coreC' and 'pro' not in re_comp['text'][-1]) or ('pro' in re_comp['text'][-1] and len(re_comp['tag']) == 1) or re_comp['tag'][-1] == 'conAmount':
        # generate transformations before compareR, e.g., ['coreC','conAmount', compareR]
        if re_comp['tag'][-1] == 'conAmount':
            update_coreTrans(conAmount_trans(c_index, re_comp))
        elif len(re_comp['tag']) > 1:
            update_coreTrans(write_trans_within(re_comp))
        # cur_TypeDict = {'tag':['compareR', 'compareR', 'coreC'], 'text':['lower than', 'higher than', 'field 0 rat_'],  'id': ['0']}
        if 'field' in re_comp['text'][-1]:  # field -> new field
            trans_field = gen_trans([re_comp['id'][-1]], [str(core_id)],
                                    None)  # generate the transformation to update field
            update_coreTrans(trans_field)  # add trans
            update_coreType(new_type(re_comp['id'][-1]))  # add type
            # update id representing the new field for next step
            cur_TypeDict['id'][-1] = str(core_id)
            update_id()
            # field * next input -> new new input
            update_coreTrans(gen_trans([cur_TypeDict['id'][-1], next_TypeDict['id'][0]], [str(core_id)], None))
            update_coreType(new_type(next_TypeDict['id'][0]))
            next_TypeDict = update_nextid(next_TypeDict)
            update_id()
        # quality/pro/amount + next_TypeDict['id'][0] -> new next_TypeDict['id'][0]
        else:
            input_qua = [next_TypeDict['id'][0], cur_TypeDict['id'][-1]]
            trans_qua = gen_trans(input_qua, [str(core_id)], None)
            update_coreTrans(trans_qua)
            update_coreType(new_type(next_TypeDict['id'][0]))
            # update next_TypeDict['id'] for next step
            next_TypeDict = update_nextid(next_TypeDict)
        # update core_id += 1 for next trans
        update_id()
    elif re_comp['tag'][-1] == 'aggre':
        # aggre trans
        aggre_trans(c_index, re_comp)
        # compareR trans
        input_agg = [next_TypeDict['id'][0], re_comp['id'][-1]]
        trans_comagg = gen_trans(input_agg, [str(core_id)], None)
        update_coreTrans(trans_comagg)
        update_coreType(new_type(next_TypeDict['id'][0]))
        # update next_TypeDict['id'] for next step
        next_TypeDict = update_nextid(next_TypeDict)
        update_id()
    elif 'boolfield' in re_comp['tag']:
        trans_bool = write_trans_within(re_comp)
        update_coreTrans(trans_bool)
        if 'region' in next_TypeDict['text'][0]:
            update_coreTrans(gen_trans([cur_TypeDict['id'][-1]], [next_TypeDict['id'][0]], None))


# [X] Generate transformation for extremaR condition, sub-condition and measure
# allTypeDict: coreTypeDict, include functional roles and their types
# index of current functional role in coreTypeDict['funcRole']
# index of the measure functional role (which involve in transformations sometimes)
def extR_trans(c_index, n_index):
    global core_id
    global coreTypeDict

    cur_TypeDict = coreTypeDict['types'][c_index]
    next_TypeDict = coreTypeDict['types'][n_index]

    re_ext = cur_TypeDict.copy()
    if cur_TypeDict['text'][cur_TypeDict['tag'].index('extremaR')] != 'closest to':
        re_ext['text'] = [t for i, t in enumerate(re_ext['text']) if re_ext['tag'][i] != 'extremaR']
        re_ext['tag'] = list(filter(lambda x: x != 'extremaR', re_ext['tag']))


    if len(re_ext['tag']) == 0:  # {'tag': ['extremaR'], 'text': ['biggest']}
        if all(ct in extre_Dict['keyword'] for ct in cur_TypeDict['text']):
            extK_index = extre_Dict['keyword'].index(cur_TypeDict['text'][0])
            if extre_Dict['cctag'][extK_index] == 'covamount':
                # next_TypeDict['id'][0] -> covamount, e.g., park -> area
                trans_e = gen_trans([next_TypeDict['id'][0]], [str(core_id)],
                                    None)  # core_id is the id of the concept describing extremaR
                update_coreTrans(trans_e)
                update_coreType(addext_type(cur_TypeDict['text'][0]))  # update the type describing extremaR
            else:
                update_coreType(addext_type(cur_TypeDict['text'][0]))
            # extremaR + next_TypeDict['id'][0] -> new next_TypeDict['id'][0]
            input0 = [next_TypeDict['id'][0], str(core_id)]
            update_id()  # update core_id for output
            trans0 = gen_trans(input0, [str(core_id)], None)
            update_coreTrans(trans0)
            update_coreType(new_type(next_TypeDict['id'][0]))
            # update next_TypeDict['id'] for next trans
            next_TypeDict = update_nextid(next_TypeDict)
            # update core_id += 1 for next trans
            update_id()
    elif re_ext['tag'] == ['coreC']:
        # cur_TypeDict = {'tag':['coreC', 'extremaR'], 'text':['eveconobjconpro 0 ira_', 'highest'],  'id': ['0']}
        if 'field' in re_ext['text'][0]:  # field -> new field
            trans_field = gen_trans(cur_TypeDict['id'], [str(core_id)],
                                    None)  # generate the transformation to update field
            update_coreTrans(trans_field)  # add trans
            update_coreType(new_type(cur_TypeDict['id'][0]))  # add type
            # update id representing the new field for next step
            cur_TypeDict['id'][0] = str(core_id)
        # quality/pro/amount + next_TypeDict['id'][0] -> new next_TypeDict['id'][0]
        else:
            input_qua = [next_TypeDict['id'][0], cur_TypeDict['id'][0]]
            trans_qua = gen_trans(input_qua, [str(core_id)], None)
            update_coreTrans(trans_qua)
            update_coreType(new_type(next_TypeDict['id'][0]))
            # update next_TypeDict['id'] for next step
            next_TypeDict = update_nextid(next_TypeDict)
        # update core_id += 1 for next trans
        update_id()
    elif re_ext['tag'][-1] == 'aggre':
        aggre_trans(c_index, re_ext)
        input_extagg = [next_TypeDict['id'][0], re_ext['id'][-1]]
        trans_extagg = gen_trans(input_extagg, [str(core_id)], None)
        update_coreTrans(trans_extagg)
        update_coreType(new_type(next_TypeDict['id'][0]))
        # update next_TypeDict['id'] for next step
        next_TypeDict = update_nextid(next_TypeDict)
        update_id()
    elif len(re_ext['tag']) > 1 and 'pro' in re_ext['text'][-1]:
        # proportion trans
        pro_trans(c_index, re_ext)
        # extremaR trans
        update_coreTrans(gen_trans([re_ext['id'][-1], next_TypeDict['id'][0]], [str(core_id)], None))
        update_coreType(new_type(next_TypeDict['id'][0]))
        update_id()
    elif 'boolfield' in re_ext['tag']:
        trans_bool = write_trans_within(re_ext)
        update_coreTrans(trans_bool)
        update_coreTrans(gen_trans([next_TypeDict['id'][0], re_ext['id'][-1]], [str(core_id)], None))
        update_coreType(new_type(next_TypeDict['id'][0]))
        next_TypeDict['id'][0] = str(core_id)
        update_id()

# [X] Generate transformation for aggre in condition, sub-condition and measure
# allTypeDict: coreTypeDict, include functional roles and their types
# index of current functional role in coreTypeDict['funcRole']
# TypeDict that includes concepts for generating aggregation transformations
def aggre_trans(c_index, aggTypeDict):
    global core_id
    global meais
    global con_meais
    global supis
    global coreTypeDict

    frole = coreTypeDict['funcRole'][c_index]

    if aggTypeDict['tag'] == ['coreC', 'aggre'] or aggTypeDict['tag'] == ['coreC', 'coreC'] :
        if frole == 'condition':
            c_mTypeDict = coreTypeDict['types'][meais[0]]
            c_input = [aggTypeDict['id'][0], c_mTypeDict['id'][0]]
            trans_agg = gen_trans(c_input, [aggTypeDict['id'][-1]], c_mTypeDict['id'][0])
            update_coreTrans(trans_agg)
        elif frole == 'measure':
            if supis and not con_meais:
                c_supTypeDict = coreTypeDict['types'][supis[0]]
                c_input = [aggTypeDict['id'][0], c_supTypeDict['id'][0]]
                trans_agg = gen_trans(c_input, [aggTypeDict['id'][-1]], c_supTypeDict['id'][0])
                update_coreTrans(trans_agg)
            elif not supis and not con_meais:
                extent_index = coreTypeDict['funcRole'].index('extent')
                c_input = [aggTypeDict['id'][0], coreTypeDict['types'][extent_index][0]]
                trans_agg = gen_trans(c_input, [aggTypeDict['id'][-1]], coreTypeDict['types'][extent_index][0])
                update_coreTrans(trans_agg)
    elif aggTypeDict['tag'] == ['coreC', 'coreC', 'aggre']:
        if frole == 'measure':
            if supis and not con_meais:
                c_supTypeDict = coreTypeDict['types'][supis[0]]
                update_coreTrans(gen_trans([aggTypeDict['id'][0]], [aggTypeDict['id'][1]], None))
                # aggre trans
                update_coreTrans(gen_trans([aggTypeDict['id'][1]], [aggTypeDict['id'][-1]], c_supTypeDict['id'][-1]))
            elif not supis and not con_meais:
                agg_extent_id = coreTypeDict['types'][coreTypeDict['funcRole'].index('extent')][0]
                update_coreTrans(gen_trans([aggTypeDict['id'][0]], [aggTypeDict['id'][1]], None))
                # aggre trans
                update_coreTrans(gen_trans([aggTypeDict['id'][1], agg_extent_id], [aggTypeDict['id'][-1]], agg_extent_id))
            elif not supis and con_meais: # What is the average housing price of neighborhoods within 100 meters from a school in Utrecht, the Netherlands
                agg_extent_id = coreTypeDict['types'][coreTypeDict['funcRole'].index('extent')][0]
                update_coreTrans(gen_trans([aggTypeDict['id'][0]], [aggTypeDict['id'][1]], None))
                # aggre trans
                update_coreTrans(gen_trans([aggTypeDict['id'][1]], [aggTypeDict['id'][-1]], agg_extent_id))
    elif aggTypeDict['tag'] == ['destination', 'origin', 'networkQ', 'aggre']:
        if frole == 'measure':
            bef_aggTypeDict = {key: value[0: i] for key, value in aggTypeDict.items() for i in range(len(value)) if aggTypeDict['tag'][i] == 'aggre'}
            aTypeDict = {key: value[i-1:] for key, value in aggTypeDict.items() for i in range(len(value)) if aggTypeDict['tag'][i] == 'aggre'}
            # network trans
            update_coreTrans(write_trans_within(bef_aggTypeDict))
            # aggre trans
            if supis and not con_meais:
                c_supTypeDict = coreTypeDict['types'][supis[0]]
                update_coreTrans(gen_trans([aTypeDict['id'][0], c_supTypeDict['id'][-1]], [aTypeDict['id'][1]], c_supTypeDict['id'][-1]))
            elif not supis and not con_meais:
                agg_extent_id = coreTypeDict['types'][coreTypeDict['funcRole'].index('extent')][0]
                update_coreTrans(gen_trans([aTypeDict['id'][0]], [aTypeDict['id'][1]], agg_extent_id))
    elif aggTypeDict['tag'] == ['destination', 'origin', 'extremaR', 'networkQ', 'aggre']:
        if frole == 'measure':
            bef_aggTypeDict = {key: value[0: i] for key, value in aggTypeDict.items() for i in range(len(value)) if aggTypeDict['tag'][i] == 'aggre'}
            aTypeDict = {key: value[i-1:] for key, value in aggTypeDict.items() for i in range(len(value)) if aggTypeDict['tag'][i] == 'aggre'}
            bef_aggTypeDict['id'] = aggTypeDict['id'][0:3]
            aTypeDict['id'] = aggTypeDict['id'][-2:4]
            # network trans
            update_coreTrans(write_trans_within(bef_aggTypeDict))
            # aggre trans
            if supis and not con_meais:
                c_supTypeDict = coreTypeDict['types'][supis[0]]
                update_coreTrans(gen_trans([str(core_id-1), c_supTypeDict['id'][-1]], [aTypeDict['id'][1]],
                                           c_supTypeDict['id'][-1]))
            elif not supis and not con_meais:
                agg_extent_id = coreTypeDict['types'][coreTypeDict['funcRole'].index('extent')][0]
                update_coreTrans(gen_trans([str(core_id-1)], [aTypeDict['id'][1]], agg_extent_id))


# [X] Generate transformation for proportion in condition and measure
# allTypeDict: coreTypeDict, include functional roles and their types
# index of current functional role in coreTypeDict['funcRole']
# TypeDict that includes concepts for generating proportion transformations
def pro_trans(c_index, proTypeDict):
    global core_id
    global meais
    global supis
    global con_meais
    global coreTypeDict
    global coreConTrans

    # seperate proTypeDict into two dictionary: one includes concepts for aggre transformation, another one includes aggre as input and other concepts for proportion transformation
    if 'aggre' in proTypeDict['tag']:
        aTypeDict = {key: value[0: i + 1] for key, value in proTypeDict.items() for i in range(len(value)) if
                     proTypeDict['tag'][i] == 'aggre'}
        afte_aTypeDict = {key: value[i:] for key, value in proTypeDict.items() for i in range(len(value)) if
                          proTypeDict['tag'][i] == 'aggre'}
        if aTypeDict['tag'] == ['coreC', 'coreC', 'aggre'] and 'amount' in aTypeDict['text'][1]:
            aTypeDict = merge_aggConAmount(aTypeDict)
            afte_aTypeDict['tag'][0] = 'coreC'
            afte_aTypeDict['text'][0] = aTypeDict['text'][-1]
            afte_aTypeDict['id'][0] = aTypeDict['id'][-1]
        aggre_trans(c_index, aTypeDict)
    else:
        afte_aTypeDict = proTypeDict.copy()

    frole = coreTypeDict['funcRole'][c_index]

    if afte_aTypeDict['tag'] == ['coreC']:
        if frole == 'measure':
            if supis and not con_meais:
                m_supTypeDict = coreTypeDict['types'][supis[0]]
                update_coreTrans(gen_trans([m_supTypeDict['id'][-1], afte_aTypeDict['id'][0]], [str(core_id)], m_supTypeDict['id'][-1]))
                update_coreType(new_type(afte_aTypeDict['id'][0]))
                update_id()
            elif con_meais and not supis: # What is the crime density within the buffer area of the shortest path from home to workplace in Amsterdam
                for ci in con_meais:
                    m_ciTypeDict = coreTypeDict['types'][ci]
                    if 'distfield' in m_ciTypeDict['tag']:
                        dist_index = m_ciTypeDict['tag'].index('distfield')
                        if m_ciTypeDict['tag'][dist_index-1] == 'networkC':
                            update_coreTrans(gen_trans([m_ciTypeDict['id'][-1], afte_aTypeDict['id'][0]], [str(core_id)], str(core_id-1)))
                        else:
                            update_coreTrans(gen_trans([m_ciTypeDict['id'][-1], afte_aTypeDict['id'][0]], [str(core_id)], m_ciTypeDict['id'][dist_index]))
                        update_coreType(new_type(afte_aTypeDict['id'][0]))
                        update_id()
                    else:
                        update_coreTrans(gen_trans([m_ciTypeDict['id'][-1], afte_aTypeDict['id'][0]], [str(core_id)],
                                               m_ciTypeDict['id'][-1]))
                        update_coreType(new_type(afte_aTypeDict['id'][0]))
                        update_id()
            elif supis and con_meais:
                m_supTypeDict = coreTypeDict['types'][supis[0]]
                for ci in con_meais:
                    m_ciTypeDict = coreTypeDict['types'][ci]
                    if 'field' in m_ciTypeDict['text'][-1] or 'boolfield' in m_ciTypeDict['text'][-1] or len(m_ciTypeDict['id']) == 1:
                        update_coreTrans(gen_trans([m_ciTypeDict['id'][-1], afte_aTypeDict['id'][0]], [str(core_id)],
                                               m_ciTypeDict['id'][-1] if 'distfield' not in  m_ciTypeDict['tag'] else m_ciTypeDict['id'][m_ciTypeDict['tag'].index('distfield')]))
                        update_coreType(new_type(afte_aTypeDict['id'][0]))
                        afte_aTypeDict = update_nextid(afte_aTypeDict)
                        update_id()
                update_coreTrans(gen_trans([afte_aTypeDict['id'][0], m_supTypeDict['id'][-1]], [str(core_id)], m_supTypeDict['id'][-1]))
                update_coreType(new_type(afte_aTypeDict['id'][0]))
                update_id()
    elif afte_aTypeDict['tag'] == ['coreC', 'coreC']:
        if frole == 'measure':
            if supis and not con_meais:
                m_supTypeDict = coreTypeDict['types'][supis[0]]
                if 'amount' in afte_aTypeDict['text'][0]:  # amount * support -> new amount
                    update_coreTrans(gen_trans([afte_aTypeDict['id'][0], m_supTypeDict['id'][-1]], [str(core_id)], m_supTypeDict['id'][-1]))
                    update_coreType(new_type(afte_aTypeDict['id'][0]))
                else:  # object/event * support -> object amount, field * support -> covamount
                    update_coreTrans(gen_trans([afte_aTypeDict['id'][0], m_supTypeDict['id'][-1]], [str(core_id)],
                                               m_supTypeDict['id'][-1]))
                    update_coreType(newAmount_type(afte_aTypeDict['text'][0].split()[0], None))
                # update id for new amount
                afte_aTypeDict['id'][0] = str(core_id)
                update_id()
                # support -> support covAmount
                update_coreTrans(gen_trans([m_supTypeDict['id'][-1]], [str(core_id)], None))
                update_coreType(newAmount_type('support', None))
                # amount * support covAmount -> pro
                update_coreTrans(gen_trans([afte_aTypeDict['id'][0], str(core_id)], [afte_aTypeDict['id'][-1]], m_supTypeDict['id'][-1]))
                update_id()
            elif con_meais:
                for ci in con_meais:
                    m_ciTypeDict = coreTypeDict['types'][ci]
                    if 'amount' in afte_aTypeDict['text'][0]:
                        # amount * condition -> new amount, distfield is key
                        if 'distfield' in m_ciTypeDict['tag']:
                            dist_index = m_ciTypeDict['tag'].index('distfield')
                            update_coreTrans(gen_trans([afte_aTypeDict['id'][0], m_ciTypeDict['id'][-1]], [str(core_id)],
                                                   m_ciTypeDict['id'][dist_index]))
                        else:
                            update_coreTrans(gen_trans([afte_aTypeDict['id'][0], m_ciTypeDict['id'][-1]], [str(core_id)], m_ciTypeDict['id'][-1]))
                        # update new type and id
                        update_coreType(new_type(afte_aTypeDict['id'][0]))
                        update_id()
                        # condition and support
                        if supis:
                            m_supTypeDict = coreTypeDict['types'][supis[0]]
                            # new amount * support -> new amount2 per support
                            update_coreTrans(gen_trans([str(core_id-1), m_supTypeDict['id'][-1]], [str(core_id)], m_supTypeDict['id'][-1]))
                            update_coreType(new_type(str(core_id-1)))
                            update_id()
                            # denominator
                            if [i['keyword'] for i in coreConTrans['types'] if i['id'] == afte_aTypeDict['id'][-1]] == ['density']:
                                update_coreTrans(gen_trans([m_supTypeDict['id'][-1]], [str(core_id)], None))
                                update_coreType(newAmount_type('support', None))
                            else:
                                update_coreTrans(gen_trans([afte_aTypeDict['id'][0], m_supTypeDict['id'][-1]], [str(core_id)], m_supTypeDict['id'][-1]))
                                update_coreType(new_type(afte_aTypeDict['id'][0]))
                            # new amount2 * denominator -> density/pro
                            update_coreTrans(gen_trans([str(core_id-1), str(core_id)], [afte_aTypeDict['id'][-1]], m_supTypeDict['id'][-1]))
                            update_id()
                        # condition and no support
                        else:
                            pro_extent_id = coreTypeDict['types'][coreTypeDict['funcRole'].index('extent')][0]
                            if [i['keyword'] for i in coreConTrans['types'] if i['id'] == afte_aTypeDict['id'][-1]] == ['density']:
                                # extent -> covAmount
                                update_coreTrans(gen_trans([pro_extent_id], [str(core_id)], None))
                                update_coreType(newAmount_type('extent', None))
                                # pro
                                update_coreTrans(gen_trans([str(core_id-1), str(core_id)], [afte_aTypeDict['id'][-1]], pro_extent_id))
                                update_id()
                            else:
                                # pro
                                update_coreTrans(gen_trans([str(core_id-1), afte_aTypeDict['id'][0]], [afte_aTypeDict['id'][-1]], pro_extent_id))
                    else:
                        if supis:
                            m_supTypeDict = coreTypeDict['types'][supis[0]]
                            # new field/object/event * support-> (cov)amount
                            keywd0 = afte_aTypeDict['text'][0].split()[0]
                            update_coreTrans(gen_trans([coreConTrans['transformations'][-1]['after'][0], m_supTypeDict['id'][-1]], [str(core_id)], m_supTypeDict['id'][-1]))
                            update_coreType(newAmount_type(keywd0, None))
                            update_id()
                            # denominator
                            if [i['keyword'] for i in coreConTrans['types'] if i['id'] == afte_aTypeDict['id'][-1]] == ['density'] or keywd0 == 'field' or keywd0 == 'region':
                                update_coreTrans(gen_trans([m_supTypeDict['id'][-1]], [str(core_id)], None))
                                update_coreType(newAmount_type('support', None))
                            else:
                                update_coreTrans(gen_trans([afte_aTypeDict['id'][0], m_supTypeDict['id'][-1]], [str(core_id)],
                                              m_supTypeDict['id'][-1]))
                                update_coreType(newAmount_type(afte_aTypeDict['text'][0].split()[0], None))
                            # new amount * denominator -> density/pro
                            update_coreTrans(gen_trans([str(core_id - 1), str(core_id)], [afte_aTypeDict['id'][-1]], m_supTypeDict['id'][-1]))
                            update_id()
                        else:
                            pro_extent_id = coreTypeDict['types'][coreTypeDict['funcRole'].index('extent')][0]
                            # new field/object/event -> (cov)Amount
                            keywd0 = afte_aTypeDict['text'][0].split()[0]
                            if keywd0 != 'field' or keywd0 != 'region':
                                update_coreTrans(gen_trans(coreConTrans['transformations'][-1]['after'], [str(core_id)], None))
                            else:
                                update_coreTrans(gen_trans(coreConTrans['transformations'][-1]['after'], [str(core_id)], pro_extent_id ))
                            update_coreType(newAmount_type(keywd0, None))
                            update_id()
                            # dominator
                            if [i['keyword'] for i in coreConTrans['types'] if i['id'] == afte_aTypeDict['id'][-1]] == ['density'] or keywd0 == 'field' or keywd0 == 'region':
                                if 'distfield' in m_ciTypeDict['tag']:
                                    update_coreTrans(gen_trans([m_ciTypeDict['id'][-1]], [str(core_id)], None))
                                    update_coreType(newAmount_type('boolfield', None))
                                else:
                                    # extent -> covAmount
                                    update_coreTrans(gen_trans([pro_extent_id], [str(core_id)], None))
                                    update_coreType(newAmount_type('extent', None))
                                # pro
                                update_coreTrans(gen_trans([str(core_id-1), str(core_id)], [afte_aTypeDict['id'][-1]], pro_extent_id))
                                update_id()
                            else:
                                # pro
                                update_coreTrans(gen_trans([str(core_id-1), afte_aTypeDict['id'][0]], [afte_aTypeDict['id'][-1]], pro_extent_id))
            elif not supis and not con_meais:
                pro_extent_id = coreTypeDict['types'][coreTypeDict['funcRole'].index('extent')][0]
                # field/object/event -> (cov)Amount
                keywd0 = afte_aTypeDict['text'][0].split()[0]
                update_coreTrans(gen_trans([afte_aTypeDict['id'][0]], [str(core_id)], pro_extent_id if keywd0 != 'field' else None))
                update_coreType(newAmount_type(keywd0, None))
                update_id()
                # extent -> covAmount
                update_coreTrans(gen_trans([pro_extent_id], [str(core_id)], None))
                update_coreType(newAmount_type('extent', None))
                # pro
                update_coreTrans(gen_trans([str(core_id-1), str(core_id)], [afte_aTypeDict['id'][-1]], pro_extent_id))
                update_id()
    elif afte_aTypeDict['tag'] == ['coreC', 'coreC', 'coreC']:
        if supis and con_meais:
            m_supTypeDict = coreTypeDict['types'][supis[0]]
            for ci in con_meais:
                m_ciTypeDict = coreTypeDict['types'][ci]
                if 'amount' in afte_aTypeDict['text'][0]:
                    # 'What is the percentage of population older than 65 for each Census Consolidated Subdivision in Alberta in Canada'
                    if m_ciTypeDict['id'] == []:
                        # input * support -> new input
                        update_coreTrans(gen_trans([afte_aTypeDict['id'][0], m_supTypeDict['id'][-1]], [str(core_id)], m_supTypeDict['id'][-1]))
                        update_coreType(new_type(afte_aTypeDict['id'][0]))
                        update_id()
                        update_coreTrans(gen_trans([afte_aTypeDict['id'][1], m_supTypeDict['id'][-1]], [str(core_id)],m_supTypeDict['id'][-1]))
                        update_coreType(new_type(afte_aTypeDict['id'][1]))
                        # pro
                        update_coreTrans(gen_trans([str(core_id-1), str(core_id)], [afte_aTypeDict['id'][-1]], m_supTypeDict['id'][-1]))
                        update_id()
        elif supis and not con_meais:
            m_supTypeDict = coreTypeDict['types'][supis[0]]
            # coreC * support -> coreC or amount
            update_coreTrans(gen_trans([afte_aTypeDict['id'][1], m_supTypeDict['id'][-1]], [str(core_id)], m_supTypeDict['id'][-1]))
            # pro
            update_coreTrans(gen_trans([str(core_id), afte_aTypeDict['id'][0]], [afte_aTypeDict['id'][-1]], m_supTypeDict['id'][-1]))
            if 'amount' in afte_aTypeDict['text'][1]:
                update_coreType(new_type(afte_aTypeDict['id'][1]))
            else:
                update_coreType(newAmount_type(afte_aTypeDict['text'][1].split()[0], None))
            update_id()
        elif not supis and not con_meais:
            pro_extent_id = coreTypeDict['types'][coreTypeDict['funcRole'].index('extent')][0]
            if 'amount' not in afte_aTypeDict['text'][1]:
                update_coreTrans(gen_trans([afte_aTypeDict['id'][1], pro_extent_id], [str(core_id)], pro_extent_id))
                update_coreType(newAmount_type(afte_aTypeDict['text'][1].split()[0], None))
                afte_aTypeDict['id'][1] = str(core_id)
                update_id()
            update_coreTrans(gen_trans(afte_aTypeDict['id'][0:2], [afte_aTypeDict['id'][-1]], pro_extent_id))
    elif afte_aTypeDict['tag'] == ['aggre', 'coreC', 'coreC']:
        if frole == 'condition':
            # coreC + measure input -> new coreC with measure input as key
            cur_mTypeDict = coreTypeDict['types'][meais[0]]
            coreC_input = [afte_aTypeDict['id'][1], cur_mTypeDict['id'][0]]
            trans_coreC = gen_trans(coreC_input, [str(core_id)], cur_mTypeDict['id'][0])
            update_coreTrans(trans_coreC)
            # add new amount type
            new_amou = afte_aTypeDict['text'][1].split()[0]
            if new_amou in ['object', 'field', 'event']:
                update_coreType(newAmount_type(new_amou, None))
            else:
                update_coreType(new_type(afte_aTypeDict['id'][1]))
            # update coreC ID for next step
            afte_aTypeDict['id'][1] = str(core_id)
            update_id()
            # proportion trans
            update_coreTrans(
                gen_trans(afte_aTypeDict['id'][0:2][::-1], [afte_aTypeDict['id'][-1]], cur_mTypeDict['id'][0]))
        if frole == 'measure':
            if supis and not con_meais:
                m_supTypeDict = coreTypeDict['types'][supis[0]]
                # coreC * support -> coreC or amount
                update_coreTrans(gen_trans([afte_aTypeDict['id'][1], m_supTypeDict['id'][-1]], [str(core_id)], m_supTypeDict['id'][-1]))
                # pro
                update_coreTrans(gen_trans([str(core_id), afte_aTypeDict['id'][0]], [afte_aTypeDict['id'][-1]], m_supTypeDict['id'][-1]))
                if 'amount' in afte_aTypeDict['text'][1]:
                    update_coreType(new_type(afte_aTypeDict['id'][1]))
                else:
                    update_coreType(newAmount_type(afte_aTypeDict['text'][1].split()[0], None))
                update_id()


# [X] Generate transformation for conAmount in condition and measure
# allTypeDict: coreTypeDict, include functional roles and their types
# index of current functional role in coreTypeDict['funcRole']
# TypeDict that includes concepts for generating conAmount transformations
def conAmount_trans(c_index, conATypeDict):
    global core_id
    global meais
    global supis
    global con_meais
    global coreTypeDict

    frole = coreTypeDict['funcRole'][c_index]

    # 'tag': ['coreC', 'conAmount']
    if frole == 'condition' or frole == 'subcon':
        nextTypeDict = coreTypeDict['types'][c_index+1]
        update_coreTrans(gen_trans([conATypeDict['id'][0]], [conATypeDict['id'][-1]], nextTypeDict['id'][0]))

    if frole == 'measure':
        if conATypeDict['tag'] == ['coreC']:
            if con_meais and not supis:
                conA_extent_id = coreTypeDict['types'][coreTypeDict['funcRole'].index('extent')][0]
                for ci in con_meais:
                    m_ciTypeDict = coreTypeDict['types'][ci]
                    update_coreTrans(gen_trans([conATypeDict['id'][0], m_ciTypeDict['id'][-1]], [str(core_id)], conA_extent_id if 'distfield' not in m_ciTypeDict['tag'] else m_ciTypeDict['id'][m_ciTypeDict['tag'].index('distfield')]))
                    update_coreType(new_type(conATypeDict['id'][0]))
                    conATypeDict['id'][0] = str(core_id)
                    update_id()
            elif supis and not con_meais:
                # What is the WOZ-waarde for each neighborhood in Amsterdam
                m_supTypeDict = coreTypeDict['types'][supis[0]]
                update_coreTrans(gen_trans([conATypeDict['id'][0], m_supTypeDict['id'][-1]], [str(core_id)], m_supTypeDict['id'][-1]))
                update_coreType(new_type(conATypeDict['id'][0]))
                update_id()
            elif not supis and not con_meais:
                conA_extent_id = coreTypeDict['types'][coreTypeDict['funcRole'].index('extent')][0]
                update_coreTrans(gen_trans([conATypeDict['id'][0]], [str(core_id)],
                                           conA_extent_id))
                update_coreType(new_type(conATypeDict['id'][0]))
                update_id()
            elif con_meais and supis:
                for ci in con_meais:
                    m_ciTypeDict = coreTypeDict['types'][ci]
                    update_coreTrans(gen_trans([conATypeDict['id'][0], m_ciTypeDict['id'][-1]], [str(core_id)], m_ciTypeDict['id'][-1] if 'distfield' not in m_ciTypeDict['tag'] else
                                               m_ciTypeDict['id'][m_ciTypeDict['tag'].index('distfield')]))
                    update_coreType(new_type(conATypeDict['id'][0]))
                    conATypeDict['id'][0] = str(core_id)
                    update_id()
                m_supTypeDict = coreTypeDict['types'][supis[0]]
                update_coreTrans(gen_trans([conATypeDict['id'][0], m_supTypeDict['id'][-1]], [str(core_id)], m_supTypeDict['id'][-1]))
                update_coreType(new_type(conATypeDict['id'][0]))
                update_id()
        elif conATypeDict['tag'] == ['coreC','coreC']:
            if con_meais and not supis:
                conA_extent_id = coreTypeDict['types'][coreTypeDict['funcRole'].index('extent')][0]
                for ci in con_meais:
                    m_ciTypeDict = coreTypeDict['types'][ci]
                    if 'distfield' in m_ciTypeDict['id'] or 'serviceobj' in m_ciTypeDict['id']:
                        update_coreTrans(gen_trans([conATypeDict['id'][0], m_ciTypeDict['id'][-1]], [str(core_id)], None))
                        update_coreType(new_type(conATypeDict['id'][0]))
                        conATypeDict['id'][0] = str(core_id)
                        update_id()
                # new input -> conAmount
                update_coreTrans(gen_trans([conATypeDict['id'][0]], [conATypeDict['id'][1]], conA_extent_id))
            elif supis and not con_meais:
                m_supTypeDict = coreTypeDict['types'][supis[0]]
                update_coreTrans(gen_trans([conATypeDict['id'][0], m_supTypeDict['id'][-1]], [conATypeDict['id'][-1]], m_supTypeDict['id'][-1]))
            elif not supis and not con_meais:
                conA_extent_id = coreTypeDict['types'][coreTypeDict['funcRole'].index('extent')][0]
                update_coreTrans(gen_trans([conATypeDict['id'][0]], [conATypeDict['id'][1]], conA_extent_id))


# [X] Generate core concept transformations within condition, measure...
# Input TypeDict = {'tag': ['coreC', 'distField', 'boolField'], 'text': ['object 1', 'from', ''], 'id': ['1', '2', '3']}
# Output [{'before': ['1'], 'after': ['2']}, {'before': ['2'], 'after': ['3']}]
def write_trans_within(TypeDict):
    global core_id
    global coreConTrans
    global measureType
    transwithin = []
    coreC_sign = 0
    net_sign = 0

    for tt in TypeDict['tag']:
        if (tt == 'boolfield' and 'serviceobj' not in TypeDict['tag']) or tt == 'allocation' or tt == 'conAm':
            if TypeDict['tag'].index(tt) - 1 >= 0:
                trans = {}
                trans['before'] = [TypeDict['id'][TypeDict['tag'].index(tt) - 1]]
                trans['after'] = [TypeDict['id'][TypeDict['tag'].index(tt)]]
                transwithin.append(trans)
        elif tt == 'distfield':
            if TypeDict['tag'].index(tt) - 1 >= 0:
                cur_tag = TypeDict['tag'][TypeDict['tag'].index(tt) - 1]
                if cur_tag == 'networkC':  # networkC -> object -> distField
                    trans_net = {}
                    trans_net['before'] = [TypeDict['id'][TypeDict['tag'].index(tt) - 1]]
                    trans_net['after'] = [str(core_id)]
                    transwithin.append(trans_net)
                    # add object in types
                    dist_index = [i for i, j in enumerate(coreConTrans['types']) if j['type'] == 'distfield'][0]
                    coreConTrans.setdefault('types', []).append({'type': 'object', 'id': str(core_id),
                                                                 'keyword': coreConTrans['types'][dist_index - 1][
                                                                     'keyword']})
                    # object -> distField
                    trans = {}
                    trans['before'] = [str(core_id)]
                    trans['after'] = [TypeDict['id'][TypeDict['tag'].index(tt)]]
                    transwithin.append(trans)
                    update_id()
                elif cur_tag == 'coreC':
                    trans = {}
                    trans['before'] = [TypeDict['id'][TypeDict['tag'].index(tt) - 1]]
                    trans['after'] = [TypeDict['id'][TypeDict['tag'].index(tt)]]
                    transwithin.append(trans)
        elif tt == 'location' and 'allocation' not in TypeDict['tag']:
            if 'extremaR' in TypeDict['tag']:
                trans = {}
                trans['before'] = [TypeDict['id'][TypeDict['tag'].index(tt) - 2]]
                trans['after'] = [TypeDict['id'][TypeDict['tag'].index(tt) - 1]]
            else:
                trans = {}
                trans['before'] = [TypeDict['id'][TypeDict['tag'].index(tt) - 1]]
                trans['after'] = [TypeDict['id'][TypeDict['tag'].index(tt)]]
            transwithin.append(trans)
        elif tt == 'serviceobj':
            s_in = TypeDict['tag'].index(tt)
            trans = {}
            if s_in - 2 >= 0 and TypeDict['tag'][s_in - 2] == 'destination':
                if s_in - 3 >= 0 and TypeDict['tag'][s_in - 3] == 'origin':  # ['origin', 'destination', 'networkQ', 'serviceObj'], remove 'roadData'
                    if len(TypeDict['id'][s_in - 3]) == 2:  # [['grid', 'centroid'], 'destination', 'networkC', 'serviceObj'], remove 'roadData'
                        trans['before'] = [TypeDict['id'][s_in - 3][0]]
                        trans['after'] = [TypeDict['id'][s_in - 3][1]]
                        transwithin.append(trans)
                    # origin: TypeDict['id'][s_in - 3], destination: TypeDict['id'][s_in - 2], remove roadData
                    # networkC is not used here.
                    trans = {}
                    trans['before'] = [TypeDict['id'][s_in - 3][-1], TypeDict['id'][s_in - 2][-1]]
                    trans['after'] = [TypeDict['id'][s_in - 1]]
                    transwithin.append(trans)
                    # driving time -> 1 min driving time
                    trans_service = {}
                    trans_service['before'] = [TypeDict['id'][s_in - 1]]
                    trans_service['after'] = [str(core_id)]
                    transwithin.append(trans_service)
                    update_coreType(new_type(trans_service['before'][0]))
                    update_id()
                    # network quality -> object
                    trans_ori ={}
                    trans_ori['before'] = [str(core_id-1)]
                    trans_ori['after'] = [str(core_id)]
                    transwithin.append(trans_ori)
                    update_coreType(new_type(TypeDict['id'][s_in - 3][-1]))
                    update_id()
                else:   # ['destination', 'networkQ', 'serviceObj', ...]
                    if len(TypeDict['id'][s_in - 2]) == 2:  # [['grid', 'centroid'], 'networkC', 'serviceObj']
                        trans['before'] = [TypeDict['id'][s_in - 2][0]]
                        trans['after'] = [TypeDict['id'][s_in - 2][1]]
                        transwithin.append(trans)
                    # destination, measure_obj -> driving time
                    trans = {}
                    trans['before'] = [TypeDict['id'][s_in - 2][-1], measureType['id'][0]]
                    trans['after'] = [TypeDict['id'][s_in - 1]]
                    transwithin.append(trans)
                    # driving time -> 1 min driving time
                    trans_service = {}
                    trans_service['before'] = [TypeDict['id'][s_in - 1]]
                    trans_service['after'] = [str(core_id)]
                    transwithin.append(trans_service)
                    update_coreType(new_type(trans_service['before'][0]))
                    update_id()
                    # network quality -> object
                    trans_des = {}
                    trans_des['before'] = [str(core_id - 1)]
                    trans_des['after'] = [str(core_id)]
                    transwithin.append(trans_des)
                    update_coreType(new_type(measureType['id'][0]))
                    measureType['id'][0] = str(core_id)
                    update_id()
            elif s_in - 2 >= 0 and TypeDict['tag'][s_in - 2] == 'origin':  # ['origin', 'networkC', 'serviceObj'], remove 'roadData'
                if len(TypeDict['id'][s_in - 2]) == 2:  # [['grid', 'centroid'], 'networkC', 'serviceObj'], remove 'roadData'
                    trans['before'] = [TypeDict['id'][s_in - 2][0]]
                    trans['after'] = [TypeDict['id'][s_in - 2][1]]
                    transwithin.append(trans)
                # origin, measure_obj -> driving time
                trans = {}
                trans['before'] = [TypeDict['id'][s_in - 2][-1], measureType['id'][0]]
                trans['after'] = [TypeDict['id'][s_in - 1]]
                transwithin.append(trans)
                # driving time -> 1 min driving time
                trans_ser = {}
                trans_ser['before'] = [TypeDict['id'][s_in - 1]]
                trans_ser['after'] = [str(core_id)]
                transwithin.append(trans_ser)
                update_coreType(new_type(trans_ser['before'][0]))
                update_id()
                # network quality -> object
                trans_ori = {}
                trans_ori['before'] = [str(core_id - 1)]
                trans_ori['after'] = [str(core_id)]
                transwithin.append(trans_ori)
                update_coreType(new_type(measureType['id'][0]))
                measureType['id'][0] = str(core_id)
                update_id()
        elif ((tt == 'networkC' and 'networkQ' not in TypeDict['tag']) or (
                tt == 'networkQ' and 'networkC' not in TypeDict['tag']) or tt =='objectQ') and (
                'destination' in TypeDict['tag'] or 'origin' in TypeDict['tag']) and 'serviceobj' not in TypeDict[
            'tag'] and TypeDict['tag'][-2:] != ['networkC', 'networkC']:
            n_in = TypeDict['tag'].index(tt)
            trans = {}
            if 'destination' in TypeDict['tag']:
                desti_loc = TypeDict['tag'].index('destination')
                if 'origin' in TypeDict['tag']:  # ['origin', 'destination', 'networkC'] //'roadData',
                    orig_loc = TypeDict['tag'].index('origin')
                    if len(TypeDict['id'][
                               orig_loc]) == 2:  # [['grid', 'centroid'], 'destination', 'networkC'] //'roadData'
                        trans['before'] = [TypeDict['id'][orig_loc][0]]
                        trans['after'] = [TypeDict['id'][orig_loc][1]]
                        transwithin.append(trans)
                    # origin: TypeDict['id'][n_in - 2], destination: TypeDict['id'][n_in - 1], // remove roadData:TypeDict['id'][n_in - 1]
                    trans = {}
                    if type(TypeDict['id'][desti_loc]) == list:
                        desti_idlist = TypeDict['id'][desti_loc][:]
                        desti_idlist.append(TypeDict['id'][orig_loc][-1])
                        trans['before'] = desti_idlist
                    elif type(TypeDict['id'][desti_loc]) == str:
                        desti_id = TypeDict['id'][desti_loc][:]
                        orig_id = TypeDict['id'][orig_loc][-1]
                        trans['before'] = [desti_id, orig_id]
                    if 'extremaR' in TypeDict['tag']:
                        trans['after'] = [TypeDict['id'][n_in-1]]
                    else:
                        trans['after'] = [TypeDict['id'][n_in]]
                    transwithin.append(trans)
                    if 'extremaR' in TypeDict['tag'] and tt == 'networkQ':
                        ex_trans = {}
                        ex_trans['before'] = trans['after']
                        ex_trans['after'] = [str(core_id)]
                        ex_trans['key'] = TypeDict['id'][orig_loc][-1]
                        transwithin.append(ex_trans)
                        ex_index = [i for i in range(0,len(coreConTrans['types'])) if coreConTrans['types'][i]['id'] == trans['after'][0]][0]
                        update_coreType(newAmount_type('networkquality', coreConTrans['types'][ex_index]['keyword']))
                        update_id()
                    elif tt == 'networkC':
                        netC_keywd_in = [i for i in range(0, len(coreConTrans['types'])) if coreConTrans['types'][i]['id'] == trans['after'][0]][0]
                        if TypeDict != measureType:
                            s_trans={}
                            s_trans['before'] = trans['after']
                            s_trans['after'] = [str(core_id)]
                            transwithin.append(s_trans)
                            update_coreType(newAmount_type('network', coreConTrans['types'][netC_keywd_in]['keyword']))
                            update_id()
                else:  # ['destination', 'networkC'] //'roadData'
                    trans['before'] = TypeDict['id'][desti_loc]
                    if 'extremaR' in TypeDict['tag']:
                        trans['after'] = [TypeDict['id'][n_in - 1]]
                    else:
                        trans['after'] = [TypeDict['id'][n_in]]
                    transwithin.append(trans)
            elif n_in - 1 >= 0 and TypeDict['tag'][n_in - 1] == 'origin':  # ['origin', 'networkC'] //'roadData',
                if len(TypeDict['id'][n_in - 1]) == 2:  # [['grid', 'centroid'], 'networkC'] //'roadData',
                    trans['before'] = [TypeDict['id'][n_in - 1][0]]
                    trans['after'] = [TypeDict['id'][n_in - 1][1]]
                    transwithin.append(trans)
                trans = {}
                trans['before'] = [TypeDict['id'][n_in - 1][-1]]
                if 'extremaR' in TypeDict['tag']:
                    trans['after'] = [TypeDict['id'][n_in - 1]]
                else:
                    trans['after'] = [TypeDict['id'][n_in]]
                transwithin.append(trans)
        elif tt == 'networkC' and TypeDict['tag'] == ['destination', 'origin', 'networkC', 'networkC']:
            if net_sign == 1:
                continue
            else:
                n_in = TypeDict['tag'].index(tt)
                trans = {}
                desti_loc = TypeDict['tag'].index('destination')
                orig_loc = TypeDict['tag'].index('origin')
                desti_idlist = TypeDict['id'][desti_loc][:]
                desti_idlist.append(TypeDict['id'][orig_loc][-1])
                desti_idlist.append(TypeDict['id'][2])
                trans['before'] = desti_idlist
                trans['after'] = [TypeDict['id'][-1]]
                transwithin.append(trans)
                net_sign += 1
        elif (tt == 'networkQ') and ('networkC' in TypeDict['tag']):
            if TypeDict['tag'] == ['networkC', 'networkQ']:
                trans = {}
                trans['before'] = [TypeDict['id'][0]]
                trans['after'] = [TypeDict['id'][1]]
                transwithin.append(trans)
            else:
                n_in = TypeDict['tag'].index(tt)
                trans = {}
                if 'destination' in TypeDict['tag']:
                    desti_loc = TypeDict['tag'].index('destination')
                    networkC_loc = TypeDict['tag'].index('networkC')
                    dest_list = TypeDict['id'][desti_loc][:]
                    networkC_id = TypeDict['id'][networkC_loc]
                    dest_list.append(networkC_id)
                    trans['before'] = dest_list
                    trans['after'] = [TypeDict['id'][n_in]]
                    transwithin.append(trans)
        elif tt == 'mergeO':
            mergeTrans = {}
            mergeTrans['before'] = TypeDict['id'][:-1]
            mergeTrans['after'] = [TypeDict['id'][-1]]
            transwithin.append(mergeTrans)
        elif tt == 'coreC' and 'serviceobj' not in TypeDict['tag'] and 'networkC' not in TypeDict[
            'tag'] and 'mergeO' not in TypeDict['tag']:
            trans = {}
            if 'destination' in TypeDict['tag']:
                if 'origin' in TypeDict['tag']:  # access score
                    oin = TypeDict['tag'].index('origin')
                    if len(TypeDict['id'][oin]) == 2:
                        trans['before'] = [TypeDict['id'][oin][0]]
                        trans['after'] = [TypeDict['id'][oin][1]]
                        transwithin.append(trans)
                    trans = {}
                    trans['before'] = [TypeDict['id'][oin][-1],
                                       TypeDict['id'][TypeDict['tag'].index('destination')][-1]]
                    trans['after'] = [TypeDict['id'][TypeDict['tag'].index('coreC')]]
                    transwithin.append(trans)
                elif 'origin' not in TypeDict['tag']:  # Euclidean distance to object
                    trans = {}
                    trans['before'] = [TypeDict['id'][TypeDict['tag'].index('destination')][-1]]
                    trans['after'] = [TypeDict['id'][TypeDict['tag'].index('coreC')]]
                    transwithin.append(trans)
            else:
                if coreC_sign == 1:
                    continue
                else:
                    coreC_loc = [x for x, y in enumerate(TypeDict['tag']) if y == 'coreC']
                    for coreC_l in coreC_loc:
                        if coreC_l < coreC_loc[-1]:
                            trans = {}
                            trans['before'] = [TypeDict['id'][coreC_l]]
                            trans['after'] = [TypeDict['id'][coreC_l + 1]]
                            transwithin.append(trans)
                coreC_sign = 1

    if 'networkC' in TypeDict['tag'] and TypeDict['tag'].index('networkC') + 1 < len(TypeDict['tag']) and \
            TypeDict['tag'][TypeDict['tag'].index('networkC') + 1] == 'coreC':
        net_index = TypeDict['tag'].index('networkC')
        trans = {}
        trans['before'] = [TypeDict['id'][net_index]]
        trans['after'] = [TypeDict['id'][net_index + 1]]
        transwithin.append(trans)

    return transwithin


# Input coreTypeDict = coreTypes:
#   {'funcRole': ['condition', 'condition', 'measure', 'extent', 'temEx'],
# 	 'types': [{'tag': ['coreC', 'distField', 'boolField'], 'text': ['object 1', 'from', ''], 'id': ['0', '1', '2']},
# 			   {'tag': ['coreC'], 'text': ['objectquality 0 boolean'], 'id': ['3']},
# 			   {'tag': ['coreC'], 'text': ['object 0'], 'id': ['4']},
# 			   ['Utrecht'],
# 			   ['2030']]}
# coreTransType = coreConTrans
#   {'types': [{'type':'object', 'id':'0', keyword:'district'},
#              {'type':'distField', 'id':'1', keyword:''},
#              {'type':'boolField', 'id':'2', keyword:''},
#               ...]}
def write_trans(parsedResult):
    try:
        parseTree = parsedResult[0]
        global coreTypeDict
        coreTypeDict = parsedResult[1]
        global coreConTrans
        coreConTrans = parsedResult[2]
        global core_id
        core_id = parsedResult[3]
        global measureType
        # coretrans = []  # save all the transformation steps

        # functional roles index
        subis = []
        conis = []
        con_supis = []
        global supis
        supis = []
        global meais
        meais = []
        global mea1is
        mea1is = []
        global con_meais
        con_meais = []

        if 'subcon' in coreTypeDict['funcRole']:
            subis = [x for x, y in enumerate(coreTypeDict['funcRole']) if y == 'subcon']
        if 'condition' in coreTypeDict['funcRole']:
            conis = [x for x, y in enumerate(coreTypeDict['funcRole']) if
                     (y == 'condition' and coreTypeDict['types'][x]['tag'])]
        if 'support' in coreTypeDict['funcRole']:
            supis = [x for x, y in enumerate(coreTypeDict['funcRole']) if y == 'support']
        if 'measure' in coreTypeDict['funcRole']:
            meais = [x for x, y in enumerate(coreTypeDict['funcRole']) if y == 'measure']
            measureType = coreTypeDict['types'][meais[0]]
        if 'measure1' in coreTypeDict['funcRole']:
            mea1is = [x for x, y in enumerate(coreTypeDict['funcRole']) if y == 'measure1']

        if supis:
            conar = np.array(conis)
            supar = np.array(supis)
            con_supis = list(conar[conar < supar])
            con_meais = [x for x in conis if x not in con_supis]
        else:
            con_meais = conis

        if subis:
            subTypeDict = coreTypeDict['types'][subis[0]]
            cur_conTypeDict = coreTypeDict['types'][con_meais[0]]
            if subTypeDict['tag'] == ['coreC']:
                if 'amount' not in cur_conTypeDict['text'][0] and 'pro' not in cur_conTypeDict['text'][0] and 'aggre' not in \
                        cur_conTypeDict['text'][0]:
                    update_coreTrans(gen_trans([cur_conTypeDict['id'][0], subTypeDict['id'][0]], [str(core_id)], None))
                    update_coreType(new_type(cur_conTypeDict['id'][0]))
                    cur_conTypeDict['id'][0] = str(core_id)
                    update_id()
            elif 'compareR' in subTypeDict['tag']:
                comR_trans(subis[0], subis[0] + 1)
            elif 'extremaR' in subTypeDict['tag']:
                if subTypeDict['text'][1] == 'closest to':
                    # distance trans
                    update_coreTrans(gen_trans([cur_conTypeDict['id'][0], subTypeDict['id'][0]], [str(core_id)], None))
                    update_coreType(newAmount_type('distance', None))
                    update_id()
                    # because of "closest to", group by trans
                    update_coreTrans(gen_trans([str(core_id-1)], [str(core_id)], cur_conTypeDict['id'][0]))
                    update_coreType(newAmount_type('networkquality', None))
                    update_id()
                    # condition input * distance -> new condition input
                    update_coreTrans(gen_trans([str(core_id - 1)], [str(core_id)], None))
                    update_coreType(new_type(cur_conTypeDict['id'][0]))
                    cur_conTypeDict['id'][0] = str(core_id)
                    update_id()
                else:
                    extR_trans(subis[0], subis[0] + 1)
            else:
                sub_trans = write_trans_within(subTypeDict)
                if sub_trans:
                    update_coreTrans(sub_trans)
                # update condition input
                if coreTypeDict['funcRole'][subis[0] + 1] == 'condition':
                    input_sub_con = [coreTypeDict['types'][subis[0] + 1]['id'][0],
                                     coreTypeDict['types'][subis[0]]['id'][-1]]
                    if 'amount' in coreTypeDict['types'][subis[0] + 1]['text'][0] and 'distfield' in \
                            coreTypeDict['types'][subis[0]]['tag']:
                        distf_index = coreTypeDict['types'][subis[0]]['tag'].index('distfield')
                        update_coreTrans(gen_trans(input_sub_con, [str(core_id)],
                                                   coreTypeDict['types'][subis[0]]['id'][distf_index]))
                    else:
                        update_coreTrans(gen_trans(input_sub_con, [str(core_id)], None))
                    update_coreType(new_type(coreTypeDict['types'][subis[0] + 1]['id'][0]))
                    # update condition input id for next trans
                    coreTypeDict['types'][subis[0] + 1]['id'][0] = str(core_id)
                    update_id()

        if con_supis:
            consupTypeDict = coreTypeDict['types'][con_supis[0]]
            supTypeDict = coreTypeDict['types'][supis[0]]
            if 'compareR' in consupTypeDict['tag']:
                comR_trans(con_supis[0], supis[0])
            elif 'extremaR' in consupTypeDict['tag']:
                extR_trans(con_supis[0], supis[0])
            elif consupTypeDict['tag'][-1] == 'conAmount' and 'compareR' not in consupTypeDict['tag'] and 'extremaR' not in consupTypeDict['tag']:
                conAmount_trans(con_supis[0], consupTypeDict)
                # support * con_sup = support_u
                update_coreTrans(gen_trans([supTypeDict['id'][0], consupTypeDict['id'][-1]], [str(core_id)], None))
                update_coreType(new_type(supTypeDict['id'][0]))
                # update support id
                supTypeDict['id'][0] = str(core_id)
                # update core_id
                update_id()
            elif len(coreTypeDict['types'][con_supis[0]]['tag']) > 1:
                update_coreTrans(write_trans_within(consupTypeDict))
                # support * con_sup = support_u
                update_coreTrans(gen_trans([supTypeDict['id'][0], consupTypeDict['id'][-1]], [str(core_id)], None))
                update_coreType(new_type(supTypeDict['id'][0]))
                # update support id
                supTypeDict['id'][0] = str(core_id)
                # update core_id
                update_id()

        if con_meais:
            for ci in con_meais:
                conTypeDict = coreTypeDict['types'][ci]
                cur_mTypeDict = coreTypeDict['types'][meais[0]]
                if conTypeDict['tag'] == ['coreC']:
                    if 'amount' not in cur_mTypeDict['text'][0] and 'pro' not in cur_mTypeDict['text'][0] and 'aggre' not in cur_mTypeDict['text'][0]:
                        update_coreTrans(gen_trans([cur_mTypeDict['id'][0], conTypeDict['id'][0]], [str(core_id)], None))
                        update_coreType(new_type(cur_mTypeDict['id'][0]))
                        cur_mTypeDict['id'][0] = str(core_id)
                        update_id()
                elif conTypeDict['tag'] == ['visible']:
                    update_coreTrans(gen_trans([cur_mTypeDict['id'][0], conTypeDict['id'][0]], [str(core_id)], None))
                    update_coreType(newAmount_type('visibility', 'visibility surface'))
                elif 'compareR' in conTypeDict['tag']:
                    comR_trans(ci, meais[0])
                elif 'extremaR' in conTypeDict['tag']:
                    if len(conTypeDict['text']) > 1 and conTypeDict['text'][1] == 'closest to':
                        # distance trans
                        update_coreTrans(gen_trans([cur_mTypeDict['id'][0], conTypeDict['id'][0]], [str(core_id)], None))
                        update_coreType(newAmount_type('distance', None))
                        update_id()
                        # because of "closest to", group by networkquality into objectquality
                        update_coreTrans(gen_trans([str(core_id - 1)], [str(core_id)], cur_mTypeDict['id'][0]))
                        update_coreType(newAmount_type('networkquality', None))
                        update_id()
                        # objectquality -> new object
                        update_coreTrans(gen_trans([str(core_id - 1)], [str(core_id)], None))
                        update_coreType(new_type(cur_mTypeDict['id'][0]))
                        cur_mTypeDict['id'][0] = str(core_id)
                        update_id()
                    else:
                        extR_trans(ci, meais[0])
                elif conTypeDict['tag'][-1] == 'conAmount' and 'compareR' not in conTypeDict['tag'] and 'extremaR' not in conTypeDict['tag']:
                    conAmount_trans(ci, conTypeDict)
                    # update measure
                    update_coreTrans(gen_trans([cur_mTypeDict['id'][0], conTypeDict['id'][-1]], [str(core_id)], None))
                    update_coreType(new_type(cur_mTypeDict['id'][0]))
                    cur_mTypeDict['id'][0] = str(core_id)
                    update_id()
                elif len(conTypeDict['id']) > 1 and 'compareR' not in conTypeDict['tag'] and 'extremaR' not in conTypeDict['tag'] and 'conAmount' not in conTypeDict['tag']:
                    meainp_index = [i for i in range(0, len(coreConTrans['types'])) if coreConTrans['types'][i]['id'] == cur_mTypeDict['id'][0]][0]
                    if ('object' in conTypeDict['text'][0] or 'event' in conTypeDict['text'][0]) and ('object' in cur_mTypeDict['text'][0] or 'event' in cur_mTypeDict['text'][0]) \
                            and 'boolfield' in conTypeDict['tag'] and 'district' not in coreConTrans['types'][meainp_index]['keyword']:
                        # Which neighborhoods are within 100 meters from a school in Utrecht
                        update_coreTrans(gen_trans([conTypeDict['id'][0], cur_mTypeDict['id'][0]], [str(core_id)], None))
                        update_coreType(newAmount_type('distance', None))
                        update_id()
                        # distance -> new distance
                        update_coreTrans(gen_trans([str(core_id-1)], [str(core_id)], None))
                        update_coreType(newAmount_type('distance', None))
                        update_id()
                        # new distance -> object
                        update_coreTrans(gen_trans([str(core_id - 1)], [str(core_id)], None))
                        update_coreType(new_type(cur_mTypeDict['id'][0]))
                        cur_mTypeDict['id'][0] = str(core_id)
                        update_id()
                        remove_boolid(conTypeDict)
                    else:
                        con_trans = write_trans_within(conTypeDict)
                        update_coreTrans(con_trans)
                        if 'serviceobj' in conTypeDict['tag'] or conTypeDict['tag'][-1] == 'networkC':
                            conTypeDict['id'][-1] = con_trans[-1]['after'][0]
                        if 'amount' not in cur_mTypeDict['text'][0] and 'pro' not in cur_mTypeDict['text'][0] and 'aggre' not in cur_mTypeDict['text'][0]:
                            if 'region' in cur_mTypeDict['text'][0] and 'serviceobj' not in conTypeDict['tag']:
                                # cur_mTypeDict['id'][0] = str(core_id)
                                update_coreTrans(gen_trans([conTypeDict['id'][-1]], [cur_mTypeDict['id'][0]], None))
                            elif 'region' not in cur_mTypeDict['text'][0] and 'serviceobj' not in conTypeDict['tag']:
                                con_mea_trans = gen_trans([cur_mTypeDict['id'][0], conTypeDict['id'][-1]], [str(core_id)], None)
                                update_coreTrans(con_mea_trans)
                                update_coreType(new_type(cur_mTypeDict['id'][0]))
                                cur_mTypeDict['id'][0] = str(core_id)
                                update_id()

        if meais:
            m0TypeDict = coreTypeDict['types'][meais[0]]
            if mea1is:
                m1TypeDict = coreTypeDict['types'][mea1is[0]]
                m1TypeDict = merge_aggConAmount(m1TypeDict)
                for i in m0TypeDict:
                    for j in m1TypeDict[i]:
                        m0TypeDict[i].insert(-1, j)
            meaTypeDict = m0TypeDict
            if 'pro' in meaTypeDict['text'][-1]:
                pro_trans(meais[0], meaTypeDict)
            elif 'conamount' in meaTypeDict['text'][-1]:
                conAmount_trans(meais[0], meaTypeDict)
            elif 'covamount' in meaTypeDict['text'][-1]:
                if meaTypeDict['tag'] == ['coreC', 'coreC']:
                    if not supis and not con_meais:
                        update_coreTrans(gen_trans([meaTypeDict['id'][0]], [meaTypeDict['id'][1]], None))
                    elif supis and not con_meais:
                        m_supTypeDict = coreTypeDict['types'][supis[0]]
                        update_coreTrans(gen_trans([meaTypeDict['id'][0], m_supTypeDict['id'][-1]], [meaTypeDict['id'][1]], None))
                    elif not supis and con_meais:
                        # new input -> covamount
                        update_coreTrans(gen_trans([meaTypeDict['id'][0]], [meaTypeDict['id'][1]], None))
                elif meaTypeDict['tag'] == ['coreC', 'coreC', 'coreC']:
                    if supis and not con_meais:
                        m_supTypeDict = coreTypeDict['types'][supis[0]]
                        update_coreTrans(gen_trans([meaTypeDict['id'][0], meaTypeDict['id'][1], m_supTypeDict['id'][-1]], [meaTypeDict['id'][-1]], None))
                    elif not supis and not con_meais:
                        update_coreTrans(gen_trans(meaTypeDict['id'][0:2], [meaTypeDict['id'][-1]], None))
                elif meaTypeDict['tag'] == ['coreC', 'aggre', 'coreC', 'coreC'] or meaTypeDict['tag'] == ['coreC', 'coreC', 'coreC', 'coreC']:
                    if not supis and not con_meais:
                        # aggre trans
                        update_coreTrans(gen_trans([meaTypeDict['id'][0], meaTypeDict['id'][2]], [meaTypeDict['id'][1]], meaTypeDict['id'][2]))
                        # aggre, coreC -> covA
                        update_coreTrans(gen_trans([meaTypeDict['id'][2], meaTypeDict['id'][1]], [meaTypeDict['id'][-1]], None))
            elif 'aggre' in meaTypeDict['text'][-1]:
                aggre_trans(meais[0], meaTypeDict)
            else:
                if supis and not con_meais:
                    m_supTypeDict = coreTypeDict['types'][supis[0]]
                    if meaTypeDict['tag'] == ['coreC']:
                        update_coreTrans(gen_trans([meaTypeDict['id'][0], m_supTypeDict['id'][-1]], [str(core_id)], m_supTypeDict['id'][-1]))
                        update_coreType(new_type(meaTypeDict['id'][0]))
                        update_id()
                    elif meaTypeDict['tag'] == ['coreC', 'coreC']:
                        update_coreTrans(gen_trans([meaTypeDict['id'][0], m_supTypeDict['id'][-1]], [meaTypeDict['id'][1]],
                                                   m_supTypeDict['id'][-1]))
                    elif meaTypeDict['tag'] == ['networkC', 'objectQ']:
                        update_coreTrans(gen_trans([meaTypeDict['id'][0], m_supTypeDict['id'][-1]], [meaTypeDict['id'][1]], m_supTypeDict['id'][-1]))
                elif supis and con_meais:
                    m_supTypeDict = coreTypeDict['types'][supis[0]]
                    if meaTypeDict['tag'] == ['coreC']:
                        update_coreTrans(gen_trans([meaTypeDict['id'][0], m_supTypeDict['id'][-1]], [str(core_id)],
                                                   m_supTypeDict['id'][-1] if 'region' not in meaTypeDict['text'][0] else None))
                        update_coreType(new_type(meaTypeDict['id'][0]))
                        update_id()
                else:
                    m_extent_id = coreTypeDict['types'][coreTypeDict['funcRole'].index('extent')][0]
                    if not supis and not con_meais and (meaTypeDict['tag'] == ['coreC'] or meaTypeDict['tag'] == ['networkC']):
                        update_coreTrans(gen_trans(meaTypeDict['id'], [str(core_id)], None))
                        update_coreType(new_type(meaTypeDict['id'][0]))
                        update_id()
                    if meaTypeDict['tag'] == ['coreC', 'location'] or meaTypeDict['tag'] == ['coreC', 'allocation']:
                        update_coreTrans(write_trans_within(meaTypeDict))
                    elif meaTypeDict['tag'] == ['coreC', 'conAm']:
                        update_coreTrans(gen_trans([meaTypeDict['id'][0]], [meaTypeDict['id'][1]], m_extent_id))
                    elif meaTypeDict['tag'] == ['coreC', 'coreC']:
                        update_coreTrans(gen_trans([meaTypeDict['id'][0]], [meaTypeDict['id'][1]], None))
                    elif meaTypeDict['tag'] == ['coreC', 'extremaR', 'location']:
                        if meaTypeDict['text'][1] in extre_Dict['keyword']:
                            extK_index = extre_Dict['keyword'].index(meaTypeDict['text'][1])
                            if extre_Dict['cctag'][extK_index] == 'covamount':
                                # meaTypeDict['id'][0] -> covamount, e.g., park -> area
                                update_coreTrans(gen_trans([meaTypeDict['id'][0]], [str(core_id)],None))
                                update_coreType(addext_type(meaTypeDict['text'][1]))  # update the type describing extremaR
                            else:
                                update_coreType(addext_type(meaTypeDict['text'][1]))
                            # extremaR + meaTypeDict['id']['id'][0] -> new meaTypeDict['id'][0]
                            input0 = [meaTypeDict['id'][0], str(core_id)]
                            update_id()  # update core_id for output
                            update_coreTrans(gen_trans(input0, [str(core_id)], None))
                            update_coreType(new_type(meaTypeDict['id'][0]))
                            # update id of new meaTypeDict['id'][0]
                            meaTypeDict['id'][0] = str(core_id)
                            # location trans
                            update_coreTrans(write_trans_within(meaTypeDict))
                            update_id()
                    elif meaTypeDict['tag'][-1] == 'mergeO':
                        update_coreTrans(gen_trans(meaTypeDict['id'][:3], [meaTypeDict['id'][-1]], None))
                    elif meaTypeDict['tag'][-1] == 'networkQ' or meaTypeDict['tag'][-1] == 'networkC':
                        update_coreTrans(write_trans_within(meaTypeDict))
                    elif meaTypeDict['tag'][-1] == 'objectQ' and 'origin' in meaTypeDict['tag']:
                        update_coreTrans(write_trans_within(meaTypeDict))
                    elif meaTypeDict['tag'] == ['destination', 'origin', 'objectQ', 'coreC']:
                        objQ_TypeDict = {key: value[0: i + 1] for key, value in meaTypeDict.items() for i in range(len(value)) if
                     meaTypeDict['tag'][i] == 'objectQ'}
                        objQ_trans = write_trans_within(objQ_TypeDict)
                        update_coreTrans(objQ_trans)
                        update_coreTrans(gen_trans(objQ_trans[-1]['after'], [meaTypeDict['id'][-1]], None))

        # print('final trans\n', coreConTrans)


    except:
        print("Cannot generate transformations.\n{}".format(coreConTrans))

    return coreConTrans
