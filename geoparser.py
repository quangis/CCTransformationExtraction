# [X] import antlr4 grammar
from antlr4 import *
from Grammar.GeoAnQuLexer import GeoAnQuLexer
from Grammar.GeoAnQuParser import GeoAnQuParser
from antlr4.tree.Trees import Trees


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


class Geoparser:
    que_stru = {'measure', 'measure1', 'condition', 'subcon', 'support'}
    measLevel = {'int_', 'nom_', 'rat_', 'cou_', 'loc_', 'ord_', 'era_', 'ira_', 'bool_'}

    # [SC] constructor
    def __init__(self):
        pass

    # [X] Extract every parser rule(tag) and text from parserTreeString
    # Output: {'tag': ['condition', 'boolR', 'extremaR', 'coreC', 'coreC', 'coreC'], 'text': ['of to', 'has', 'highest',
    # 'proportion 0 ira', 'object 1', 'objconamount 0 count']}
    def get_text(self, cur_treeStr):
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
    # Output: {'tag': ['extremaR', 'coreC', 'coreC', 'coreC'], 'text': ['highest', 'proportion 0 ira', 'object 1', 'objconamount 0 count']}
    def core_concept_extract(self, result, TreeDict):
        cur_TD = {}
        keep_set = {'coreC', 'networkC', 'networkQ', 'objectQ', 'location', 'allocation', 'conAm', 'conAmount', 'boolField', 'distField',
                    'serviceObj', 'aggre', 'compareR', 'mergeO', 'extremaR','visible'}
        tag_in = [i for i, x in enumerate(TreeDict['tag']) if not x in keep_set]
        cur_TD['tag'] = [TreeDict['tag'][i] for i in range(0, len(TreeDict['tag'])) if i not in tag_in]
        for i in range(0, len(cur_TD['tag'])):
            if cur_TD['tag'][i] == 'boolField' or cur_TD['tag'][i] == 'distField' or cur_TD['tag'][i] == 'serviceObj':
                cur_TD['tag'][i] = cur_TD['tag'][i].lower()
        cur_TD['text'] = [TreeDict['text'][i] for i in range(0, len(TreeDict['text'])) if i not in tag_in]

        # at least 3000 meters from the rivers or Where are the luxury hotels with more than 20 bedrooms {'tag': ['compareR', 'coreC'], 'text': ['more than', 'object 1']}
        # and ('boolfield' in cur_TD['tag'] or (len(cur_TD['tag']) == 2 and cur_TD['tag'].index('compareR') + 1 < 2 and cur_TD['tag'][cur_TD['tag'].index('compareR') + 1] == 'coreC')) remove compreR
        if 'compareR' in cur_TD['tag']:
            compR_index = [x for x, y in enumerate(cur_TD['tag']) if y == 'compareR']
            for cur_ci in compR_index:
                compR_list = cur_TD['text'][cur_ci].split()
                cur_TD['text'][cur_ci] = result[compR_list[0]][int(compR_list[1])]

        # where is the most popular ski piste {'tag': ['location', 'extremaR', 'coreC'], 'text': ['where is', 'most popular', 'object 0']}
        if 'extremaR' in cur_TD['tag']:
            ext_index = [x for x, y in enumerate(cur_TD['tag']) if y == 'extremaR']
            for cur_ei in ext_index:
                ext_list = cur_TD['text'][cur_ei].split()
                cur_TD['text'][cur_ei] = result[ext_list[0]][int(ext_list[1])]
        return cur_TD


    # [X]Write core concepts in the questions into the designed structure
    # Input dictionary: {'tag': ['origin', 'destination', 'networkC', 'serviceObj', 'boolField'],
    # 'text': [['object 1', 'hexagonal grids with diameter of 2000 meters'], 'object 0', 'network 0', 'from to', '']}
    # Output[0]: [{'type': ['object'], 'id': '0', 'keyword': 'centroid'}, {...}, ...]
    # Output[1]:{'tag': ['origin', 'destination', 'networkC', 'serviceObj', 'boolField'],
    # 'text': [['object 1', 'hexagonal grids with diameter of equantity 1'], 'object 0', 'network 0', 'from to', ''],
    # 'id': [['0', '1'], '2', '3', '4']}
    def write_type(self, result, core_id, coreDict):
        corety = []
        csign = 0
        netsign = 0

        for cur_tag in coreDict['tag']:
            curtag_index = coreDict['tag'].index(cur_tag)
            if cur_tag == 'distfield' or cur_tag == 'allocation':
                coreType = {}
                coreType['type'] = cur_tag
                coreType['id'] = str(core_id)
                coreType['keyword'] = ''
                corety.append(coreType)
                coreDict.setdefault('id', []).insert(curtag_index, str(core_id))
                core_id += 1
            elif cur_tag == 'location':
                if coreDict['text'] == ['what areas'] or coreDict['text'] == ['what area']:
                    coreType = {}
                    coreType['type'] = 'region'
                    coreType['id'] = str(core_id)
                    coreType['keyword'] = coreDict['text'][0][5:]
                    corety.append(coreType)
                    coreDict.setdefault('id', []).insert(curtag_index, str(core_id))
                    coreDict['tag'] = ['coreC']
                    coreDict['text'] = ['region']
                    core_id += 1
                else:
                    coreType = {}
                    coreType['type'] = cur_tag
                    coreType['id'] = str(core_id)
                    coreType['keyword'] = ''
                    corety.append(coreType)
                    coreDict.setdefault('id', []).insert(curtag_index, str(core_id))
                    core_id += 1
            elif cur_tag == 'boolfield' and 'serviceobj' not in coreDict['tag']:
                coreType = {}
                coreType['type'] = cur_tag
                coreType['id'] = str(core_id)
                coreType['keyword'] = ''
                corety.append(coreType)
                coreDict.setdefault('id', []).insert(curtag_index, str(core_id))
                # coreDict.setdefault('id', []).append(str(core_id))
                core_id += 1
            elif cur_tag == 'conAm':
                coreType = {}
                coreType['type'] = 'conamount'
                coreType['id'] = str(core_id)
                coreType['keyword'] = 'how many'
                coreType['measureLevel'] = 'cou_'
                corety.append(coreType)
                coreDict.setdefault('id', []).insert(curtag_index, str(core_id))
                # coreDict.setdefault('id', []).append(str(core_id))
                core_id += 1
            elif cur_tag == 'objectQ':
                coreType = {}
                coreType['type'] = 'objectquality'
                coreType['id'] = str(core_id)
                objQ = coreDict['text'][curtag_index].split()
                coreType['keyword'] = result[objQ[0]][int(objQ[1])]
                coreType['measureLevel'] = objQ[2]
                corety.append(coreType)
                coreDict.setdefault('id', []).insert(curtag_index, str(core_id))
                # coreDict.setdefault('id', []).append(str(core_id))
                core_id += 1
            elif cur_tag == 'conAmount':
                coreType = {}
                coreType['type'] = 'conamount'
                coreType['id'] = str(core_id)
                coreType['keyword'] = ''
                coreType['measureLevel'] = 'cou_'
                corety.append(coreType)
                coreDict.setdefault('id', []).insert(curtag_index, str(core_id))
                # coreDict.setdefault('id', []).append(str(core_id))
                core_id += 1
            elif cur_tag == 'grid' or cur_tag == 'distanceBand':
                coreType = {}
                coreType['type'] = cur_tag
                coreType['id'] = str(core_id)
                coreType['keyword'] = coreDict['text'][coreDict['tag'].index(cur_tag)]
                corety.append(coreType)
                coreDict.setdefault('id', []).insert(curtag_index, str(core_id))
                # coreDict.setdefault('id', []).append(str(core_id))
                core_id += 1
            elif cur_tag == 'aggre':
                coreType = {}
                coreType['type'] = cur_tag
                coreType['id'] = str(core_id)
                # curtag_index = coreDict['tag'].index(cur_tag)
                coreType['keyword'] = result['aggregate'][0]
                if coreDict['tag'][curtag_index - 1] == 'extreDist' and coreDict['text'][curtag_index - 2].split(' ')[
                    -1] in Geoparser.measLevel:
                    coreType['measureLevel'] = coreDict['text'][curtag_index - 2].split(' ')[-1]
                elif coreDict['text'][curtag_index - 1].split(' ')[-1] in Geoparser.measLevel:
                    coreType['measureLevel'] = coreDict['text'][curtag_index - 1].split(' ')[-1]
                corety.append(coreType)
                coreDict.setdefault('id', []).insert(curtag_index, str(core_id))
                core_id += 1
            elif cur_tag == 'mergeO':
                coreType = {}
                previous_CoreC = coreDict['text'][coreDict['tag'].index('mergeO')-1]
                coreType['type'] = previous_CoreC.split()[0] # type of mergeO is based on the type of the previous coreC
                coreType['id'] = str(core_id)
                coreType['keyword'] = 'merge layer'
                if len(previous_CoreC.split()) == 3:
                    coreType['measureLevel'] = previous_CoreC[2]
                corety.append(coreType)
                coreDict.setdefault('id', []).insert(curtag_index, str(core_id))
                # coreDict.setdefault('id', []).append(str(core_id))
                core_id += 1
            elif cur_tag == 'networkC':
                # read network keywords
                if netsign == 1:
                    continue
                else:
                    net_locs = [x for x, y in enumerate(coreDict['tag']) if y == cur_tag]
                    for nloc in net_locs:
                        coreType = {}
                        nts = coreDict['text'][nloc].split(' ')
                        coreType['type'] = nts[0]
                        coreType['id'] = str(core_id)
                        coreType['keyword'] = result[nts[0]][int(nts[1])]  # e.g., driving time, network distance
                        corety.append(coreType)
                        coreDict.setdefault('id', []).insert(nloc, str(core_id))
                        # coreDict.setdefault('id', []).append(str(core_id))
                        core_id += 1
                    netsign += 1
            elif cur_tag == 'networkQ':
                coreType = {}
                nts = coreDict['text'][coreDict['tag'].index('networkQ')].split(' ')
                coreType['type'] = nts[0]
                coreType['id'] = str(core_id)
                coreType['keyword'] = result[nts[0]][int(nts[1])]  # e.g., driving time, network distance
                coreType['measureLevel'] = nts[2]
                corety.append(coreType)
                coreDict.setdefault('id', []).insert(curtag_index, str(core_id))
                # coreDict.setdefault('id', []).append(str(core_id))
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
            elif cur_tag == 'visible':
                coreType = {}
                coreType['type'] = 'field'
                coreType['id'] = str(core_id)
                coreType['keyword'] = 'slope'
                coreType['measureLevel'] = 'rat_'
                corety.append(coreType)
                coreDict.setdefault('id', []).insert(curtag_index, str(core_id))
                coreDict['tag'] = ['visible']
                coreDict['text'] = ['field']
                core_id += 1
            elif cur_tag == 'extent':
                for p in result['placename']:
                    coreType = {}
                    coreType['type'] = 'object'
                    coreType['id'] = str(core_id)
                    coreType['keyword'] = p # result['placename'][int(coreDict['text'][0].split(' ')[1])]
                    corety.append(coreType)
                    coreDict.setdefault('id', []).append(str(core_id))
                    core_id += 1
            elif cur_tag == "extremaR" or cur_tag == "compareR":
                coreDict.setdefault('id', []).insert(curtag_index, '')

        coreDict['id'] = [value for value in coreDict['id'] if value != '']

        return corety, coreDict, core_id


    # [X] Generate parser tree of question by the GeoAnQu grammar and extract core concept transformations
    def geo_parser(self, result, core_id, coreTypeDict, coreConTrans):
        sentence = result['ner_Question']

        wei_len = 0

        input = InputStream(sentence)  # [X]sentence =  'What areas are with slope larger than 10 in Spain'
        lexer = GeoAnQuLexer(input)  # get lexer rule
        stream = CommonTokenStream(lexer)  # token stream to tokens
        parser = GeoAnQuParser(stream)
        try:
            tree = parser.start()  # [X] get parsed tree of the sentence
            treeStr = Trees.toStringTree(tree, None, parser)  # Print out a whole tree in LISP form
            quesTextDic = self.get_text(treeStr)

            sequence = [ele for ele in quesTextDic['tag'] if ele in Geoparser.que_stru]
            sequence.reverse()

            # print('treeStr\n', treeStr)
            # print('quesTextDic\n', quesTextDic)
            # print('sequence\n', sequence)

            if 'condition' in sequence:
                conCores = []
                con_count = treeStr.count('condition')
                for cur_i in range(0, con_count):
                    con_treeStr = Trees.toStringTree(tree.condition(cur_i), None, parser)
                    conTextDic_ori = self.get_text(con_treeStr)
                    if 'subcon' in con_treeStr:
                        subcon_treeStr = Trees.toStringTree(tree.condition(cur_i).subcon(), None, parser)
                        subconTextDic = self.get_text(subcon_treeStr)
                        subconCore = self.core_concept_extract(result, subconTextDic)
                        subconCore['tag'].reverse()
                        subconCore['text'].reverse()
                        # print('subconCore\n', subconCore)
                        # remove concepts in subcon from con
                        subcon_index = conTextDic_ori['tag'].index('subcon')
                        conTextDic = {}
                        conTextDic['tag'] = conTextDic_ori['tag'][:subcon_index]
                        conTextDic['text'] = conTextDic_ori['text'][:subcon_index]
                    else:
                        conTextDic = conTextDic_ori
                    conCore = self.core_concept_extract(result, conTextDic)
                    if 'destination' in conTextDic['tag']:
                        des_list = []
                        if 'serviceObj' in conTextDic['tag']:
                            destination = tree.condition(cur_i).boolField().serviceObj().destination()
                            dest_childCount = destination.getChildCount()
                        elif 'distField' in conTextDic['tag']:
                            destination = tree.condition(cur_i).boolField().distField().destination()
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
                            origin = tree.condition(cur_i).boolField().distField().origin()
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
                                ori_text = result[ori_text[:4]][int(ori_text[-1])]
                                ori_list.append(ori_text.strip())
                                # ori_list in forward order, e.g, [object0, grid], object = centroid
                            elif 'placename' in ori_text:
                                ori_text = ori_text[:-1] + ' ' + ori_text[-1]
                                ori_list.append(ori_text.strip())
                        ori_list.reverse()
                        conCore['tag'].append('origin')
                        conCore['text'].append(ori_list)
                    if 'grid' in conTextDic['tag'] and 'origin' not in conTextDic['tag'] and 'destination' not in \
                            conTextDic['tag']:
                        cgrid_text = tree.condition(cur_i).grid().getText()
                        cgrid_text = result[cgrid_text[:4]][int(cgrid_text[-1])]
                        conCore['tag'].append('grid')
                        conCore['text'].append(cgrid_text)
                    conCore['tag'].reverse()
                    conCore['text'].reverse()
                    conCores.insert(0, conCore)

            if 'measure' in sequence:
                mea_treeStr = Trees.toStringTree(tree.measure(), None, parser)
                meaTextDic = self.get_text(mea_treeStr)
                meaCore = self.core_concept_extract(result, meaTextDic)
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
                    origin = tree.measure().origin()
                    ori_childCount = origin.getChildCount()
                    ori_list = []
                    for o_i in range(0, ori_childCount):
                        ori_text = origin.getChild(o_i).getText()
                        if 'object' in ori_text or 'event' in ori_text:
                            ori_text = ori_text[:-1] + ' ' + ori_text[-1]
                            ori_list.append(ori_text)
                        elif 'grid' in ori_text:
                            ori_text = result[ori_text[:4]][int(ori_text[-1])]
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
                mea1_treeStr = Trees.toStringTree(tree.measure1(0), None, parser)
                mea1TreeDic = self.get_text(mea1_treeStr)
                mea1Core = self.core_concept_extract(result, mea1TreeDic)
                mea1Core['tag'].reverse()
                mea1Core['text'].reverse()

            for seq in sequence:
                if seq == 'measure':
                    meaTypes = self.write_type(result, core_id, meaCore)
                    coreConTrans.setdefault('types', []).extend(meaTypes[0])  # type info in the final results
                    coreTypeDict.setdefault('funcRole', []).append(seq)
                    coreTypeDict.setdefault('types', []).append(meaTypes[1])
                    core_id = meaTypes[2]
                    if wei_len:
                        coreTypeDict['weight'] = wei_len
                    # if 'aggre' not in meaTypes[1]['tag'][-1] and 'pro' not in meaTypes[1]['text'][-1] and 'conamount' not in \
                    #         meaTypes[1]['text'][-1] and 'covamount' not in meaTypes[1]['text'][-1]:
                    #     print('measure\t', meaTypes[1])
                elif seq == 'measure1':
                    mea1Types = self.write_type(result, core_id, mea1Core)
                    coreConTrans.setdefault('types', []).extend(mea1Types[0])
                    coreTypeDict.setdefault('funcRole', []).append(seq)
                    coreTypeDict.setdefault('types', []).append(mea1Types[1])
                    core_id = mea1Types[2]
                elif seq == 'condition':
                    conTypes = self.write_type(result, core_id, conCores[0])
                    coreConTrans.setdefault('types', []).extend(conTypes[0])
                    coreTypeDict.setdefault('funcRole', []).append(seq)
                    coreTypeDict.setdefault('types', []).append(conTypes[1])
                    conCores.pop(0)
                    core_id = conTypes[2]
                elif seq == 'subcon':
                    subconTypes = self.write_type(result, core_id, subconCore)
                    coreConTrans.setdefault('types', []).extend(subconTypes[0])
                    coreTypeDict.setdefault('funcRole', []).append(seq)
                    coreTypeDict.setdefault('types', []).append(subconTypes[1])
                    core_id = subconTypes[2]
                elif seq == 'support':
                    if 'sup_object' in result:
                        supTypes = ([{'type': 'object', 'id': str(core_id), 'keyword': result['sup_object'][0]}],
                                {'tag': ['support'], 'text': ['support'], 'id': [str(core_id)]})
                    elif 'sup_grid' in result:
                        supTypes = ([{'type': 'grid', 'id': str(core_id), 'keyword': result['sup_grid'][0]}],
                                    {'tag': ['support'], 'text': ['support'], 'id': [str(core_id)]})
                    elif 'sup_distBand' in result:
                        supTypes = ([{'type': 'distanceBand', 'id': str(core_id), 'keyword': result['sup_distBand'][0]}],
                                    {'tag': ['support'], 'text': ['support'], 'id': [str(core_id)]})
                    coreConTrans.setdefault('types', []).extend(supTypes[0])
                    coreTypeDict.setdefault('funcRole', []).append('support')
                    coreTypeDict.setdefault('types', []).append(supTypes[1])
                    core_id += 1

            if 'extent' in treeStr:
                ext_treeStr = Trees.toStringTree(tree.extent(), None, parser)
                extTextDic = self.get_text(ext_treeStr)
                extTypes = self.write_type(result, core_id, extTextDic)
                coreConTrans.setdefault('types', []).extend(extTypes[0])
                coreConTrans['extent'] = extTypes[1]['id']
                core_id = extTypes[2]
                coreTypeDict.setdefault('funcRole', []).append('extent')
                coreTypeDict.setdefault('types', []).append(extTypes[1]['id'])

            if 'temporalex' in treeStr:
                coreConTrans['temporalEx'] = result['temEx']
                coreTypeDict.setdefault('funcRole', []).append('temEx')
                coreTypeDict.setdefault('types', []).append(coreConTrans['temporalEx'])

            # print('coreTypes\n', coreTypes)
            # print('coreConTrans\n', coreConTrans)

        except:
            print("Question cannot be parsed.\n{}".format(result))

        return treeStr, coreTypeDict, coreConTrans, core_id
