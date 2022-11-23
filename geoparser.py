import re
# [X] import antlr4 grammar
from antlr4 import *
from Grammar.GeoAnQuLexer import GeoAnQuLexer
from Grammar.GeoAnQuParser import GeoAnQuParser
from antlr4.tree.Trees import Trees

que_stru = {'measure', 'measure1', 'condition', 'subcon', 'support'}
measLevel = {'interval', 'nominal', 'ratio', 'count', 'loc', 'ordinal', 'era', 'ira', 'boolean'}

class BracketMatch:
    def __init__(self, refstr, parent=None, start=-1, end=-1):
        self.parent = parent
        self.start = start
        self.end = end
        self.refstr = refstr
        self.nested_matches = []

    def __str__(self):
        cur_index = self.start + 1
        result = ""
        if self.start == -1 or self.end == -1:
            return ""
        for child_match in self.nested_matches:
            if child_match.start != -1 and child_match.end != -1:
                result += self.refstr[cur_index:child_match.start]
                cur_index = child_match.end + 1
            else:
                continue
        result += self.refstr[cur_index:self.end]
        return result


# [X] Extract parser rules(tags) and text from parserTreeString
def get_text(cur_treeStr):
    nodetextDic = {}
    root = BracketMatch(cur_treeStr)
    cur_match = root
    for i in range(len(cur_treeStr)):
        if '(' == cur_treeStr[i]:
            new_match = BracketMatch(cur_treeStr, cur_match, i)
            cur_match.nested_matches.append(new_match)
            cur_match = new_match
        elif ')' == cur_treeStr[i]:
            cur_match.end = i
            cur_match = cur_match.parent
        else:
            continue
    # Here we built the set of matches, now we must print them
    nodes_list = root.nested_matches
    tag = []
    # So we conduct a BFS to visit and print each match...
    while nodes_list != []:
        node = nodes_list.pop(0)
        nodes_list.extend(node.nested_matches)
        nodeStr = str(node).strip()
        nodetextDic.setdefault('tag', []).append(nodeStr.split()[0])
        nodetextDic.setdefault('text', []).append(' '.join(nodeStr.split()[1:][0:len(nodeStr.split()[1:])]))

    return nodetextDic


# [X]Extract core concept from texts and tags of the parse tree
# Input: {'tag': ['condition', 'boolR', 'extremaR', 'coreC', 'coreC', 'coreC'], 'text': ['of to', 'has', 'highest',
# 'proportion 0 ira', 'object 1', 'objconamount 0 count']}
# Output: {'tag': ['coreC', 'coreC', 'coreC'], 'text': ['proportion 0 ira', 'object 1', 'objconamount 0 count']}
def core_concept_extract(TreeDict):
    cur_TD = {}
    keep_set = {'coreC', 'networkC', 'networkQ', 'location', 'allocation', 'conAm', 'boolField', 'distField',
                'serviceObj', 'aggre', 'compareR'}  # 'extremaR',
    tag_in = [i for i, x in enumerate(TreeDict['tag']) if not x in keep_set]
    cur_TD['tag'] = [TreeDict['tag'][i] for i in range(0, len(TreeDict['tag'])) if i not in tag_in]
    for i in range(0, len(cur_TD['tag'])):
        if cur_TD['tag'][i] == 'boolField' or cur_TD['tag'][i] == 'distField' or cur_TD['tag'][i] == 'serviceObj':
            cur_TD['tag'][i] = cur_TD['tag'][i].lower()
    cur_TD['text'] = [TreeDict['text'][i] for i in range(0, len(TreeDict['text'])) if i not in tag_in]

    # at least 3000 meters from the rivers or Where are the luxury hotels with more than 20 bedrooms {'tag': ['compareR', 'coreC'], 'text': ['more than', 'object 1']}
    if 'compareR' in cur_TD['tag'] and ('boolfield' in cur_TD['tag'] or (
            len(cur_TD['tag']) == 2 and cur_TD['tag'].index('compareR') + 1 < 2 and cur_TD['tag'][
        cur_TD['tag'].index('compareR') + 1] == 'coreC')):
        compR_index = cur_TD['tag'].index('compareR')
        cur_TD['tag'].pop(compR_index)
        cur_TD['text'].pop(compR_index)

    # from origin to the nearest destination, add extreDist(nearest) to cur_TD
    if 'extreDist' in TreeDict['tag'] and (
            'networkC' in TreeDict['tag'] or 'networkQ' in TreeDict['tag']) and 'serviceObj' not in TreeDict['tag']:
        cur_in = [cur_TD['tag'].index(i) for i in TreeDict['tag'] if i.startswith('network')][0]
        cur_TD['tag'].insert(cur_in, 'extreDist')
        cur_TD['text'].insert(cur_in, TreeDict['text'][TreeDict['tag'].index('extreDist')])

    return cur_TD


# [X]Write core concepts in the questions into the designed structure
# Input dictionary: {'tag': ['origin', 'destination', 'networkC', 'serviceObj', 'boolField'],
# 'text': [['object 1', 'hexagonal grids with diameter of 2000 meters'], 'object 0', 'network 0', 'from to', '']}
# Output[0]: [{'type': ['object'], 'id': '0', 'keyword': 'centroid'}, {...}, ...]
# Output[1]:{'tag': ['origin', 'destination', 'networkC', 'serviceObj', 'boolField'],
# 'text': [['object 1', 'hexagonal grids with diameter of equantity 1'], 'object 0', 'network 0', 'from to', ''],
# 'id': [['0', '1'], '2', '3', '4']}
def write_type(result, core_id, coreDict):
    corety = []
    csign = 0

    #--------new---------
    for cur_tag in coreDict['tag']:
        if cur_tag == 'distfield' or cur_tag == 'location' or cur_tag == 'allocation': #--------new---------
            coreType = {}
            coreType['type'] = cur_tag
            coreType['id'] = str(core_id)
            coreType['keyword'] = ''
            corety.append(coreType)
            coreDict.setdefault('id', []).append(str(core_id))
            core_id += 1
        elif cur_tag == 'boolfield' and 'serviceobj' not in coreDict['tag']: #--------new---------
            coreType = {}
            coreType['type'] = cur_tag
            coreType['id'] = str(core_id)
            coreType['keyword'] = ''
            corety.append(coreType)
            coreDict.setdefault('id', []).append(str(core_id))
            core_id += 1
        elif cur_tag == 'conAm':
            coreType = {}
            coreType['type'] = 'conamount'
            coreType['id'] = str(core_id)
            # -------new-----
            coreType['keyword'] = 'how many'
            coreType['measureLevel'] = 'count'
            # -------new-----
            corety.append(coreType)
            coreDict.setdefault('id', []).append(str(core_id))
            core_id += 1
        elif cur_tag == 'grid' or cur_tag == 'distanceBand':
            coreType = {}
            coreType['type'] = cur_tag
            coreType['id'] = str(core_id)
            coreType['keyword'] = coreDict['text'][coreDict['tag'].index(cur_tag)]
            corety.append(coreType)
            coreDict.setdefault('id', []).append(str(core_id))
            core_id += 1
        elif cur_tag == 'aggre':
            coreType = {}
            coreType['type'] = cur_tag
            coreType['id'] = str(core_id)
            curtag_index = coreDict['tag'].index(cur_tag)
            coreType['keyword'] = coreDict['text'][curtag_index]
            if coreDict['tag'][curtag_index - 1] == 'extreDist' and coreDict['text'][curtag_index - 2].split(' ')[
                -1] in measLevel:
                coreType['measureLevel'] = coreDict['text'][curtag_index - 2].split(' ')[-1]
            elif coreDict['text'][curtag_index - 1].split(' ')[-1] in measLevel:
                coreType['measureLevel'] = coreDict['text'][curtag_index - 1].split(' ')[-1]
            corety.append(coreType)
            coreDict.setdefault('id', []).append(str(core_id))
            core_id += 1
        elif cur_tag == 'networkC':
            # read network keywords
            coreType = {}
            nts = coreDict['text'][coreDict['tag'].index('networkC')].split(' ')
            coreType['type'] = nts[0]
            coreType['id'] = str(core_id)
            coreType['keyword'] = result[nts[0]][int(nts[1])]  # e.g., driving time, network distance
            corety.append(coreType)
            coreDict.setdefault('id', []).append(str(core_id))
            core_id += 1
        elif cur_tag == 'networkQ':
            coreType = {}
            nts = coreDict['text'][coreDict['tag'].index('networkQ')].split(' ')
            coreType['type'] = nts[0]
            coreType['id'] = str(core_id)
            coreType['keyword'] = result[nts[0]][int(nts[1])]  # e.g., driving time, network distance
            coreType['measureLevel'] = nts[2]
            corety.append(coreType)
            coreDict.setdefault('id', []).append(str(core_id))
            core_id += 1
        elif cur_tag == 'coreC':
            if csign == 1:
                continue
            else:
                clocs = [x for x, y in enumerate(coreDict['tag']) if y == cur_tag]
                for cloc in clocs:
                    coreType = {}
                    cts = coreDict['text'][cloc].split(' ')
                    if len(cts) == 2:  # object 0
                        coreType['type'] = cts[0]
                        coreType['id'] = str(core_id)
                        coreType['keyword'] = result[cts[0]][int(cts[1])]
                        corety.append(coreType)
                        coreDict.setdefault('id', []).append(str(core_id))
                        core_id += 1
                    elif len(cts) == 3:  # # eveconobjconpro 0 ira
                        coreType['type'] = cts[0]
                        coreType['id'] = str(core_id)
                        coreType['keyword'] = result[cts[0]][int(cts[1])]
                        coreType['measureLevel'] = cts[2]
                        corety.append(coreType)
                        coreDict.setdefault('id', []).append(str(core_id))
                        core_id += 1
                csign += 1
        elif cur_tag == 'destination':
            des_id = []
            for d in coreDict['text'][coreDict['tag'].index(cur_tag)]:
                coreType = {}
                dtext = d.split(' ')
                if dtext[0] == 'placename':
                    coreType['type'] = 'object'
                else:
                    coreType['type'] = dtext[0]
                coreType['id'] = str(core_id)
                coreType['keyword'] = result[dtext[0]][int(dtext[1])]
                corety.append(coreType)
                des_id.append(str(core_id))
                core_id += 1
            coreDict.setdefault('id', []).append(des_id)
        elif cur_tag == 'origin':
            ori_id = []
            for o in coreDict['text'][coreDict['tag'].index(cur_tag)]:
                coreType = {}
                if 'grid' in o:
                    coreType['type'] = 'grid'
                    coreType['id'] = str(core_id)
                    coreType['keyword'] = o
                    corety.append(coreType)
                    ori_id.append(str(core_id))
                    core_id += 1
                else:
                    otext = o.split(' ')
                    if otext[0] == 'placename':
                        coreType['type'] = 'object'
                    else:
                        coreType['type'] = otext[0]
                    coreType['id'] = str(core_id)
                    coreType['keyword'] = result[otext[0]][int(otext[1])]
                    corety.append(coreType)
                    ori_id.append(str(core_id))
                    core_id += 1
            coreDict.setdefault('id', []).append(ori_id)
        elif cur_tag == 'extent':
            coreType = {}
            coreType['type'] = 'object'
            coreType['id'] = str(core_id)
            coreType['keyword'] = result['placename'][int(coreDict['text'][0].split(' ')[1])]
            corety.append(coreType)
            coreDict.setdefault('id', []).append(str(core_id))
            core_id += 1

    return corety, coreDict, core_id


# [X] Generate parser tree of question by the GeoAnQu grammar and extract core concept transformations
def geo_parser(result, core_id, coreConTrans):

    ques_incorrect = ''
    sentence = result['ner_Question']

    coreTypes = {}
    wei_len = 0

    input = InputStream(sentence)  # [X]sentence =  'What areas are with slope larger than 10 in Spain'
    lexer = GeoAnQuLexer(input)  # get lexer rule
    stream = CommonTokenStream(lexer)  # token stream to tokens
    parser = GeoAnQuParser(stream)
    try:
        tree = parser.start()  # [X] get parsed tree of the sentence
        treeStr = Trees.toStringTree(tree, None, parser)  # Print out a whole tree in LISP form
        quesTextDic = get_text(treeStr)

        sequence = [ele for ele in quesTextDic['tag'] if ele in que_stru]
        sequence.reverse()

        if 'condition' in sequence:
            conCores = []
            con_count = treeStr.count('condition')
            for cur_i in range(0, con_count):
                con_treeStr = Trees.toStringTree(tree.condition(cur_i), None, parser)
                conTextDic = get_text(con_treeStr)
                if 'date' in conTextDic['tag'] and 'coreC' not in conTextDic['tag']:
                    conCore = {}
                    conCore['tag'] = ['compareR']
                    conCore['text'] = [conTextDic['text'][conTextDic['tag'].index('date')]]
                else:
                    conCore = core_concept_extract(conTextDic)
                if 'destination' in conTextDic['tag']:
                    des_list = []
                    if 'serviceObj' in conTextDic['tag']:
                        destination = tree.condition(cur_i).boolField().serviceObj().destination()
                        dest_childCount = destination.getChildCount()
                    elif 'distField' in conTextDic['tag']:
                        destination = tree.condition(cur_i).boolField().distField().destination(0)
                        dest_childCount = destination.getChildCount()
                    else:
                        destination = tree.condition(cur_i).destination()
                        dest_childCount = destination.getChildCount()
                    for d_i in range(0, dest_childCount):
                        dest_text = destination.getChild(d_i).getText()
                        if 'object' in dest_text or 'event' in dest_text:
                            dest_text = dest_text[:-1] + ' ' + dest_text[-1]
                            des_list.append(dest_text)
                        elif 'placename' in dest_text:
                            dest_text = dest_text[:-1] + ' ' + dest_text[-1]
                            des_list.append(dest_text)
                    des_list.reverse()
                    conCore['tag'].append('destination')
                    conCore['text'].append(des_list)
                if 'origin' in conTextDic['tag']:  # 'centriods of object/grid' or 'object' or 'grid'
                    if 'serviceObj' in conTextDic['tag']:
                        origin = tree.condition(cur_i).boolField().serviceObj().origin()
                        ori_childCount = origin.getChildCount()
                    elif 'distField' in conTextDic['tag']:
                        origin = tree.condition(cur_i).boolField().distField().origin(0)
                        ori_childCount = origin.getChildCount()
                    else:
                        origin = tree.condition(cur_i).origin()
                        ori_childCount = origin.getChildCount()
                    for o_i in range(0, ori_childCount):
                        ori_list = []
                        ori_text = origin.getChild(o_i).getText()
                        if 'object' in ori_text or 'event' in ori_text:
                            ori_text = ori_text[:-1] + ' ' + ori_text[-1]
                            ori_list.append(ori_text)
                        elif 'grid' in ori_text:
                            if 'equantity' in ori_text:
                                ein = ori_text.index('equantity') + 9
                                ori_text = ori_text.replace('equantity' + ori_text[ein],
                                                            result['quantity'][int(ori_text[ein])] + ' ')
                            if 'of' in ori_text:
                                ori_text = ori_text.replace('of', 'of ')
                            if 'with' in ori_text:
                                ori_text = ori_text.replace('with', ' with ')
                            ori_list.append(ori_text.strip())
                            # ori_list in forward order, e.g, [object0, grid], object = centroid
                        elif 'placename' in ori_text:
                            ori_text = ori_text[:-1] + ' ' + ori_text[-1]
                            ori_list.append(ori_text.strip())
                    #-------new---------
                    ori_list.reverse()
                    conCore['tag'].append('origin')
                    conCore['text'].append(ori_list)
                    # -------new---------
                if 'grid' in conTextDic['tag'] and 'origin' not in conTextDic['tag'] and 'destination' not in \
                        conTextDic['tag']:
                    cgrid_text = tree.condition(cur_i).grid().getText()
                    if 'equantity' in cgrid_text:
                        ein = cgrid_text.index('equantity') + 9
                        cgrid_text = cgrid_text.replace('equantity' + cgrid_text[ein],
                                                        result['quantity'][int(cgrid_text[ein])] + ' ')
                    conCore['tag'].append('grid')
                    conCore['text'].append(cgrid_text)
                conCore['tag'].reverse()
                conCore['text'].reverse()
                conCores.insert(0, conCore)

        if 'measure' in sequence:
            mea_treeStr = Trees.toStringTree(tree.measure(), None, parser)
            meaTextDic = get_text(mea_treeStr)
            meaCore = core_concept_extract(meaTextDic)
            if 'destination' in meaTextDic['tag']:
                destination = tree.measure().destination(0)
                dest_childCount = destination.getChildCount()  # 'closest object0', childcount = 2
                des_list = []
                for d_i in range(0, dest_childCount):
                    dest_text = destination.getChild(d_i).getText()
                    if 'object' in dest_text or 'event' in dest_text:
                        dest_text = dest_text[:-1] + ' ' + dest_text[-1]
                        des_list.append(dest_text)
                    elif 'placename' in dest_text:
                        dest_text = dest_text[:-1] + ' ' + dest_text[-1]
                        des_list.append(dest_text.strip())
                des_list.reverse()
                meaCore['tag'].append('destination')
                meaCore['text'].append(des_list)
            if 'origin' in meaTextDic['tag']:  # 'centriods of object/grid' or 'object' or 'grid'
                origin = tree.measure().origin(0)
                ori_childCount = origin.getChildCount()
                ori_list = []
                for o_i in range(0, ori_childCount):
                    ori_text = origin.getChild(o_i).getText()
                    if 'object' in ori_text or 'event' in ori_text:
                        ori_text = ori_text[:-1] + ' ' + ori_text[-1]
                        ori_list.append(ori_text)
                    elif 'grid' in ori_text:
                        if 'equantity' in ori_text:
                            ein = ori_text.index('equantity') + 9
                            ori_text = ori_text.replace('equantity' + ori_text[ein],
                                                        result['quantity'][int(ori_text[ein])] + ' ')
                        if 'of' in ori_text:
                            ori_text = ori_text.replace('of', 'of ')
                        if 'with' in ori_text:
                            ori_text = ori_text.replace('with', ' with ')
                        ori_list.append(ori_text.strip())
                        # ori_list in forward order, e.g, [object0, grid], object = centroid
                    elif 'placename' in ori_text:
                        ori_text = ori_text[:-1] + ' ' + ori_text[-1]
                        ori_list.append(ori_text.strip())
                ori_list.reverse()
                if 'destination' in meaTextDic['tag'] and quesTextDic['tag'].index('destination') > quesTextDic['tag'].index('origin'):
                    meaCore['text'].insert(meaCore['tag'].index('destination'), ori_list)
                    meaCore['tag'].insert(meaCore['tag'].index('destination'),'origin')
                else:
                    meaCore['tag'].append('origin')
                    meaCore['text'].append(ori_list)
            meaCore['tag'].reverse()
            meaCore['text'].reverse()
            if 'weight' in meaTextDic['tag']:
                wei_loc = meaTextDic['tag'].index('weight')
                wei_len = len(meaTextDic['tag']) - wei_loc - 1

        if 'measure1' in sequence:
            mea1_treeStr = Trees.toStringTree(tree.measure1(), None, parser)
            mea1TreeDic = get_text(mea1_treeStr)
            mea1Core = core_concept_extract(mea1TreeDic)

        if 'subcon' in sequence:
            subcon_treeStr = Trees.toStringTree(tree.subcon(), None, parser)
            subconTextDic = get_text(subcon_treeStr)
            subconCore = core_concept_extract(subconTextDic)
            subconCore['tag'].reverse()
            subconCore['text'].reverse()

        if 'support' in sequence:
            sup_treeStr = Trees.toStringTree(tree.support(), None, parser)
            supTextDic = get_text(sup_treeStr)
            supCore = core_concept_extract(supTextDic)
            if 'grid' in supTextDic['tag']:
                grid_text = tree.support().grid().getText()
                if 'equantity' in grid_text:
                    ein = grid_text.index('equantity') + 9
                    grid_text = grid_text.replace('equantity' + grid_text[ein],
                                                  result['quantity'][int(grid_text[ein])] + ' ')
                supCore['tag'].append('grid')
                supCore['text'].append(grid_text)
            if 'distBand' in supTextDic['tag']:
                distBand_text = tree.support().distBand().getText()
                if 'equantity' in distBand_text:
                    eins = [m.start() for m in re.finditer('equantity', distBand_text)]
                    e = 9
                    for ein in eins:
                        distBand_text = distBand_text.replace('equantity' + distBand_text[ein + e],
                                                              ' equantity ' + distBand_text[ein + e] + ' ')
                        e = e + 3
                    dBts = distBand_text.split(' ')
                    eqins = [x for x, y in enumerate(dBts) if y == 'equantity']
                    qlocs = []
                    for eqin in eqins:
                        qlocs.append(dBts[eqin + 1])
                    for qloc in qlocs:
                        distBand_text = distBand_text.replace(
                            'equantity ' + distBand_text[distBand_text.index('equantity') + 10],
                            result['quantity'][int(qloc)])
                supCore['tag'].append('distanceBand')
                supCore['text'].append(distBand_text.strip())
            supCore['tag'].reverse()
            supCore['text'].reverse()

        for seq in sequence:
            if seq == 'measure':
                meaTypes = write_type(result, core_id, meaCore)
                coreConTrans.setdefault('types', []).extend(meaTypes[0])  # type info in the final results
                coreTypes.setdefault('funcRole', []).append(seq)
                coreTypes.setdefault('types', []).append(meaTypes[1])
                core_id = meaTypes[2]
                if wei_len:
                    coreTypes['weight'] = wei_len
            elif seq == 'measure1':
                mea1Types = write_type(result, core_id, mea1Core)
                coreConTrans.setdefault('types', []).extend(mea1Types[0])
                coreTypes.setdefault('funcRole', []).append(seq)
                coreTypes.setdefault('types', []).append(mea1Types[1])
                core_id = mea1Types[2]
            elif seq == 'condition':
                conTypes = write_type(result, core_id, conCores[0])
                coreConTrans.setdefault('types', []).extend(conTypes[0])
                coreTypes.setdefault('funcRole', []).append(seq)
                coreTypes.setdefault('types', []).append(conTypes[1])
                conCores.pop(0)
                core_id = conTypes[2]
            elif seq == 'subcon':
                subconTypes = write_type(result, core_id, subconCore)
                coreConTrans.setdefault('types', []).extend(subconTypes[0])
                coreTypes.setdefault('funcRole', []).append(seq)
                coreTypes.setdefault('types', []).append(subconTypes[1])
                core_id = subconTypes[2]
            elif seq == 'support':
                supTypes = write_type(result, core_id, supCore)
                coreConTrans.setdefault('types', []).extend(supTypes[0])
                coreTypes.setdefault('funcRole', []).append(seq)
                coreTypes.setdefault('types', []).append(supTypes[1])
                core_id = supTypes[2]

        ext_count = treeStr.count('extent')
        if ext_count:
            for cur_i in range(0, ext_count):
                ext_treeStr = Trees.toStringTree(tree.extent()[cur_i], None, parser)
                extTextDic = get_text(ext_treeStr)
                extTypes = write_type(result, core_id, extTextDic)
                coreConTrans.setdefault('types', []).extend(extTypes[0])
                coreConTrans.setdefault('extent', []).append(extTypes[1]['id'][0])
                core_id = extTypes[2]
            coreTypes.setdefault('funcRole', []).append('extent')
            coreTypes.setdefault('types', []).append(extTypes[1]['id'])

        tem_count = treeStr.count('temEx')
        if tem_count:
            for cur_t in range(0, tem_count):
                tem_treeStr = Trees.toStringTree(tree.temEx(cur_t), None, parser)
                temTextDic = get_text(tem_treeStr)
                temsp = temTextDic['text'][0].split(' ')
                coreConTrans.setdefault('temporalEx', []).append(result['date'][int(temsp[1])])
            coreTypes.setdefault('funcRole', []).append('temEx')
            coreTypes.setdefault('types', []).append(coreConTrans['temporalEx'])

        # print('coreTypes:', coreTypes)
        # print('coreConTrans:', coreConTrans)

    except:
        ques_incorrect = sentence

    return treeStr, coreTypes, coreConTrans, core_id, ques_incorrect


