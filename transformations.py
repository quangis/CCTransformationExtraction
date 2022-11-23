import numpy

# generate type for a subset of a concept. only change id. keywords and type remain same.
def new_type(curid):
    global core_id
    global coreConTrans

    newtype_index = [i for i, j in enumerate(coreConTrans['types']) if j['id'] == curid][
        0]  # find index for the subset transcross_condi['after']
    newtype = coreConTrans['types'][newtype_index].copy()  # copy type for the subset
    newtype['id'] = str(core_id)  # update id for the subset

    return newtype


# [X] Generate core concept transformations within condition, measure...
# Input TypeDict = {'tag': ['coreC', 'distField', 'boolField'], 'text': ['object 1', 'from', ''], 'id': ['1', '2', '3']}
# Output [{'before': ['1'], 'after': ['2']}, {'before': ['2'], 'after': ['3']}]
def write_trans_within(TypeDict):
    global core_id
    global coreConTrans
    global measureType
    transwithin = []
    coreC_sign = 0

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
                    core_id += 1
                elif cur_tag == 'coreC':
                    trans = {}
                    trans['before'] = [TypeDict['id'][TypeDict['tag'].index(tt) - 1]]
                    trans['after'] = [TypeDict['id'][TypeDict['tag'].index(tt)]]
                    transwithin.append(trans)
        elif tt == 'location' and 'allocation' not in TypeDict['tag']:
            trans = {}
            trans['before'] = [TypeDict['id'][TypeDict['tag'].index(tt) - 1]]
            trans['after'] = [TypeDict['id'][TypeDict['tag'].index(tt)]]
            transwithin.append(trans)
        elif tt == 'serviceobj':
            s_in = TypeDict['tag'].index(tt)
            trans = {}
            #-------new----------
            if s_in - 2 >= 0 and TypeDict['tag'][s_in - 2] == 'destination':
                if s_in - 3 >= 0 and TypeDict['tag'][
                    s_in - 3] == 'origin':  # ['origin', 'destination', 'networkC', 'serviceObj'], remove 'roadData'
                    if len(TypeDict['id'][
                               s_in - 3]) == 2:  # [['grid', 'centroid'], 'destination', 'networkC', 'serviceObj'], remove 'roadData'
                        trans['before'] = [TypeDict['id'][s_in - 3][0]]
                        trans['after'] = [TypeDict['id'][s_in - 3][1]]
                        transwithin.append(trans)
                    # origin: TypeDict['id'][s_in - 3], destination: TypeDict['id'][s_in - 2], remove roadData
                    # networkC is not used here.
                    trans = {}
                    trans['before'] = [TypeDict['id'][s_in - 3][-1], TypeDict['id'][s_in - 2][-1]]
                    trans['after'] = [TypeDict['id'][s_in-1]]
                    transwithin.append(trans)
                    trans_service = {}  # driving time -> 1 min driving time
                    trans_service['before'] = [TypeDict['id'][s_in - 1]]
                    trans_service['after'] = [str(core_id)]
                    transwithin.append(trans_service)
                    coreConTrans.setdefault('types', []).append(new_type(trans_service['before'][0]))
                    core_id += 1
            elif s_in - 2 >= 0 and TypeDict['tag'][
                s_in - 2] == 'origin':  # ['origin', 'networkC', 'serviceObj'], remove 'roadData'
                if len(TypeDict['id'][
                           s_in - 2]) == 2:  # [['grid', 'centroid'], 'networkC', 'serviceObj'], remove 'roadData'
                    trans['before'] = [TypeDict['id'][s_in - 2][0]]
                    trans['after'] = [TypeDict['id'][s_in - 2][1]]
                    transwithin.append(trans)
                trans = {} # origin, measure_obj -> driving time
                trans['before'] = [TypeDict['id'][s_in - 2][-1], measureType['id'][0]]
                trans['after'] = [TypeDict['id'][s_in-1]]
                transwithin.append(trans)
                trans_ser = {} # driving time -> 1 min driving time
                trans_ser['before'] = [TypeDict['id'][s_in - 1]]
                trans_ser['after'] = [str(core_id)]
                transwithin.append(trans_ser)
                coreConTrans.setdefault('types', []).append(new_type(trans_ser['before'][0]))
                core_id += 1
            # -------new----------
        elif (tt == 'networkC' or tt == 'networkQ') and (
                'destination' in TypeDict['tag'] or 'origin' in TypeDict['tag']) and 'serviceobj' not in TypeDict[
            'tag']:
            n_in = TypeDict['tag'].index(tt)
            trans = {}
            if 'destination' in TypeDict['tag']:
                desti_loc = TypeDict['tag'].index('destination')
                if 'origin' in TypeDict['tag']:  # ['origin', 'destination', 'networkC'] //'roadData',
                    orig_loc = TypeDict['tag'].index('origin')
                    if len(TypeDict['id'][orig_loc]) == 2:  # [['grid', 'centroid'], 'destination', 'networkC'] //'roadData'
                        trans['before'] = [TypeDict['id'][orig_loc][0]]
                        trans['after'] = [TypeDict['id'][orig_loc][1]]
                        transwithin.append(trans)
                    # origin: TypeDict['id'][n_in - 2], destination: TypeDict['id'][n_in - 1], // remove roadData:TypeDict['id'][n_in - 1]
                    trans = {}
                    trans['before'] = [TypeDict['id'][orig_loc][-1], TypeDict['id'][desti_loc][-1]]
                    trans['after'] = [TypeDict['id'][n_in]]
                    transwithin.append(trans)
                else:  # ['destination', 'networkC'] //'roadData'
                    trans['before'] = [TypeDict['id'][desti_loc][-1]]
                    trans['after'] = [TypeDict['id'][n_in]]
                    transwithin.append(trans)
            elif n_in - 1 >= 0 and TypeDict['tag'][n_in - 1] == 'origin':  # ['origin', 'networkC'] //'roadData',
                if len(TypeDict['id'][n_in - 1]) == 2:  # [['grid', 'centroid'], 'networkC'] //'roadData',
                    trans['before'] = [TypeDict['id'][n_in - 1][0]]
                    trans['after'] = [TypeDict['id'][n_in - 1][1]]
                    transwithin.append(trans)
                trans = {}
                trans['before'] = [TypeDict['id'][n_in - 1][-1]]
                trans['after'] = [TypeDict['id'][n_in]]
                transwithin.append(trans)
            # TODO: duplicate? [origin([object1]), netoworkC]
            # elif n_in - 1 >= 0 and TypeDict['tag'][n_in - 1] == 'origin':
            #     trans = {}
            #     trans['before'] = [TypeDict['id'][n_in - 1][0]]
            #     trans['after'] = [TypeDict['id'][n_in]]
            #     transwithin.append(trans)
        elif tt == 'extreDist' and TypeDict['tag'][TypeDict['tag'].index('extreDist') - 1] == 'networkQ':
            trans = {}
            trans['before'] = [TypeDict['id'][TypeDict['tag'].index('extreDist') - 1]]
            trans['after'] = [str(core_id)]
            transwithin.append(trans)
            # add object quality in types
            net_index = [i for i, j in enumerate(coreConTrans['types']) if j['id'] == trans['before'][0]][0]
            coreConTrans.setdefault('types', []).append(
                {'type': 'objectquality', 'id': str(core_id),
                 'keyword': TypeDict['text'][TypeDict['tag'].index('extreDist')] + ' ' +
                            coreConTrans['types'][net_index]['keyword'], 'measureLevel': 'ratio'})
            core_id += 1
        elif tt == 'compareR' and len(TypeDict['tag']) == 2:
            trans = {}
            trans['before'] = [TypeDict['id'][TypeDict['tag'].index(tt)]]
            trans['after'] = [str(core_id)]
            transwithin.append(trans)
            coreConTrans.setdefault('types', []).append(new_type(trans['before'][0]))
            core_id += 1
        elif tt == 'coreC' and 'serviceobj' not in TypeDict['tag'] and 'networkC' not in TypeDict['tag']:
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
        coreTypeDict = parsedResult[1]
        global coreConTrans
        coreConTrans = parsedResult[2]
        global core_id
        core_id = parsedResult[3]
        global measureType
        coretrans = []
        subis = []
        conis = []
        supis = []
        meais = []
        mea1is = []
        con_supis = []
        mc = []  # if condition number = 2, need to combine m*condition1 and m*condition2

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
            conar = numpy.array(conis)
            supar = numpy.array(supis)
            con_supis = list(conar[conar < supar])
            con_meais = [x for x in conis if x not in con_supis]
        else:
            con_meais = conis

        if subis:
            if len(coreTypeDict['types'][subis[0]]['tag']) > 1:
                #---------new--------
                if ('compareR' in coreTypeDict['types'][subis[0]]['tag'] and
                    coreTypeDict['types'][subis[0]]['tag'].index('compareR') + 1 < 2 and
                    'pro' not in coreTypeDict['types'][subis[0]]['text'][
                        coreTypeDict['types'][subis[0]]['tag'].index('compareR') + 1]) or "boolfield" in \
                        coreTypeDict['types'][subis[0]]['tag']:
                    sub_trans = write_trans_within(coreTypeDict['types'][subis[0]])
                    coretrans.extend(sub_trans)
                #---------new--------
            if coreTypeDict['funcRole'][subis[0] + 1] == 'condition':
                transcross = {}
                transcross['before'] = [coreTypeDict['types'][subis[0] + 1]['id'][0],
                                        coreTypeDict['types'][subis[0]]['id'][-1]]
                transcross['after'] = [str(core_id)]
                coreConTrans.setdefault('types', []).append(new_type(coreTypeDict['types'][subis[0] + 1]['id'][0]))
                if 'amount' in coreTypeDict['types'][subis[0] + 1]['text'][0] and 'distfield' in coreTypeDict['types'][subis[0]]['tag']:
                    distf_index = coreTypeDict['types'][subis[0]]['tag'].index('distfield')
                    transcross['key'] = coreTypeDict['types'][subis[0]]['id'][distf_index]
                coreTypeDict['types'][subis[0] + 1]['id'][0] = transcross['after'][0]
                core_id += 1
                coretrans.append(transcross)

        if con_supis:
            if len(coreTypeDict['types'][con_supis[0]]['tag']) > 1:
                con_sup_trans = write_trans_within(coreTypeDict['types'][con_supis[0]])
                coretrans.extend(con_sup_trans[0])
            transcross = {}
            transcross['before'] = [coreTypeDict['types'][supis[0]]['id'][0],
                                    coreTypeDict['types'][con_supis[0]]['id'][-1]]
            transcross['after'] = [str(core_id)]
            coretrans.append(transcross)
            coreConTrans.setdefault('types', []).append(new_type(coreTypeDict['types'][supis[0]]['id'][0]))
            coreTypeDict['types'][supis[0]]['id'][0] = transcross['after'][0]
            core_id += 1

        # if there is transformations within support, no such question in GeoAnQu
        if supis and len(coreTypeDict['types'][supis[0]]['tag']) > 1:
            sup_trans = write_trans_within(coreTypeDict['types'][supis[0]])
            coretrans.extend(sup_trans)

        if con_meais:
            for ci in con_meais:
                if any('proportion' in e for e in coreTypeDict['types'][ci]['text']):
                    amount_id = coreTypeDict['types'][ci]['id'][0:-1]
                    if amount_id:
                        transcross = {}
                        transcross['before'] = amount_id
                        transcross['after'] = [coreTypeDict['types'][ci]['id'][-1]]
                        # Which park has the highest proportion of bald eagles to the bird totals in Texas, extremaR is not considered here.
                        if coreTypeDict['types'][meais[0]]['tag'] == ['coreC']:
                            transcross['key'] = coreTypeDict['types'][meais[0]]['id'][0]
                        coretrans.append(transcross)
                    elif not amount_id and len(coreTypeDict['types'][ci]['tag']) > 1:
                        con_mea_trans = write_trans_within(coreTypeDict['types'][ci])
                        coretrans.extend(con_mea_trans)
                        if 'compareR' in coreTypeDict['types'][ci]['tag']:
                            compR_index = coreTypeDict['types'][ci]['tag'].index('compareR')
                            coreTypeDict['types'][ci]['id'][compR_index] = con_mea_trans[0]['after'][0]
                elif len(coreTypeDict['types'][ci]['tag']) > 1 and not any(
                        'aggre' in e for e in coreTypeDict['types'][ci]['tag']) and not any(
                    'proportion' in e for e in coreTypeDict['types'][ci]['text']):
                    con_mea_trans = write_trans_within(coreTypeDict['types'][ci])
                    coretrans.extend(con_mea_trans)
                    if 'serviceobj' in coreTypeDict['types'][ci]['tag']:
                        coreTypeDict['types'][ci]['id'][-1] = con_mea_trans[-1]['after'][0]
                    if 'compareR' in coreTypeDict['types'][ci]['tag']:
                        compR_index = coreTypeDict['types'][ci]['tag'].index('compareR')
                        coreTypeDict['types'][ci]['id'][compR_index] = con_mea_trans[0]['after'][0]
                elif any('aggre' in e for e in coreTypeDict['types'][ci]['tag']):
                    transcross = {}
                    transcross['before'] = [coreTypeDict['types'][ci]['id'][-2]]
                    transcross['after'] = [coreTypeDict['types'][ci]['id'][-1]]
                    coretrans.append(transcross)

        if meais:
            if (any('proportion' in e for e in coreTypeDict['types'][meais[0]]['text']) or \
                    any('eveconobjconpro' in e for e in coreTypeDict['types'][meais[0]]['text'])) and ('covamount' not in coreTypeDict['types'][meais[0]]['text'][-1]):
                amount_id = coreTypeDict['types'][meais[0]]['id'][0:-1]
                if amount_id:
                    if supis and not con_meais:
                        for a in amount_id:
                            a_index = coreTypeDict['types'][meais[0]]['id'].index(a)
                            if 'amount' in coreTypeDict['types'][meais[0]]['text'][a_index]:
                                transcross = {}  # objconA * support -> content Amount
                                transcross['before'] = [a, coreTypeDict['types'][supis[0]]['id'][-1]]
                                transcross['after'] = [str(core_id)]
                                transcross['key'] = coreTypeDict['types'][supis[0]]['id'][-1]
                                coretrans.append(transcross)
                                coreConTrans.setdefault('types', []).append(new_type(a))
                                coreTypeDict['types'][meais[0]]['id'][a_index] = transcross['after'][0]
                                core_id += 1
                            elif 'object' in coreTypeDict['types'][meais[0]]['text'][a_index] or 'event' in \
                                    coreTypeDict['types'][meais[0]]['text'][a_index]:
                                transcross = {}  # object * support -> object amount
                                transcross['before'] = [a, coreTypeDict['types'][supis[0]]['id'][-1]]
                                transcross['after'] = [str(core_id)]
                                transcross['key'] = coreTypeDict['types'][supis[0]]['id'][-1]
                                coretrans.append(transcross)
                                coreConTrans.setdefault('types', []).append(
                                    {'type': 'amount', 'id': str(core_id), 'keyword': '', 'measureLevel': 'era'})
                                coreTypeDict['types'][meais[0]]['id'][coreTypeDict['types'][meais[0]]['id'].index(a)] = \
                                transcross['after'][0]  # why change id?
                                core_id += 1
                            elif 'field' in coreTypeDict['types'][meais[0]]['text'][
                                a_index]:  # percentage of water areas for each PC4
                                transcross = {}  # field * support -> field coverage amount
                                transcross['before'] = [coreTypeDict['types'][meais[0]]['id'][0],
                                                        coreTypeDict['types'][supis[0]]['id'][-1]]
                                transcross['after'] = [str(core_id)]
                                transcross['key'] = coreTypeDict['types'][supis[0]]['id'][-1]
                                coretrans.append(transcross)
                                coreConTrans.setdefault('types', []).append(
                                    {'type': 'covamount', 'id': str(core_id), 'keyword': '', 'measureLevel': 'era'})
                                core_id += 1
                        if not mea1is:
                            if len(coreTypeDict['types'][meais[0]]['id']) > 2:  # [amount+amount, proportion]
                                transcross = {}  # objconA * objconA  = proportion
                                transcross['before'] = coreTypeDict['types'][meais[0]]['id'][0:-1]
                                transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-1]]
                                transcross['key'] = coreTypeDict['types'][supis[0]]['id'][-1]
                                coretrans.append(transcross)
                            elif len(coreTypeDict['types'][meais[0]]['id']) == 2:  # [field/object/event, proportion]
                                transcross = {}  # support -> support coverage amount
                                transcross['before'] = [coreTypeDict['types'][supis[0]]['id'][-1]]
                                transcross['after'] = [str(core_id)]
                                coretrans.append(transcross)
                                coreConTrans.setdefault('types', []).append(
                                    {'type': 'covamount', 'id': str(core_id), 'keyword': '', 'measureLevel': 'era'})
                                # field coverage amount * support coverage amount = proportion
                                transcross = {}
                                transcross['before'] = [str(core_id - 1), str(core_id)]
                                transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-1]]
                                transcross['key'] = coreTypeDict['types'][supis[0]]['id'][-1]
                                coretrans.append(transcross)
                                core_id += 1
                        elif mea1is:
                            a1 = coreTypeDict['types'][mea1is[0]]['id'][-1]
                            transcross = {}
                            transcross['before'] = [a1, coreTypeDict['types'][supis[0]]['id'][-1]]
                            transcross['after'] = [str(core_id)]
                            transcross['key'] = coreTypeDict['types'][supis[0]]['id'][-1]
                            coretrans.append(transcross)
                            coreConTrans.setdefault('types', []).append(new_type(a1))
                            coreTypeDict['types'][mea1is[0]]['id'][coreTypeDict['types'][mea1is[0]]['id'].index(a1)] = \
                                transcross['after'][0]
                            core_id += 1
                            transcross = {}  # objconA * objconA  = proportion
                            transcross['before'] = [coreTypeDict['types'][meais[0]]['id'][0],
                                                    coreTypeDict['types'][mea1is[0]]['id'][-1]]
                            transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-1]]
                            transcross['key'] = coreTypeDict['types'][supis[0]]['id'][-1]
                            coretrans.append(transcross)
                    elif con_meais and not supis:
                        if 'id' not in coreTypeDict['types'][con_meais[0]]:  # compareR or extremaR
                            transcross = {}
                            transcross['before'] = [coreTypeDict['types'][meais[0]]['id'][0]]
                            transcross['after'] = [str(core_id)]
                            coretrans.append(transcross)
                            coreConTrans.setdefault('types', []).append(
                                new_type(coreTypeDict['types'][meais[0]]['id'][0]))
                            core_id += 1
                        else:
                            transcross = {}  # objconA * condi = objconA_u  or field * condi = field_u
                            transcross['before'] = [coreTypeDict['types'][con_meais[0]]['id'][-1],
                                                    coreTypeDict['types'][meais[0]]['id'][0]]
                            transcross['after'] = [str(core_id)]
                            if 'amount' in coreTypeDict['types'][meais[0]]['text'][0] and 'distfield' in coreTypeDict['types'][con_meais[0]]['tag']:
                                distf_index = coreTypeDict['types'][con_meais[0]]['tag'].index('distfield')
                                transcross['key'] = coreTypeDict['types'][con_meais[0]]['id'][distf_index]
                            coretrans.append(transcross)
                            coreConTrans.setdefault('types', []).append(
                                new_type(coreTypeDict['types'][meais[0]]['id'][0]))
                            core_id += 1
                        if mea1is:
                            transcross = {}
                            transcross['before'] = [str(core_id - 1),
                                                    coreTypeDict['types'][mea1is[0]]['id'][0]]
                            transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-1]]
                            transcross['key'] = coreConTrans['extent'][0]
                            coretrans.append(transcross)
                            core_id += 1
                        else:
                            if any('conamount' in e for e in coreTypeDict['types'][meais[0]]['text']):
                                transcross = {}  # objconA_u * objconA = proportion for [condition, objconA, proportion]
                                transcross['before'] = [str(core_id - 1),
                                                        coreTypeDict['types'][meais[0]]['id'][0]]
                                transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-1]]
                                transcross['key'] = coreConTrans['extent'][0]
                                coretrans.append(transcross)
                                core_id += 1
                            elif any('field' in e for e in coreTypeDict['types'][meais[0]]['text']):
                                transcross = {}  # field_u -> field coverage amount
                                transcross['before'] = [str(core_id - 1)]  # field_u
                                transcross['after'] = [str(core_id)]  # covamount
                                coretrans.append(transcross)
                                coreConTrans.setdefault('types', []).append(
                                    {'type': 'covamount', 'id': str(core_id), 'keyword': '', 'measureLevel': 'era'})
                                core_id += 1
                                if 'id' not in coreTypeDict['types'][con_meais[0]]:  # noise larger than 70 db
                                    #  extent -> extent coverage amount
                                    transcross = {}
                                    transcross['before'] = coreConTrans['extent']
                                    transcross['after'] = [str(core_id)]
                                    coretrans.append(transcross)
                                    coreConTrans.setdefault('types', []).append(
                                        {'type': 'covamount', 'id': str(core_id), 'keyword': '',
                                         'measureLevel': 'era'})
                                    # field coverage amount, extent coverage amount -> proportion
                                    transcross = {}
                                    transcross['before'] = [str(core_id - 1), str(
                                        core_id)]  # core_id-1 = field covamount, core_id = extent covamount
                                    transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-1]]
                                    transcross['key'] = coreConTrans['extent'][0]
                                    coretrans.append(transcross)
                                    core_id += 1
                                else:
                                    # condition -> conidtion coverage amount
                                    transcross = {}
                                    transcross['before'] = [
                                        coreTypeDict['types'][con_meais[0]]['id'][-1]]  # boolfiled or distfield
                                    transcross['after'] = [str(core_id)]
                                    coretrans.append(transcross)
                                    coreConTrans.setdefault('types', []).append(
                                        {'type': 'covamount', 'id': str(core_id), 'keyword': '',
                                         'measureLevel': 'era'})
                                    # field coverage amount * condition coverage amount = proportion
                                    transcross = {}
                                    transcross['before'] = [str(core_id - 1), str(core_id)]
                                    transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-1]]
                                    transcross['key'] = coreConTrans['extent'][0] #---------new-----
                                    coretrans.append(transcross)
                                    core_id += 1
                            else:
                                transcross = {}  # object_u -> object_u amount
                                transcross['before'] = [str(core_id - 1)]
                                transcross['after'] = [str(core_id)]
                                transcross['key'] = coreConTrans['extent'][
                                    0]  # object to amount need a key, to covamount donot a key?
                                coretrans.append(transcross)
                                coreConTrans.setdefault('types', []).append(
                                    {'type': 'amount', 'id': str(core_id), 'keyword': '', 'measureLevel': 'era'})
                                core_id += 1
                                # object -> object amount
                                transcross = {}  # object -> object amount
                                transcross['before'] = [coreTypeDict['types'][meais[0]]['id'][0]]
                                transcross['after'] = [str(core_id)]
                                transcross['key'] = coreConTrans['extent'][0]
                                coretrans.append(transcross)
                                coreConTrans.setdefault('types', []).append(
                                    {'type': 'amount', 'id': str(core_id), 'keyword': '', 'measureLevel': 'era'})
                                # object amount * condition coverage amount = proportion
                                transcross = {}
                                transcross['before'] = [str(core_id - 1), str(core_id)]
                                transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-1]]
                                transcross['key'] = coreConTrans['extent'][0]
                                coretrans.append(transcross)
                                core_id += 1
                    elif not supis and not con_meais:
                        # extent -> extent covamount
                        trans_ext = {}
                        trans_ext['before'] = [coreConTrans['extent'][0]]
                        trans_ext['after'] = [str(core_id)]
                        coretrans.append(trans_ext)
                        coreConTrans.setdefault('types', []).append(
                            {'type': 'covamount', 'id': str(core_id), 'keyword': '', 'measureLevel': 'era'})
                        core_id += 1
                        if any('field' in e for e in coreTypeDict['types'][meais[0]][
                            'text']):  # What is the percentage of noise polluted areas in placename0
                            # field -> field covamount
                            transcross = {}
                            transcross['before'] = [coreTypeDict['types'][meais[0]]['id'][0]]
                            transcross['after'] = [str(core_id)]
                            coretrans.append(transcross)
                            coreConTrans.setdefault('types', []).append(
                                {'type': 'covamount', 'id': str(core_id), 'keyword': '', 'measureLevel': 'era'})
                        else:
                            # What is the percentage of vacant houses to the house totals in Tarrant County, Texas
                            # 'What is the density of parks in Amsterdam'
                            obj_loc = [coreTypeDict['types'][meais[0]]['text'].index(i) for i in
                                       coreTypeDict['types'][meais[0]]['text'] if 'object' in i]
                            if obj_loc:
                                # obj -> amount
                                trans_obj = {}
                                trans_obj['before'] = [coreTypeDict['types'][meais[0]]['id'][obj_loc[0]]]
                                trans_obj['after'] = [str(core_id)]
                                trans_obj['key'] = coreConTrans['extent'][0]
                                coretrans.append(trans_obj)
                                coreConTrans.setdefault('types', []).append(
                                    {'type': 'amount', 'id': str(core_id), 'keyword': '',
                                     'measureLevel': 'era'})
                                coreTypeDict['types'][meais[0]]['id'][obj_loc[0]] = trans_obj['after'][0]
                        # proportion
                        if len(amount_id) == 2:
                            transcross = {}
                            transcross['before'] = coreTypeDict['types'][meais[0]]['id'][0:-1]
                            transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-1]]
                            transcross['key'] = coreConTrans['extent'][0]
                            coretrans.append(transcross)
                        elif len(amount_id) == 1:
                            transcross = {}
                            transcross['before'] = [str(core_id), trans_ext['after'][0]]
                            transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-1]]
                            transcross['key'] = coreConTrans['extent'][0]
                            coretrans.append(transcross)
                            core_id += 1
                    elif supis and con_meais:
                        # object* condi = object_u or field * condi = field_u  or objconA * condi = objconA_u
                        # What is the proportion of noise larger than 70 db for each neighbourhood in Amsterdam
                        if 'compareR' in coreTypeDict['types'][con_meais[0]]['tag'] and len(
                                coreTypeDict['types'][con_meais[0]]['tag']) == 1:
                            compR_trans = {}
                            compR_trans['before'] = [coreTypeDict['types'][meais[0]]['id'][0]]
                            compR_trans['after'] = [str(core_id)]
                            coretrans.append(compR_trans)
                        else:  # percentage of households within 2000 meters from the supermarkets for each district
                            transcross_condi = {}
                            transcross_condi['before'] = [coreTypeDict['types'][con_meais[0]]['id'][-1],
                                                          coreTypeDict['types'][meais[0]]['id'][0]]
                            transcross_condi['after'] = [str(core_id)]
                            coretrans.append(transcross_condi)
                        newtype = new_type(coreTypeDict['types'][meais[0]]['id'][0])
                        coreConTrans.setdefault('types', []).append(newtype)
                        core_id += 1
                        # object_u * support -> object_u amount or field_u * support -> field_u covamount, key required
                        transcross = {}
                        transcross['before'] = [newtype['id'], coreTypeDict['types'][supis[0]]['id'][-1]]
                        transcross['after'] = [str(core_id)]
                        transcross['key'] = coreTypeDict['types'][supis[0]]['id'][-1]
                        coretrans.append(transcross)
                        if newtype['type'] == 'object':
                            coreConTrans.setdefault('types', []).append(
                                {'type': 'amount', 'id': str(core_id), 'keyword': '', 'measureLevel': 'era'})
                        elif newtype['type'] == 'field':
                            coreConTrans.setdefault('types', []).append(
                                {'type': 'covamount', 'id': str(core_id), 'keyword': '', 'measureLevel': 'era'})
                        else:
                            coreConTrans.setdefault('types',[]).append(new_type(coreTypeDict['types'][meais[0]]['id'][0]))
                        core_id += 1
                        # object * support = object_u_u amount  key required
                        if mea1is:
                            transcross = {}
                            transcross['before'] = [coreTypeDict['types'][mea1is[0]]['id'][0],coreTypeDict['types'][supis[0]]['id'][-1]]
                            transcross['after'] = [str(core_id)]
                            transcross['key'] = coreTypeDict['types'][supis[0]]['id'][-1]
                            coretrans.append(transcross)
                            coreConTrans.setdefault('types', []).append(new_type(coreTypeDict['types'][mea1is[0]]['id'][0]))
                        else:
                            if newtype['type'] == 'object' or "amount" in newtype['type']:
                                transcross_sup = {}
                                transcross_sup['before'] = [coreTypeDict['types'][meais[0]]['id'][0],
                                                            coreTypeDict['types'][supis[0]]['id'][-1]]
                                transcross_sup['after'] = [str(core_id)]
                                transcross_sup['key'] = coreTypeDict['types'][supis[0]]['id'][-1]
                                coreConTrans.setdefault('types', []).append(
                                    {'type': 'amount', 'id': str(core_id), 'keyword': '', 'measureLevel': 'era'})
                            elif newtype['type'] == 'field':  # support -> covamount if field,
                                transcross_sup = {}
                                transcross_sup['before'] = [coreTypeDict['types'][supis[0]]['id'][-1]]
                                transcross_sup['after'] = [str(core_id)]
                                coreConTrans.setdefault('types', []).append(
                                    {'type': 'covamount', 'id': str(core_id), 'keyword': '', 'measureLevel': 'era'})
                            coretrans.append(transcross_sup)
                        # object_u amount * object_u_u amount -> proportion or field_u covamount * field_u_u covamount -> proportion
                        transcross_pro = {}
                        transcross_pro['before'] = [str(core_id - 1), str(core_id)]
                        transcross_pro['after'] = [coreTypeDict['types'][meais[0]]['id'][-1]]
                        transcross_pro['key'] = coreTypeDict['types'][supis[0]]['id'][-1]
                        coretrans.append(transcross_pro)
                        core_id += 1
                else:  # only one proportion in measure. e.g.,What is the crime density within the buffer area of the shortest path from home to workplace in Amsterdam
                    if con_meais and not supis:
                        transcross = {}
                        transcross['before'] = [coreTypeDict['types'][con_meais[0]]['id'][-1],
                                                coreTypeDict['types'][meais[0]]['id'][0]]
                        transcross['after'] = [str(core_id)]
                        if 'distfield' in coreTypeDict['types'][0]['tag']:
                            dist_index = [i for i, j in enumerate(coreConTrans['types']) if j['type'] == 'distfield'][0]
                            if coreTypeDict['types'][0]['tag'][dist_index - 1] == 'networkC':
                                transcross['key'] = str(core_id - 1)
                            elif coreTypeDict['types'][0]['tag'][dist_index - 1] == 'coreC':
                                transcross['key'] = coreTypeDict['types'][0]['id'][dist_index - 1]
                        coretrans.append(transcross)
                        # add new proportion type in coreConTrans[types]
                        coreConTrans.setdefault('types', []).append(new_type(coreTypeDict['types'][meais[0]]['id'][0]))
                        core_id += 1
                    elif supis and not con_meais:
                        transcross = {}
                        transcross['before'] = [coreTypeDict['types'][supis[0]]['id'][-1],
                                                coreTypeDict['types'][meais[0]]['id'][0]]
                        transcross['after'] = [str(core_id)]
                        transcross['key'] = coreTypeDict['types'][supis[0]]['id'][-1]
                        coretrans.append(transcross)
                        coreConTrans.setdefault('types', []).append(new_type(coreTypeDict['types'][meais[0]]['id'][0]))
                        core_id += 1
            elif any('objconobjconpro' in e for e in coreTypeDict['types'][meais[0]]['text']) and any(
                    'object' in e for e in coreTypeDict['types'][meais[0]]['text']):
                if supis and not con_meais:
                    # object/objconA * support - > objconA
                    trans_sup = {}
                    trans_sup['before'] = [coreTypeDict['types'][meais[0]]['id'][0],
                                           coreTypeDict['types'][supis[0]]['id'][0]]
                    trans_sup['after'] = [str(core_id)]
                    trans_sup['key'] = coreTypeDict['types'][supis[0]]['id'][0]
                    coretrans.append(trans_sup)
                    coreConTrans.setdefault('types', []).append(
                        {'type': 'objconamount', 'id': str(core_id), 'keyword': '', 'measureLevel': 'era'})
                    core_id += 1
                    # objconA * a unknown objconA -> proportion
                    transcross = {}
                    transcross['before'] = [trans_sup['after'][0], str(core_id)]
                    transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-1]]
                    transcross['key'] = coreTypeDict['types'][supis[0]]['id'][0]
                    coretrans.append(transcross)
                    coreConTrans.setdefault('types', []).append(
                        {'type': 'objconamount', 'id': str(core_id), 'keyword': '', 'measureLevel': 'era'})
                    core_id += 1
            elif any('conamount' in e for e in coreTypeDict['types'][meais[0]]['text']) and not any(
                    'aggre' in e for e in coreTypeDict['types'][meais[0]]['tag']) and not any(
                'proportion' in e for e in coreTypeDict['types'][meais[0]]['text']) and not any(
                'covamount' in e for e in coreTypeDict['types'][meais[0]]['text']):
                if supis and not con_meais:
                    if len(coreTypeDict['types'][meais[0]]['tag']) == 2:  # conamount of coreC
                        transcross = {}
                        transcross['before'] = [coreTypeDict['types'][meais[0]]['id'][0],
                                                coreTypeDict['types'][supis[0]]['id'][-1]]
                        transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-1]]
                        transcross['key'] = coreTypeDict['types'][supis[0]]['id'][-1]
                        coretrans.append(transcross)
                    else:  # What is the WOZ-waarde for each neighborhood in Amsterdam, What is the population for each city in Aichi prefecture in Japan
                        transcross = {}
                        transcross['before'] = [coreTypeDict['types'][meais[0]]['id'][0],
                                                coreTypeDict['types'][supis[0]]['id'][-1]]
                        transcross['after'] = [str(core_id)]
                        transcross['key'] = coreTypeDict['types'][supis[0]]['id'][-1]
                        coretrans.append(transcross)
                        coreConTrans.setdefault('types', []).append(new_type(coreTypeDict['types'][meais[0]]['id'][0]))
                elif con_meais and not supis:
                    if len(coreTypeDict['types'][meais[0]]['tag']) > 1:
                        # object * condition -> object_u
                        transcross = {}
                        transcross['before'] = [coreTypeDict['types'][meais[0]]['id'][0],
                                                coreTypeDict['types'][con_meais[0]]['id'][-1]]
                        transcross['after'] = [str(core_id)]
                        coretrans.append(transcross)
                        coreConTrans.setdefault('types', []).append(new_type(coreTypeDict['types'][meais[0]]['id'][0]))
                        transcross = {}
                        transcross['before'] = [str(core_id)]
                        transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-1]]
                        transcross['key'] = coreConTrans['extent'][0]
                        coretrans.append(transcross)
                        core_id += 1
                    else:
                        transcross = {}
                        transcross['before'] = [coreTypeDict['types'][meais[0]]['id'][0],
                                                coreTypeDict['types'][con_meais[0]]['id'][-1]]
                        transcross['after'] = [str(core_id)]
                        transcross['key'] = coreConTrans['extent'][0]
                        coretrans.append(transcross)
                        coreConTrans.setdefault('types', []).append(new_type(coreTypeDict['types'][meais[0]]['id'][0]))
                        core_id += 1
                elif con_meais and supis:
                    for ci in con_meais:
                        if len(coreTypeDict['types'][ci]['tag']) == 1 and (
                                coreTypeDict['types'][ci]['tag'][0] == 'extremaR' or coreTypeDict['types'][ci]['tag'][
                            0] == 'compareR'):
                            transcross = {}
                            transcross['before'] = [coreTypeDict['types'][meais[0]]['id'][0]]
                            transcross['after'] = [str(core_id)]
                            coretrans.append(transcross)
                            coreConTrans.setdefault('types', []).append(
                                new_type(coreTypeDict['types'][meais[0]]['id'][0]))
                            coreTypeDict['types'][meais[0]]['id'][0] = transcross['after'][0]
                            core_id += 1
                        else:
                            transcross = {}
                            transcross['before'] = [coreTypeDict['types'][meais[0]]['id'][0],
                                                    coreTypeDict['types'][ci]['id'][-1]]
                            transcross['after'] = [str(core_id)]
                            coretrans.append(transcross)
                            coreConTrans.setdefault('types', []).append(
                                new_type(coreTypeDict['types'][meais[0]]['id'][0]))
                            coreTypeDict['types'][meais[0]]['id'][0] = transcross['after'][0]
                            core_id += 1
                    if len(coreTypeDict['types'][meais[0]]['tag']) == 2:
                        transcross = {}
                        transcross['before'] = [coreTypeDict['types'][meais[0]]['id'][0],
                                                coreTypeDict['types'][supis[0]]['id'][-1]]
                        transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-1]]
                        transcross['key'] = coreTypeDict['types'][supis[0]]['id'][-1]
                        coretrans.append(transcross)
                elif not con_meais and not supis:
                    transcross = {}
                    transcross['before'] = [coreTypeDict['types'][meais[0]]['id'][0]]
                    transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-1]]
                    transcross['key'] = coreConTrans['extent'][0]
                    coretrans.append(transcross)
            elif any('covamount' in e for e in coreTypeDict['types'][meais[0]]['text']) and not any(
                    'aggre' in e for e in coreTypeDict['types'][meais[0]]['tag']):
                if not supis and not con_meais:
                    if 'loc' in coreTypeDict['types'][meais[0]]['text'][-1] and 'weight' in coreTypeDict:
                        if coreTypeDict[
                            'weight'] == 2:  # What is the mean center of customers weighted by the number of transactions in Oleander city
                            # transformation within weight
                            trans_weight = {}
                            trans_weight['before'] = [coreTypeDict['types'][meais[0]]['id'][0]]
                            trans_weight['after'] = [coreTypeDict['types'][meais[0]]['id'][1]]
                            if 'conamount' in coreTypeDict['types'][meais[0]]['text'][1]:
                                trans_weight['key'] = coreTypeDict['types'][meais[0]]['id'][2]
                            coretrans.append(trans_weight)
                            # weight output * measure input -> covamount loc
                            transcross = {}
                            transcross['before'] = coreTypeDict['types'][meais[0]]['id'][1:3]
                            transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-1]]
                            coretrans.append(transcross)
                        elif coreTypeDict[
                            'weight'] == 1:  # What is the mean center of the fire calls weighted by the priority in Fort Worth
                            # weight * measure input -> covamount loc
                            transcross = {}
                            transcross['before'] = coreTypeDict['types'][meais[0]]['id'][0:2]
                            transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-1]]
                            coretrans.append(transcross)
                    else:
                        cov_trans = write_trans_within(coreTypeDict['types'][meais[0]])
                        # if 'era' in coreTypeDict['types'][meais[0]]['text'][-1].split(' '):  # is key required? no
                        #     cov_trans[0]['key'] = coreConTrans['extent'][0]
                        coretrans.extend(cov_trans)
                elif supis and not con_meais:
                    if 'location' in coreTypeDict['types'][meais[0]]['tag']:
                        transcross = {}
                        transcross['before'] = [coreTypeDict['types'][meais[0]]['id'][0],
                                                coreTypeDict['types'][supis[0]]['id'][-1]]
                        transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-2]]
                        coretrans.append(transcross)
                        transcross = {}
                        transcross['before'] = [coreTypeDict['types'][meais[0]]['id'][-2]]
                        transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-1]]
                        coretrans.append(transcross)
                    else:
                        transcross = {}
                        transcross['before'] = [coreTypeDict['types'][meais[0]]['id'][0],
                                                coreTypeDict['types'][supis[0]]['id'][-1]]
                        transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-1]]
                        if 'era' in coreTypeDict['types'][meais[0]]['text'][-1].split(' '):  # is key required? no
                            transcross['key'] = coreTypeDict['types'][supis[0]]['id'][-1]
                        coretrans.append(transcross)
                elif con_meais and not supis:
                    if 'location' in coreTypeDict['types'][meais[0]]['tag']:
                        transcross = {}
                        transcross['before'] = [coreTypeDict['types'][meais[0]]['id'][0],
                                                coreTypeDict['types'][conis[0]]['id'][-1]]
                        transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-2]]
                        coretrans.append(transcross)
                        transcross = {}
                        transcross['before'] = [coreTypeDict['types'][meais[0]]['id'][-2]]
                        transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-1]]
                        coretrans.append(transcross)
                    else:
                        transcross = {}
                        transcross['before'] = [coreTypeDict['types'][meais[0]]['id'][0],
                                                coreTypeDict['types'][conis[0]]['id'][-1]]
                        transcross['after'] = [str(core_id)]
                        coretrans.append(transcross)
                        coreConTrans.setdefault('types', []).append(new_type(coreTypeDict['types'][meais[0]]['id'][0]))
                        transcross = {}
                        transcross['before'] = [str(core_id)]
                        transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-1]]
                        coretrans.append(transcross)
                        core_id += 1
                elif supis and con_meais:
                    transcross = {}
                    transcross['before'] = [coreTypeDict['types'][meais[0]]['id'][0],
                                            coreTypeDict['types'][supis[0]]['id'][-1]]
                    transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][1]]
                    coretrans.append(transcross)
                    if 'location' in coreTypeDict['types'][meais[0]]['tag']:
                        transcross = {}
                        transcross['before'] = [coreTypeDict['types'][meais[0]]['id'][1]]
                        transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-1]]
                        coretrans.append(transcross)
            elif any('aggre' in e for e in coreTypeDict['types'][meais[0]]['tag']):
                if len(coreTypeDict['types'][meais[0]]['tag']) - 1 > 1:
                    befagg_trans = write_trans_within(coreTypeDict['types'][meais[0]])
                    coretrans.extend(befagg_trans)
                    if 'extreDist' in coreTypeDict['types'][0]['tag']:
                        extre_index = coreTypeDict['types'][0]['tag'].index('extreDist')
                        coreTypeDict['types'][0]['id'].insert(extre_index, str(core_id - 1))
                if supis:
                    transcross = {}
                    transcross['before'] = [coreTypeDict['types'][meais[0]]['id'][-2],
                                            coreTypeDict['types'][supis[0]]['id'][-1]]
                    transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-1]]
                    transcross['key'] = coreTypeDict['types'][supis[0]]['id'][-1]
                    coretrans.append(transcross)
                # TODO: update later, if extreDist exsit
                elif con_meais:
                    transcross = {}
                    transcross['before'] = [coreTypeDict['types'][meais[0]]['id'][-2],
                                            coreTypeDict['types'][con_meais[0]]['id'][-1]]
                    transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-1]]
                    coretrans.append(transcross)
                else:
                    transcross = {}
                    transcross['before'] = [coreTypeDict['types'][meais[0]]['id'][-2]]
                    transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-1]]
                    transcross['key'] = coreTypeDict['types'][coreTypeDict['funcRole'].index('extent')][0]
                    coretrans.append(transcross)
            else:
                if supis and not con_meais:
                    if len(coreTypeDict['types'][meais[0]]['id']) == 1:
                        transcross = {}
                        transcross['before'] = [coreTypeDict['types'][meais[0]]['id'][0],
                                                coreTypeDict['types'][supis[0]]['id'][-1]]
                        transcross['after'] = [str(core_id)]
                        if 'quality' in coreTypeDict['types'][meais[0]]['text'][0]:
                            transcross['key'] = coreTypeDict['types'][supis[0]]['id'][-1]
                        coretrans.append(transcross)
                        coreConTrans.setdefault('types', []).append(new_type(coreTypeDict['types'][meais[0]]['id'][0]))
                        core_id += 1
                    # -------new--------
                    elif len(coreTypeDict['types'][meais[0]]['id'][0]) > 1:
                        mea_trans = write_trans_within(coreTypeDict['types'][meais[0]])
                        if 'quality' in coreTypeDict['types'][meais[0]]['text'][-1]:
                            mea_trans[-1]['key'] = coreTypeDict['types'][supis[0]]['id'][-1]
                        coretrans.extend(mea_trans)
                    # -------new--------
                    else:
                        transcross = {}
                        transcross['before'] = [coreTypeDict['types'][meais[0]]['id'][0],
                                                coreTypeDict['types'][supis[0]]['id'][-1]]
                        transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-1]]
                        if 'quality' in coreTypeDict['types'][meais[0]]['text'][-1]:
                            transcross['key'] = coreTypeDict['types'][supis[0]]['id'][-1]
                        coretrans.append(transcross)
                elif con_meais and not supis:
                    for ci in con_meais:
                        if len(coreTypeDict['types'][ci]['tag']) == 1 and (
                                coreTypeDict['types'][ci]['tag'][0] == 'extremaR' or coreTypeDict['types'][ci]['tag'][
                            0] == 'compareR'):
                            transcross = {}
                            if type(coreTypeDict['types'][meais[0]]['id'][0]) is list:
                                # What is the network distance to primary schools for children aged between 4 and 12 in Multifunctional Urban Area in Rotterdam
                                trans_bef_id = coreTypeDict['types'][meais[0]]['id'][0][0]
                            else:
                                trans_bef_id = coreTypeDict['types'][meais[0]]['id'][0]
                            transcross['before'] = [trans_bef_id]
                            transcross['after'] = [str(core_id)]
                            coretrans.append(transcross)
                            coreConTrans.setdefault('types', []).append(
                                new_type(trans_bef_id))
                            core_id += 1
                        # elif len(coreTypeDict['types'][ci]['tag']) == 2 and coreTypeDict['types'][meais[0]]['tag'][0] != 'location':
                        #     # and (coreTypeDict['types'][ci]['tag'][0] == 'extremaR' or coreTypeDict['types'][ci]['tag'][0] == 'compareR')
                        #     trans_compR = {}
                        #     trans_compR['before'] = [coreTypeDict['types'][ci]['id'][0]]
                        #     trans_compR['after'] = [str(core_id)]
                        #     coretrans.append(trans_compR)
                        #     coreConTrans.setdefault('types', []).append(new_type(coreTypeDict['types'][ci]['id'][0]))
                        #     core_id += 1
                        #     transcross = {}
                        #     transcross['before'] = [trans_compR['after'][0], coreTypeDict['types'][meais[0]]['id'][0]]
                        #     transcross['after'] = [str(core_id)]
                        #     coretrans.append(transcross)
                        #     coreConTrans.setdefault('types', []).append(new_type(coreTypeDict['types'][meais[0]]['id'][0]))
                        #     core_id += 1
                        elif coreTypeDict['types'][meais[0]]['tag'][0] == 'location' or \
                                coreTypeDict['types'][meais[0]]['tag'][0] == 'allocation':
                            transcross = {}
                            transcross['before'] = [coreTypeDict['types'][ci]['id'][-1]]
                            transcross['after'] = [coreTypeDict['types'][meais[0]]['id'][-1]]
                            coretrans.append(transcross)
                        else:  # What houses are for sale and in neighborhoods with crime rate lower than 50 per 1000 people in Utrecht
                            transcross = {}
                            if type(coreTypeDict['types'][meais[0]]['id'][0]) is list:
                                transbef_id = coreTypeDict['types'][meais[0]]['id'][0][0]
                            else:
                                transbef_id= coreTypeDict['types'][meais[0]]['id'][0]
                            transcross['before'] = [transbef_id, coreTypeDict['types'][ci]['id'][-1]]
                            transcross['after'] = [str(core_id)]
                            coretrans.append(transcross)
                            coreConTrans.setdefault('types', []).append(new_type(transbef_id))
                            core_id += 1
                        # How many buildings are within 3 minutes of driving time from fire stations in Oleander
                        # Where are the flat areas within 500 meters of a major highway in the United Kingdom
                        if len(coreTypeDict['types'][meais[0]]['tag']) > 1:
                            if type(coreTypeDict['types'][meais[0]]['id'][0]) is list:
                                # What is the potential geographic access from communities to the sexual and productive health services located in rural areas
                                coreTypeDict['types'][meais[0]]['id'][0][0] = transcross['after'][0]
                            else:
                                coreTypeDict['types'][meais[0]]['id'][0] = transcross['after'][0]
                            mea_trans = write_trans_within(coreTypeDict['types'][meais[0]])
                            if coreTypeDict['types'][meais[0]]['tag'][-1] == "conAm":
                                mea_trans[0]['key'] = coreConTrans['extent'][0]
                            # if len(con_meais) > 1:
                            #     mea_trans[-1]['after'][0] = mea_trans[-1]['after'][0] + sign
                            coretrans.extend(mea_trans)
                            mc.append(mea_trans[-1]['after'][0])
                        else:
                            mc.append(transcross['after'][0])
                    if len(mc) > 1:
                        transcross = {}
                        transcross['before'] = mc
                        transcross['after'] = [str(core_id)]
                        coretrans.append(transcross)
                        coreConTrans.setdefault('types', []).append(new_type(mc[0]))
                        core_id += 1
                else:
                    if len(coreTypeDict['types'][meais[0]]['tag']) > 1:
                        if 'extreDist' in parseTree and not (any('network' in e for e in coreTypeDict['types'][meais[0]]['tag']) or any('destination' in e for e in coreTypeDict['types'][meais[0]]['tag'])):
                            transcross = {}
                            transcross['before'] = coreTypeDict['types'][meais[0]]['id']
                            transcross['after'] = [str(core_id)]
                            coretrans.append(transcross)
                            coreConTrans.setdefault('types', []).append(new_type(coreTypeDict['types'][meais[0]]['id'][-1]))
                        else:
                            mea_trans = write_trans_within(coreTypeDict['types'][meais[0]])
                            # -----new-------
                            if coreTypeDict['types'][meais[0]]['tag'][-1] == "conAm":
                                mea_trans[0]['key'] = coreConTrans['extent'][0]
                            # -----new-------
                            coretrans.extend(mea_trans)
                    else:
                        transcross = {}
                        transcross['before'] = [coreTypeDict['types'][meais[0]]['id'][0]]
                        transcross['after'] = [str(core_id)]
                        coreConTrans.setdefault('types', []).append(new_type(coreTypeDict['types'][meais[0]]['id'][0]))
                        coretrans.append(transcross)

        coreConTrans.setdefault('transformations', []).extend(coretrans)

        #print(coreConTrans)

    except:
        coreConTrans['transformations'] = []

    return coreConTrans


