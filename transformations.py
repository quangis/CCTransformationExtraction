import numpy as np

from DictManager import *


class TransformHandler:
    extre_Dict = DictManager.readExtremaR()

    # [SC] constructor
    def __init__(self):
        self.core_id = None
        self.coreConTrans = None
        self.coreTypeDict = None
        self.measureType = None
        self.supis = []
        self.meais = []
        self.con_meais = []
        self.mea1is = []


    # [X] Add core concept type of for extremaR and compareR
    def addext_type(self, e_keyword):
        e_index = TransformHandler.extre_Dict['keyword'].index(e_keyword)

        ext_type = {'type': TransformHandler.extre_Dict['cctag'][e_index], 'id': str(self.core_id),
                    'keyword': TransformHandler.extre_Dict['tType'][e_index]}
        if TransformHandler.extre_Dict['ml'][e_index] != 'null':
            ext_type['measureLevel'] = TransformHandler.extre_Dict['ml'][e_index]

        return ext_type


    # [X] Generate type for a subset of a concept. only change id, while keywords and type remain the same.
    def new_type(self, curid):
        newtype = {}

        if type(curid) == list:
            curid = curid[-1]

        if type(curid) == str:
            newtype_index = [i for i, j in enumerate(self.coreConTrans['types']) if j['id'] == curid][
                0]  # find index for the subset transcross_condi['after']
            newtype = self.coreConTrans['types'][newtype_index].copy()  # copy type for the subset
            newtype['id'] = str(self.core_id)  # update id for the subset
        else:
            print("Error: input is not a string in self.new_type()")

        return newtype


    # [X] Generate type for a generated amount that transformed from a object, event, field, support, extent into amount.
    # c_coreC: concept name, can be object, event, field, support
    def newAmount_type(self, c_coreC, keywd):
        newAmoutType = {}

        if c_coreC == 'object' or c_coreC == 'event':
            newAmoutType = {'type': 'amount', 'id': str(self.core_id), 'keyword': keywd if keywd!= None else '', 'measureLevel': 'era_'}
        elif c_coreC == 'field' or c_coreC == 'region' or c_coreC == 'boolfield' or c_coreC == 'support' or c_coreC == 'extent':
            newAmoutType = {'type': 'covamount', 'id': str(self.core_id), 'keyword': keywd if keywd!= None else '', 'measureLevel': 'era_'}
        elif c_coreC == 'networkquality':
            newAmoutType = {'type': 'objectquality', 'id': str(self.core_id), 'keyword': keywd if keywd!= None else '', 'measureLevel': 'rat_'}
        elif c_coreC == 'network':
            newAmoutType = {'type': 'object', 'id': str(self.core_id), 'keyword': keywd if keywd!= None else ''}
        elif c_coreC == 'visibility':
            newAmoutType = {'type': 'field', 'id': str(self.core_id), 'keyword': keywd if keywd != None else '', 'measureLevel': 'nom_'}
        elif c_coreC == 'distance':
            newAmoutType = {'type': 'networkquality', 'id': str(self.core_id), 'keyword': keywd if keywd != None else '',
                            'measureLevel': 'rat_'}

        return newAmoutType


    # [X] Generate transformations
    # cur_input: list
    # cur_output: list
    # cur_key: string or None
    def gen_trans(self, cur_input, cur_output, cur_key):
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
            print("Error: input or output is not a list in self.gen_trans(). {}".format(cur_input))

        if type(cur_key) == str:
            cur_trans['key'] = cur_key
        elif cur_key == None:
            pass
        else:
            print("Error: key is not a string in self.gen_trans(). {}".format(cur_key))

        return cur_trans


    # [X] Add new types in coreConTrans
    def update_coreType(self, cur_type):
        if type(cur_type) == dict:
            self.coreConTrans.setdefault('types', []).append(cur_type)
        elif type(cur_type) == list:
            self.coreConTrans.setdefault('types', []).extend(cur_type)

        # [SC][TODO] why is there a return?
        return self.coreConTrans


    # [X] Add new transformations in coreConTrans
    def update_coreTrans(self, cur_tran):
        if type(cur_tran) == dict:
            self.coreConTrans.setdefault('transformations', []).append(cur_tran)
        elif type(cur_tran) == list:
            self.coreConTrans.setdefault('transformations', []).extend(cur_tran)
        # [SC][TODO] why is there a return?
        return self.coreConTrans


    # update next_TypeDict['id'] for next trans inside comR_trans() and extR_trans()
    def update_nextid(self, nextTypeDict):
        if 'pro' in nextTypeDict['text'][-1] and len(nextTypeDict['text']) == 2 and not self.mea1is:
            nextTypeDict['tag'].insert(0, 'coreC')
            nextTypeDict['text'].insert(0, nextTypeDict['text'][0])
            nextTypeDict['id'].insert(0, str(self.core_id))
        else:
            nextTypeDict['id'][0] = str(self.core_id)

        return nextTypeDict


    # [X] Update core_id
    def update_id(self):
        self.core_id += 1

        return self.core_id


    # remove id of distfield and boolfield
    def remove_boolid(self, conTypeDict):
        dist_index = [i for i in range(0, len(self.coreConTrans['types'])) if self.coreConTrans['types'][i]['type'] == 'distfield'][0]
        # bool_index = [i for i in range(0, len(coreConTrans['types'])) if coreConTrans['types'][i]['type'] == 'boolfield'][0]

        del self.coreConTrans['types'][dist_index]
        del self.coreConTrans['types'][dist_index]


    def merge_aggConAmount(self, mergeTypeDict):
        c_index = None

        a_index = [i for i in range(0, len(self.coreConTrans['types'])) if self.coreConTrans['types'][i]['id'] == mergeTypeDict['id'][-1]][0]
        a_keywd = self.coreConTrans['types'][a_index]['keyword']

        if mergeTypeDict['tag'] == ['coreC', 'aggre'] and a_keywd == 'total':
            c_index = [i for i in range(0, len(self.coreConTrans['types'])) if self.coreConTrans['types'][i]['id'] == mergeTypeDict['id'][0]][0]
        elif mergeTypeDict['tag'] == ['coreC', 'coreC', 'aggre'] and a_keywd == 'total':
            c_index = [i for i in range(0, len(self.coreConTrans['types'])) if self.coreConTrans['types'][i]['id'] == mergeTypeDict['id'][1]][0]

        if c_index != None:
            self.coreConTrans['types'][c_index]['keyword'] = a_keywd + ' ' + self.coreConTrans['types'][c_index]['keyword']
            self.coreConTrans['types'].pop(a_index)
            mergeTypeDict['tag'].pop()
            mergeTypeDict['text'].pop()
            mergeTypeDict['id'].pop()

        return mergeTypeDict


    # [X] Generate transformation for comparison condition and sub-condition
    # allTypeDict: coreTypeDict, include functional roles and their types
    # index of current functional role in coreTypeDict['funcRole']
    # index of the next functional role (which involve in transformations sometimes)
    def comR_trans(self, c_index, n_index):
        cur_TypeDict = self.coreTypeDict['types'][c_index]
        next_TypeDict = self.coreTypeDict['types'][n_index]

        re_comp = cur_TypeDict.copy()
        re_comp['text'] = [t for i, t in enumerate(re_comp['text']) if re_comp['tag'][i] != 'compareR']
        re_comp['tag'] = list(filter(lambda x: x != 'compareR', re_comp['tag']))

        if len(re_comp['tag']) == 0:  # {'tag': ['compareR', 'compareR'], 'text': ['older than', 'younger than']}
            if all(ct in TransformHandler.extre_Dict['keyword'] for ct in cur_TypeDict['text']):
                # quality/pro/amount + next_TypeDict['id'][0] -> new next_TypeDict['id'][0]
                # self.core_id is the id of the concept describing compareR. next_TypeDict['id'][0] is a list when it is origin or destination
                input0 = [next_TypeDict['id'][0] if type(next_TypeDict['id'][0]) != list else next_TypeDict['id'][0][-1], str(self.core_id)]
                self.update_coreType(self.addext_type(cur_TypeDict['text'][0]))  # update the type describing compareR
                self.update_id()  # update self.core_id for output
                trans_c0 = self.gen_trans(input0, [str(self.core_id)], None)
                self.update_coreTrans(trans_c0)
                self.update_coreType(self.new_type(next_TypeDict['id'][0] if type(next_TypeDict['id'][0]) != list else next_TypeDict['id'][0][-1]))
                # update next_TypeDict['id'] for next trans
                next_TypeDict = self.update_nextid(next_TypeDict)
                # update self.core_id += 1 for next trans
                self.update_id()
        elif (re_comp['tag'][-1] == 'coreC' and 'pro' not in re_comp['text'][-1]) or ('pro' in re_comp['text'][-1] and len(re_comp['tag']) == 1) or re_comp['tag'][-1] == 'conAmount':
            # generate transformations before compareR, e.g., ['coreC','conAmount', compareR]
            if re_comp['tag'][-1] == 'conAmount':
                self.update_coreTrans(self.conAmount_trans(c_index, re_comp))
            elif len(re_comp['tag']) > 1:
                self.update_coreTrans(self.write_trans_within(re_comp))
            # cur_TypeDict = {'tag':['compareR', 'compareR', 'coreC'], 'text':['lower than', 'higher than', 'field 0 rat_'],  'id': ['0']}
            if 'field' in re_comp['text'][-1]:  # field -> new field
                trans_field = self.gen_trans([re_comp['id'][-1]], [str(self.core_id)],
                                        None)  # generate the transformation to update field
                self.update_coreTrans(trans_field)  # add trans
                self.update_coreType(self.new_type(re_comp['id'][-1]))  # add type
                # update id representing the new field for next step
                cur_TypeDict['id'][-1] = str(self.core_id)
                self.update_id()
                # field * next input -> new new input
                self.update_coreTrans(self.gen_trans([cur_TypeDict['id'][-1], next_TypeDict['id'][0]], [str(self.core_id)], None))
                self.update_coreType(self.new_type(next_TypeDict['id'][0]))
                next_TypeDict = self.update_nextid(next_TypeDict)
                self.update_id()
            # quality/pro/amount + next_TypeDict['id'][0] -> new next_TypeDict['id'][0]
            else:
                input_qua = [next_TypeDict['id'][0], cur_TypeDict['id'][-1]]
                trans_qua = self.gen_trans(input_qua, [str(self.core_id)], None)
                self.update_coreTrans(trans_qua)
                self.update_coreType(self.new_type(next_TypeDict['id'][0]))
                # update next_TypeDict['id'] for next step
                next_TypeDict = self.update_nextid(next_TypeDict)
            # update self.core_id += 1 for next trans
            self.update_id()
        elif re_comp['tag'][-1] == 'aggre':
            # aggre trans
            self.aggre_trans(c_index, re_comp)
            # compareR trans
            input_agg = [next_TypeDict['id'][0], re_comp['id'][-1]]
            trans_comagg = self.gen_trans(input_agg, [str(self.core_id)], None)
            self.update_coreTrans(trans_comagg)
            self.update_coreType(self.new_type(next_TypeDict['id'][0]))
            # update next_TypeDict['id'] for next step
            next_TypeDict = self.update_nextid(next_TypeDict)
            self.update_id()
        elif 'boolfield' in re_comp['tag']:
            trans_bool = self.write_trans_within(re_comp)
            self.update_coreTrans(trans_bool)
            if 'region' in next_TypeDict['text'][0]:
                self.update_coreTrans(self.gen_trans([cur_TypeDict['id'][-1]], [next_TypeDict['id'][0]], None))


    # [X] Generate transformation for extremaR condition, sub-condition and measure
    # allTypeDict: coreTypeDict, include functional roles and their types
    # index of current functional role in coreTypeDict['funcRole']
    # index of the measure functional role (which involve in transformations sometimes)
    def extR_trans(self, c_index, n_index):
        cur_TypeDict = self.coreTypeDict['types'][c_index]
        next_TypeDict = self.coreTypeDict['types'][n_index]

        re_ext = cur_TypeDict.copy()
        if cur_TypeDict['text'][cur_TypeDict['tag'].index('extremaR')] != 'closest to':
            re_ext['text'] = [t for i, t in enumerate(re_ext['text']) if re_ext['tag'][i] != 'extremaR']
            re_ext['tag'] = list(filter(lambda x: x != 'extremaR', re_ext['tag']))


        if len(re_ext['tag']) == 0:  # {'tag': ['extremaR'], 'text': ['biggest']}
            if all(ct in TransformHandler.extre_Dict['keyword'] for ct in cur_TypeDict['text']):
                extK_index = TransformHandler.extre_Dict['keyword'].index(cur_TypeDict['text'][0])
                if TransformHandler.extre_Dict['cctag'][extK_index] == 'covamount':
                    # next_TypeDict['id'][0] -> covamount, e.g., park -> area
                    trans_e = self.gen_trans([next_TypeDict['id'][0]], [str(self.core_id)],
                                        None)  # self.core_id is the id of the concept describing extremaR
                    self.update_coreTrans(trans_e)
                    self.update_coreType(self.addext_type(cur_TypeDict['text'][0]))  # update the type describing extremaR
                else:
                    self.update_coreType(self.addext_type(cur_TypeDict['text'][0]))
                # extremaR + next_TypeDict['id'][0] -> new next_TypeDict['id'][0]
                input0 = [next_TypeDict['id'][0], str(self.core_id)]
                self.update_id()  # update self.core_id for output
                trans0 = self.gen_trans(input0, [str(self.core_id)], None)
                self.update_coreTrans(trans0)
                self.update_coreType(self.new_type(next_TypeDict['id'][0]))
                # update next_TypeDict['id'] for next trans
                next_TypeDict = self.update_nextid(next_TypeDict)
                # update self.core_id += 1 for next trans
                self.update_id()
        elif re_ext['tag'] == ['coreC']:
            # cur_TypeDict = {'tag':['coreC', 'extremaR'], 'text':['eveconobjconpro 0 ira_', 'highest'],  'id': ['0']}
            if 'field' in re_ext['text'][0]:  # field -> new field
                trans_field = self.gen_trans(cur_TypeDict['id'], [str(self.core_id)],
                                        None)  # generate the transformation to update field
                self.update_coreTrans(trans_field)  # add trans
                self.update_coreType(self.new_type(cur_TypeDict['id'][0]))  # add type
                # update id representing the new field for next step
                cur_TypeDict['id'][0] = str(self.core_id)
            # quality/pro/amount + next_TypeDict['id'][0] -> new next_TypeDict['id'][0]
            else:
                input_qua = [next_TypeDict['id'][0], cur_TypeDict['id'][0]]
                trans_qua = self.gen_trans(input_qua, [str(self.core_id)], None)
                self.update_coreTrans(trans_qua)
                self.update_coreType(self.new_type(next_TypeDict['id'][0]))
                # update next_TypeDict['id'] for next step
                next_TypeDict = self.update_nextid(next_TypeDict)
            # update self.core_id += 1 for next trans
            self.update_id()
        elif re_ext['tag'][-1] == 'aggre':
            self.aggre_trans(c_index, re_ext)
            input_extagg = [next_TypeDict['id'][0], re_ext['id'][-1]]
            trans_extagg = self.gen_trans(input_extagg, [str(self.core_id)], None)
            self.update_coreTrans(trans_extagg)
            self.update_coreType(self.new_type(next_TypeDict['id'][0]))
            # update next_TypeDict['id'] for next step
            next_TypeDict = self.update_nextid(next_TypeDict)
            self.update_id()
        elif len(re_ext['tag']) > 1 and 'pro' in re_ext['text'][-1]:
            # proportion trans
            self.pro_trans(c_index, re_ext)
            # extremaR trans
            self.update_coreTrans(self.gen_trans([re_ext['id'][-1], next_TypeDict['id'][0]], [str(self.core_id)], None))
            self.update_coreType(self.new_type(next_TypeDict['id'][0]))
            self.update_id()
        elif 'boolfield' in re_ext['tag']:
            trans_bool = self.write_trans_within(re_ext)
            self.update_coreTrans(trans_bool)
            self.update_coreTrans(self.gen_trans([next_TypeDict['id'][0], re_ext['id'][-1]], [str(self.core_id)], None))
            self.update_coreType(self.new_type(next_TypeDict['id'][0]))
            next_TypeDict['id'][0] = str(self.core_id)
            self.update_id()


    # [X] Generate transformation for aggre in condition, sub-condition and measure
    # allTypeDict: coreTypeDict, include functional roles and their types
    # index of current functional role in coreTypeDict['funcRole']
    # TypeDict that includes concepts for generating aggregation transformations
    def aggre_trans(self, c_index, aggTypeDict):
        frole = self.coreTypeDict['funcRole'][c_index]

        if aggTypeDict['tag'] == ['coreC', 'aggre'] or aggTypeDict['tag'] == ['coreC', 'coreC'] :
            if frole == 'condition':
                c_mTypeDict = self.coreTypeDict['types'][self.meais[0]]
                c_input = [aggTypeDict['id'][0], c_mTypeDict['id'][0]]
                trans_agg = self.gen_trans(c_input, [aggTypeDict['id'][-1]], c_mTypeDict['id'][0])
                self.update_coreTrans(trans_agg)
            elif frole == 'measure':
                if self.supis and not self.con_meais:
                    c_supTypeDict = self.coreTypeDict['types'][self.supis[0]]
                    c_input = [aggTypeDict['id'][0], c_supTypeDict['id'][0]]
                    trans_agg = self.gen_trans(c_input, [aggTypeDict['id'][-1]], c_supTypeDict['id'][0])
                    self.update_coreTrans(trans_agg)
                elif not self.supis and not self.con_meais:
                    extent_index = self.coreTypeDict['funcRole'].index('extent')
                    c_input = [aggTypeDict['id'][0], self.coreTypeDict['types'][extent_index][0]]
                    trans_agg = self.gen_trans(c_input, [aggTypeDict['id'][-1]], self.coreTypeDict['types'][extent_index][0])
                    self.update_coreTrans(trans_agg)
        elif aggTypeDict['tag'] == ['coreC', 'coreC', 'aggre']:
            if frole == 'measure':
                if self.supis and not self.con_meais:
                    c_supTypeDict = self.coreTypeDict['types'][self.supis[0]]
                    self.update_coreTrans(self.gen_trans([aggTypeDict['id'][0]], [aggTypeDict['id'][1]], None))
                    # aggre trans
                    self.update_coreTrans(self.gen_trans([aggTypeDict['id'][1]], [aggTypeDict['id'][-1]], c_supTypeDict['id'][-1]))
                elif not self.supis and not self.con_meais:
                    agg_extent_id = self.coreTypeDict['types'][self.coreTypeDict['funcRole'].index('extent')][0]
                    self.update_coreTrans(self.gen_trans([aggTypeDict['id'][0]], [aggTypeDict['id'][1]], None))
                    # aggre trans
                    self.update_coreTrans(self.gen_trans([aggTypeDict['id'][1], agg_extent_id], [aggTypeDict['id'][-1]], agg_extent_id))
                elif not self.supis and self.con_meais:  # What is the average housing price of neighborhoods within 100 meters from a school in Utrecht, the Netherlands
                    agg_extent_id = self.coreTypeDict['types'][self.coreTypeDict['funcRole'].index('extent')][0]
                    self.update_coreTrans(self.gen_trans([aggTypeDict['id'][0]], [aggTypeDict['id'][1]], None))
                    # aggre trans
                    self.update_coreTrans(self.gen_trans([aggTypeDict['id'][1]], [aggTypeDict['id'][-1]], agg_extent_id))
        elif aggTypeDict['tag'] == ['destination', 'origin', 'networkQ', 'aggre']:
            if frole == 'measure':
                bef_aggTypeDict = {key: value[0: i] for key, value in aggTypeDict.items() for i in range(len(value)) if aggTypeDict['tag'][i] == 'aggre'}
                aTypeDict = {key: value[i-1:] for key, value in aggTypeDict.items() for i in range(len(value)) if aggTypeDict['tag'][i] == 'aggre'}
                # network trans
                self.update_coreTrans(self.write_trans_within(bef_aggTypeDict))
                # aggre trans
                if self.supis and not self.con_meais:
                    c_supTypeDict = self.coreTypeDict['types'][self.supis[0]]
                    self.update_coreTrans(self.gen_trans([aTypeDict['id'][0], c_supTypeDict['id'][-1]], [aTypeDict['id'][1]], c_supTypeDict['id'][-1]))
                elif not self.supis and not self.con_meais:
                    agg_extent_id = self.coreTypeDict['types'][self.coreTypeDict['funcRole'].index('extent')][0]
                    self.update_coreTrans(self.gen_trans([aTypeDict['id'][0]], [aTypeDict['id'][1]], agg_extent_id))
        elif aggTypeDict['tag'] == ['destination', 'origin', 'extremaR', 'networkQ', 'aggre']:
            if frole == 'measure':
                bef_aggTypeDict = {key: value[0: i] for key, value in aggTypeDict.items() for i in range(len(value)) if aggTypeDict['tag'][i] == 'aggre'}
                aTypeDict = {key: value[i-1:] for key, value in aggTypeDict.items() for i in range(len(value)) if aggTypeDict['tag'][i] == 'aggre'}
                bef_aggTypeDict['id'] = aggTypeDict['id'][0:3]
                aTypeDict['id'] = aggTypeDict['id'][-2:4]
                # network trans
                self.update_coreTrans(self.write_trans_within(bef_aggTypeDict))
                # aggre trans
                if self.supis and not self.con_meais:
                    c_supTypeDict = self.coreTypeDict['types'][self.supis[0]]
                    self.update_coreTrans(self.gen_trans([str(self.core_id-1), c_supTypeDict['id'][-1]], [aTypeDict['id'][1]],
                                               c_supTypeDict['id'][-1]))
                elif not self.supis and not self.con_meais:
                    agg_extent_id = self.coreTypeDict['types'][self.coreTypeDict['funcRole'].index('extent')][0]
                    self.update_coreTrans(self.gen_trans([str(self.core_id-1)], [aTypeDict['id'][1]], agg_extent_id))


    # [X] Generate transformation for proportion in condition and measure
    # allTypeDict: coreTypeDict, include functional roles and their types
    # index of current functional role in coreTypeDict['funcRole']
    # TypeDict that includes concepts for generating proportion transformations
    def pro_trans(self, c_index, proTypeDict):
        # seperate proTypeDict into two dictionary: one includes concepts for aggre transformation, another one includes aggre as input and other concepts for proportion transformation
        if 'aggre' in proTypeDict['tag']:
            aTypeDict = {key: value[0: i + 1] for key, value in proTypeDict.items() for i in range(len(value)) if
                         proTypeDict['tag'][i] == 'aggre'}
            afte_aTypeDict = {key: value[i:] for key, value in proTypeDict.items() for i in range(len(value)) if
                              proTypeDict['tag'][i] == 'aggre'}
            if aTypeDict['tag'] == ['coreC', 'coreC', 'aggre'] and 'amount' in aTypeDict['text'][1]:
                aTypeDict = self.merge_aggConAmount(aTypeDict)
                afte_aTypeDict['tag'][0] = 'coreC'
                afte_aTypeDict['text'][0] = aTypeDict['text'][-1]
                afte_aTypeDict['id'][0] = aTypeDict['id'][-1]
            self.aggre_trans(c_index, aTypeDict)
        else:
            afte_aTypeDict = proTypeDict.copy()

        frole = self.coreTypeDict['funcRole'][c_index]

        if afte_aTypeDict['tag'] == ['coreC']:
            if frole == 'measure':
                if self.supis and not self.con_meais:
                    m_supTypeDict = self.coreTypeDict['types'][self.supis[0]]
                    self.update_coreTrans(self.gen_trans([m_supTypeDict['id'][-1], afte_aTypeDict['id'][0]], [str(self.core_id)], m_supTypeDict['id'][-1]))
                    self.update_coreType(self.new_type(afte_aTypeDict['id'][0]))
                    self.update_id()
                elif self.con_meais and not self.supis: # What is the crime density within the buffer area of the shortest path from home to workplace in Amsterdam
                    for ci in self.con_meais:
                        m_ciTypeDict = self.coreTypeDict['types'][ci]
                        if 'distfield' in m_ciTypeDict['tag']:
                            dist_index = m_ciTypeDict['tag'].index('distfield')
                            if m_ciTypeDict['tag'][dist_index-1] == 'networkC':
                                self.update_coreTrans(self.gen_trans([m_ciTypeDict['id'][-1], afte_aTypeDict['id'][0]], [str(self.core_id)], str(self.core_id-1)))
                            else:
                                self.update_coreTrans(self.gen_trans([m_ciTypeDict['id'][-1], afte_aTypeDict['id'][0]], [str(self.core_id)], m_ciTypeDict['id'][dist_index]))
                            self.update_coreType(self.new_type(afte_aTypeDict['id'][0]))
                            self.update_id()
                        else:
                            self.update_coreTrans(self.gen_trans([m_ciTypeDict['id'][-1], afte_aTypeDict['id'][0]], [str(self.core_id)],
                                                   m_ciTypeDict['id'][-1]))
                            self.update_coreType(self.new_type(afte_aTypeDict['id'][0]))
                            self.update_id()
                elif self.supis and self.con_meais:
                    m_supTypeDict = self.coreTypeDict['types'][self.supis[0]]
                    for ci in self.con_meais:
                        m_ciTypeDict = self.coreTypeDict['types'][ci]
                        if 'field' in m_ciTypeDict['text'][-1] or 'boolfield' in m_ciTypeDict['text'][-1] or len(m_ciTypeDict['id']) == 1:
                            self.update_coreTrans(self.gen_trans([m_ciTypeDict['id'][-1], afte_aTypeDict['id'][0]], [str(self.core_id)],
                                                   m_ciTypeDict['id'][-1] if 'distfield' not in  m_ciTypeDict['tag'] else m_ciTypeDict['id'][m_ciTypeDict['tag'].index('distfield')]))
                            self.update_coreType(self.new_type(afte_aTypeDict['id'][0]))
                            afte_aTypeDict = self.update_nextid(afte_aTypeDict)
                            self.update_id()
                    self.update_coreTrans(self.gen_trans([afte_aTypeDict['id'][0], m_supTypeDict['id'][-1]], [str(self.core_id)], m_supTypeDict['id'][-1]))
                    self.update_coreType(self.new_type(afte_aTypeDict['id'][0]))
                    self.update_id()
        elif afte_aTypeDict['tag'] == ['coreC', 'coreC']:
            if frole == 'measure':
                if self.supis and not self.con_meais:
                    m_supTypeDict = self.coreTypeDict['types'][self.supis[0]]
                    if 'amount' in afte_aTypeDict['text'][0]:  # amount * support -> new amount
                        self.update_coreTrans(self.gen_trans([afte_aTypeDict['id'][0], m_supTypeDict['id'][-1]], [str(self.core_id)], m_supTypeDict['id'][-1]))
                        self.update_coreType(self.new_type(afte_aTypeDict['id'][0]))
                    else:  # object/event * support -> object amount, field * support -> covamount
                        self.update_coreTrans(self.gen_trans([afte_aTypeDict['id'][0], m_supTypeDict['id'][-1]], [str(self.core_id)],
                                                   m_supTypeDict['id'][-1]))
                        self.update_coreType(self.newAmount_type(afte_aTypeDict['text'][0].split()[0], None))
                    # update id for new amount
                    afte_aTypeDict['id'][0] = str(self.core_id)
                    self.update_id()
                    # support -> support covAmount
                    self.update_coreTrans(self.gen_trans([m_supTypeDict['id'][-1]], [str(self.core_id)], None))
                    self.update_coreType(self.newAmount_type('support', None))
                    # amount * support covAmount -> pro
                    self.update_coreTrans(self.gen_trans([afte_aTypeDict['id'][0], str(self.core_id)], [afte_aTypeDict['id'][-1]], m_supTypeDict['id'][-1]))
                    self.update_id()
                elif self.con_meais:
                    for ci in self.con_meais:
                        m_ciTypeDict = self.coreTypeDict['types'][ci]
                        if 'amount' in afte_aTypeDict['text'][0]:
                            # amount * condition -> new amount, distfield is key
                            if 'distfield' in m_ciTypeDict['tag']:
                                dist_index = m_ciTypeDict['tag'].index('distfield')
                                self.update_coreTrans(self.gen_trans([afte_aTypeDict['id'][0], m_ciTypeDict['id'][-1]], [str(self.core_id)],
                                                       m_ciTypeDict['id'][dist_index]))
                            else:
                                self.update_coreTrans(self.gen_trans([afte_aTypeDict['id'][0], m_ciTypeDict['id'][-1]], [str(self.core_id)], m_ciTypeDict['id'][-1]))
                            # update new type and id
                            self.update_coreType(self.new_type(afte_aTypeDict['id'][0]))
                            self.update_id()
                            # condition and support
                            if self.supis:
                                m_supTypeDict = self.coreTypeDict['types'][self.supis[0]]
                                # new amount * support -> new amount2 per support
                                self.update_coreTrans(self.gen_trans([str(self.core_id-1), m_supTypeDict['id'][-1]], [str(self.core_id)], m_supTypeDict['id'][-1]))
                                self.update_coreType(self.new_type(str(self.core_id-1)))
                                self.update_id()
                                # denominator
                                if [i['keyword'] for i in self.coreConTrans['types'] if i['id'] == afte_aTypeDict['id'][-1]] == ['density']:
                                    self.update_coreTrans(self.gen_trans([m_supTypeDict['id'][-1]], [str(self.core_id)], None))
                                    self.update_coreType(self.newAmount_type('support', None))
                                else:
                                    self.update_coreTrans(self.gen_trans([afte_aTypeDict['id'][0], m_supTypeDict['id'][-1]], [str(self.core_id)], m_supTypeDict['id'][-1]))
                                    self.update_coreType(self.new_type(afte_aTypeDict['id'][0]))
                                # new amount2 * denominator -> density/pro
                                self.update_coreTrans(self.gen_trans([str(self.core_id-1), str(self.core_id)], [afte_aTypeDict['id'][-1]], m_supTypeDict['id'][-1]))
                                self.update_id()
                            # condition and no support
                            else:
                                pro_extent_id = self.coreTypeDict['types'][self.coreTypeDict['funcRole'].index('extent')][0]
                                if [i['keyword'] for i in self.coreConTrans['types'] if i['id'] == afte_aTypeDict['id'][-1]] == ['density']:
                                    # extent -> covAmount
                                    self.update_coreTrans(self.gen_trans([pro_extent_id], [str(self.core_id)], None))
                                    self.update_coreType(self.newAmount_type('extent', None))
                                    # pro
                                    self.update_coreTrans(self.gen_trans([str(self.core_id-1), str(self.core_id)], [afte_aTypeDict['id'][-1]], pro_extent_id))
                                    self.update_id()
                                else:
                                    # pro
                                    self.update_coreTrans(self.gen_trans([str(self.core_id-1), afte_aTypeDict['id'][0]], [afte_aTypeDict['id'][-1]], pro_extent_id))
                        else:
                            if self.supis:
                                m_supTypeDict = self.coreTypeDict['types'][self.supis[0]]
                                # new field/object/event * support-> (cov)amount
                                keywd0 = afte_aTypeDict['text'][0].split()[0]
                                self.update_coreTrans(self.gen_trans([self.coreConTrans['transformations'][-1]['after'][0], m_supTypeDict['id'][-1]], [str(self.core_id)], m_supTypeDict['id'][-1]))
                                self.update_coreType(self.newAmount_type(keywd0, None))
                                self.update_id()
                                # denominator
                                if [i['keyword'] for i in self.coreConTrans['types'] if i['id'] == afte_aTypeDict['id'][-1]] == ['density'] or keywd0 == 'field' or keywd0 == 'region':
                                    self.update_coreTrans(self.gen_trans([m_supTypeDict['id'][-1]], [str(self.core_id)], None))
                                    self.update_coreType(self.newAmount_type('support', None))
                                else:
                                    self.update_coreTrans(self.gen_trans([afte_aTypeDict['id'][0], m_supTypeDict['id'][-1]], [str(self.core_id)],
                                                  m_supTypeDict['id'][-1]))
                                    self.update_coreType(self.newAmount_type(afte_aTypeDict['text'][0].split()[0], None))
                                # new amount * denominator -> density/pro
                                self.update_coreTrans(self.gen_trans([str(self.core_id - 1), str(self.core_id)], [afte_aTypeDict['id'][-1]], m_supTypeDict['id'][-1]))
                                self.update_id()
                            else:
                                pro_extent_id = self.coreTypeDict['types'][self.coreTypeDict['funcRole'].index('extent')][0]
                                # new field/object/event -> (cov)Amount
                                keywd0 = afte_aTypeDict['text'][0].split()[0]
                                if keywd0 != 'field' or keywd0 != 'region':
                                    self.update_coreTrans(self.gen_trans(self.coreConTrans['transformations'][-1]['after'], [str(self.core_id)], None))
                                else:
                                    self.update_coreTrans(self.gen_trans(self.coreConTrans['transformations'][-1]['after'], [str(self.core_id)], pro_extent_id))
                                self.update_coreType(self.newAmount_type(keywd0, None))
                                self.update_id()
                                # dominator
                                if [i['keyword'] for i in self.coreConTrans['types'] if i['id'] == afte_aTypeDict['id'][-1]] == ['density'] or keywd0 == 'field' or keywd0 == 'region':
                                    if 'distfield' in m_ciTypeDict['tag']:
                                        self.update_coreTrans(self.gen_trans([m_ciTypeDict['id'][-1]], [str(self.core_id)], None))
                                        self.update_coreType(self.newAmount_type('boolfield', None))
                                    else:
                                        # extent -> covAmount
                                        self.update_coreTrans(self.gen_trans([pro_extent_id], [str(self.core_id)], None))
                                        self.update_coreType(self.newAmount_type('extent', None))
                                    # pro
                                    self.update_coreTrans(self.gen_trans([str(self.core_id-1), str(self.core_id)], [afte_aTypeDict['id'][-1]], pro_extent_id))
                                    self.update_id()
                                else:
                                    # pro
                                    self.update_coreTrans(self.gen_trans([str(self.core_id-1), afte_aTypeDict['id'][0]], [afte_aTypeDict['id'][-1]], pro_extent_id))
                elif not self.supis and not self.con_meais:
                    pro_extent_id = self.coreTypeDict['types'][self.coreTypeDict['funcRole'].index('extent')][0]
                    # field/object/event -> (cov)Amount
                    keywd0 = afte_aTypeDict['text'][0].split()[0]
                    self.update_coreTrans(self.gen_trans([afte_aTypeDict['id'][0]], [str(self.core_id)], pro_extent_id if keywd0 != 'field' else None))
                    self.update_coreType(self.newAmount_type(keywd0, None))
                    self.update_id()
                    # extent -> covAmount
                    self.update_coreTrans(self.gen_trans([pro_extent_id], [str(self.core_id)], None))
                    self.update_coreType(self.newAmount_type('extent', None))
                    # pro
                    self.update_coreTrans(self.gen_trans([str(self.core_id-1), str(self.core_id)], [afte_aTypeDict['id'][-1]], pro_extent_id))
                    self.update_id()
        elif afte_aTypeDict['tag'] == ['coreC', 'coreC', 'coreC']:
            if self.supis and self.con_meais:
                m_supTypeDict = self.coreTypeDict['types'][self.supis[0]]
                for ci in self.con_meais:
                    m_ciTypeDict = self.coreTypeDict['types'][ci]
                    if 'amount' in afte_aTypeDict['text'][0]:
                        # 'What is the percentage of population older than 65 for each Census Consolidated Subdivision in Alberta in Canada'
                        if m_ciTypeDict['id'] == []:
                            # input * support -> new input
                            self.update_coreTrans(self.gen_trans([afte_aTypeDict['id'][0], m_supTypeDict['id'][-1]], [str(self.core_id)], m_supTypeDict['id'][-1]))
                            self.update_coreType(self.new_type(afte_aTypeDict['id'][0]))
                            self.update_id()
                            self.update_coreTrans(self.gen_trans([afte_aTypeDict['id'][1], m_supTypeDict['id'][-1]], [str(self.core_id)],m_supTypeDict['id'][-1]))
                            self.update_coreType(self.new_type(afte_aTypeDict['id'][1]))
                            # pro
                            self.update_coreTrans(self.gen_trans([str(self.core_id-1), str(self.core_id)], [afte_aTypeDict['id'][-1]], m_supTypeDict['id'][-1]))
                            self.update_id()
            elif self.supis and not self.con_meais:
                m_supTypeDict = self.coreTypeDict['types'][self.supis[0]]
                # coreC * support -> coreC or amount
                self.update_coreTrans(self.gen_trans([afte_aTypeDict['id'][1], m_supTypeDict['id'][-1]], [str(self.core_id)], m_supTypeDict['id'][-1]))
                # pro
                self.update_coreTrans(self.gen_trans([str(self.core_id), afte_aTypeDict['id'][0]], [afte_aTypeDict['id'][-1]], m_supTypeDict['id'][-1]))
                if 'amount' in afte_aTypeDict['text'][1]:
                    self.update_coreType(self.new_type(afte_aTypeDict['id'][1]))
                else:
                    self.update_coreType(self.newAmount_type(afte_aTypeDict['text'][1].split()[0], None))
                self.update_id()
            elif not self.supis and not self.con_meais:
                pro_extent_id = self.coreTypeDict['types'][self.coreTypeDict['funcRole'].index('extent')][0]
                if 'amount' not in afte_aTypeDict['text'][1]:
                    self.update_coreTrans(self.gen_trans([afte_aTypeDict['id'][1], pro_extent_id], [str(self.core_id)], pro_extent_id))
                    self.update_coreType(self.newAmount_type(afte_aTypeDict['text'][1].split()[0], None))
                    afte_aTypeDict['id'][1] = str(self.core_id)
                    self.update_id()
                self.update_coreTrans(self.gen_trans(afte_aTypeDict['id'][0:2], [afte_aTypeDict['id'][-1]], pro_extent_id))
        elif afte_aTypeDict['tag'] == ['aggre', 'coreC', 'coreC']:
            if frole == 'condition':
                # coreC + measure input -> new coreC with measure input as key
                cur_mTypeDict = self.coreTypeDict['types'][self.meais[0]]
                coreC_input = [afte_aTypeDict['id'][1], cur_mTypeDict['id'][0]]
                trans_coreC = self.gen_trans(coreC_input, [str(self.core_id)], cur_mTypeDict['id'][0])
                self.update_coreTrans(trans_coreC)
                # add new amount type
                new_amou = afte_aTypeDict['text'][1].split()[0]
                if new_amou in ['object', 'field', 'event']:
                    self.update_coreType(self.newAmount_type(new_amou, None))
                else:
                    self.update_coreType(self.new_type(afte_aTypeDict['id'][1]))
                # update coreC ID for next step
                afte_aTypeDict['id'][1] = str(self.core_id)
                self.update_id()
                # proportion trans
                self.update_coreTrans(
                    self.gen_trans(afte_aTypeDict['id'][0:2][::-1], [afte_aTypeDict['id'][-1]], cur_mTypeDict['id'][0]))
            if frole == 'measure':
                if self.supis and not self.con_meais:
                    m_supTypeDict = self.coreTypeDict['types'][self.supis[0]]
                    # coreC * support -> coreC or amount
                    self.update_coreTrans(self.gen_trans([afte_aTypeDict['id'][1], m_supTypeDict['id'][-1]], [str(self.core_id)], m_supTypeDict['id'][-1]))
                    # pro
                    self.update_coreTrans(self.gen_trans([str(self.core_id), afte_aTypeDict['id'][0]], [afte_aTypeDict['id'][-1]], m_supTypeDict['id'][-1]))
                    if 'amount' in afte_aTypeDict['text'][1]:
                        self.update_coreType(self.new_type(afte_aTypeDict['id'][1]))
                    else:
                        self.update_coreType(self.newAmount_type(afte_aTypeDict['text'][1].split()[0], None))
                    self.update_id()


    # [X] Generate transformation for conAmount in condition and measure
    # allTypeDict: coreTypeDict, include functional roles and their types
    # index of current functional role in coreTypeDict['funcRole']
    # TypeDict that includes concepts for generating conAmount transformations
    def conAmount_trans(self, c_index, conATypeDict):
        frole = self.coreTypeDict['funcRole'][c_index]

        # 'tag': ['coreC', 'conAmount']
        if frole == 'condition' or frole == 'subcon':
            nextTypeDict = self.coreTypeDict['types'][c_index+1]
            self.update_coreTrans(self.gen_trans([conATypeDict['id'][0]], [conATypeDict['id'][-1]], nextTypeDict['id'][0]))

        if frole == 'measure':
            if conATypeDict['tag'] == ['coreC']:
                if self.con_meais and not self.supis:
                    conA_extent_id = self.coreTypeDict['types'][self.coreTypeDict['funcRole'].index('extent')][0]
                    for ci in self.con_meais:
                        m_ciTypeDict = self.coreTypeDict['types'][ci]
                        self.update_coreTrans(self.gen_trans([conATypeDict['id'][0], m_ciTypeDict['id'][-1]], [str(self.core_id)],
                                                   conA_extent_id if 'distfield' not in m_ciTypeDict['tag'] else
                                                   m_ciTypeDict['id'][m_ciTypeDict['tag'].index('distfield')]))
                        self.update_coreType(self.new_type(conATypeDict['id'][0]))
                        conATypeDict['id'][0] = str(self.core_id)
                        self.update_id()
                elif self.supis and not self.con_meais:
                    # What is the WOZ-waarde for each neighborhood in Amsterdam
                    m_supTypeDict = self.coreTypeDict['types'][self.supis[0]]
                    self.update_coreTrans(self.gen_trans([conATypeDict['id'][0], m_supTypeDict['id'][-1]], [str(self.core_id)], m_supTypeDict['id'][-1]))
                    self.update_coreType(self.new_type(conATypeDict['id'][0]))
                    self.update_id()
                elif not self.supis and not self.con_meais:
                    conA_extent_id = self.coreTypeDict['types'][self.coreTypeDict['funcRole'].index('extent')][0]
                    self.update_coreTrans(self.gen_trans([conATypeDict['id'][0]], [str(self.core_id)],
                                                         conA_extent_id))
                    self.update_coreType(self.new_type(conATypeDict['id'][0]))
                    self.update_id()
                elif self.con_meais and self.supis:
                    for ci in self.con_meais:
                        m_ciTypeDict = self.coreTypeDict['types'][ci]
                        self.update_coreTrans(self.gen_trans([conATypeDict['id'][0], m_ciTypeDict['id'][-1]], [str(self.core_id)],
                                                   m_ciTypeDict['id'][-1] if 'distfield' not in m_ciTypeDict['tag'] else
                                                   m_ciTypeDict['id'][m_ciTypeDict['tag'].index('distfield')]))
                        self.update_coreType(self.new_type(conATypeDict['id'][0]))
                        conATypeDict['id'][0] = str(self.core_id)
                        self.update_id()
                    m_supTypeDict = self.coreTypeDict['types'][self.supis[0]]
                    self.update_coreTrans(self.gen_trans([conATypeDict['id'][0], m_supTypeDict['id'][-1]], [str(self.core_id)],
                                               m_supTypeDict['id'][-1]))
                    self.update_coreType(self.new_type(conATypeDict['id'][0]))
                    self.update_id()
            elif conATypeDict['tag'] == ['coreC','coreC']:
                if self.con_meais and not self.supis:
                    conA_extent_id = self.coreTypeDict['types'][self.coreTypeDict['funcRole'].index('extent')][0]
                    for ci in self.con_meais:
                        m_ciTypeDict = self.coreTypeDict['types'][ci]
                        if 'distfield' in m_ciTypeDict['id'] or 'serviceobj' in m_ciTypeDict['id']:
                            self.update_coreTrans(self.gen_trans([conATypeDict['id'][0], m_ciTypeDict['id'][-1]], [str(self.core_id)], None))
                            self.update_coreType(self.new_type(conATypeDict['id'][0]))
                            conATypeDict['id'][0] = str(self.core_id)
                            self.update_id()
                    # new input -> conAmount
                    self.update_coreTrans(self.gen_trans([conATypeDict['id'][0]], [conATypeDict['id'][1]], conA_extent_id))
                elif self.supis and not self.con_meais:
                    m_supTypeDict = self.coreTypeDict['types'][self.supis[0]]
                    self.update_coreTrans(self.gen_trans([conATypeDict['id'][0], m_supTypeDict['id'][-1]], [conATypeDict['id'][-1]], m_supTypeDict['id'][-1]))
                elif not self.supis and not self.con_meais:
                    conA_extent_id = self.coreTypeDict['types'][self.coreTypeDict['funcRole'].index('extent')][0]
                    self.update_coreTrans(self.gen_trans([conATypeDict['id'][0]], [conATypeDict['id'][1]], conA_extent_id))


    # [X] Generate core concept transformations within condition, measure...
    # Input TypeDict = {'tag': ['coreC', 'distField', 'boolField'], 'text': ['object 1', 'from', ''], 'id': ['1', '2', '3']}
    # Output [{'before': ['1'], 'after': ['2']}, {'before': ['2'], 'after': ['3']}]
    def write_trans_within(self, TypeDict):
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
                        trans_net['after'] = [str(self.core_id)]
                        transwithin.append(trans_net)
                        # add object in types
                        dist_index = \
                        [i for i, j in enumerate(self.coreConTrans['types']) if j['type'] == 'distfield'][0]
                        self.coreConTrans.setdefault('types', []).append({'type': 'object', 'id': str(self.core_id),
                                                                          'keyword': self.coreConTrans['types'][
                                                                              dist_index - 1][
                                                                              'keyword']})
                        # object -> distField
                        trans = {}
                        trans['before'] = [str(self.core_id)]
                        trans['after'] = [TypeDict['id'][TypeDict['tag'].index(tt)]]
                        transwithin.append(trans)
                        self.update_id()
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
                        if len(TypeDict['id'][
                                   s_in - 3]) == 2:  # [['grid', 'centroid'], 'destination', 'networkC', 'serviceObj'], remove 'roadData'
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
                        trans_service['after'] = [str(self.core_id)]
                        transwithin.append(trans_service)
                        self.update_coreType(self.new_type(trans_service['before'][0]))
                        self.update_id()
                        # network quality -> object
                        trans_ori = {}
                        trans_ori['before'] = [str(self.core_id - 1)]
                        trans_ori['after'] = [str(self.core_id)]
                        transwithin.append(trans_ori)
                        self.update_coreType(self.new_type(TypeDict['id'][s_in - 3][-1]))
                        self.update_id()
                    else:  # ['destination', 'networkQ', 'serviceObj', ...]
                        if len(TypeDict['id'][s_in - 2]) == 2:  # [['grid', 'centroid'], 'networkC', 'serviceObj']
                            trans['before'] = [TypeDict['id'][s_in - 2][0]]
                            trans['after'] = [TypeDict['id'][s_in - 2][1]]
                            transwithin.append(trans)
                        # destination, measure_obj -> driving time
                        trans = {}
                        trans['before'] = [TypeDict['id'][s_in - 2][-1], self.measureType['id'][0]]
                        trans['after'] = [TypeDict['id'][s_in - 1]]
                        transwithin.append(trans)
                        # driving time -> 1 min driving time
                        trans_service = {}
                        trans_service['before'] = [TypeDict['id'][s_in - 1]]
                        trans_service['after'] = [str(self.core_id)]
                        transwithin.append(trans_service)
                        self.update_coreType(self.new_type(trans_service['before'][0]))
                        self.update_id()
                        # network quality -> object
                        trans_des = {}
                        trans_des['before'] = [str(self.core_id - 1)]
                        trans_des['after'] = [str(self.core_id)]
                        transwithin.append(trans_des)
                        self.update_coreType(self.new_type(self.measureType['id'][0]))
                        self.measureType['id'][0] = str(self.core_id)
                        self.update_id()
                elif s_in - 2 >= 0 and TypeDict['tag'][
                    s_in - 2] == 'origin':  # ['origin', 'networkC', 'serviceObj'], remove 'roadData'
                    if len(TypeDict['id'][
                               s_in - 2]) == 2:  # [['grid', 'centroid'], 'networkC', 'serviceObj'], remove 'roadData'
                        trans['before'] = [TypeDict['id'][s_in - 2][0]]
                        trans['after'] = [TypeDict['id'][s_in - 2][1]]
                        transwithin.append(trans)
                    # origin, measure_obj -> driving time
                    trans = {}
                    trans['before'] = [TypeDict['id'][s_in - 2][-1], self.measureType['id'][0]]
                    trans['after'] = [TypeDict['id'][s_in - 1]]
                    transwithin.append(trans)
                    # driving time -> 1 min driving time
                    trans_ser = {}
                    trans_ser['before'] = [TypeDict['id'][s_in - 1]]
                    trans_ser['after'] = [str(self.core_id)]
                    transwithin.append(trans_ser)
                    self.update_coreType(self.new_type(trans_ser['before'][0]))
                    self.update_id()
                    # network quality -> object
                    trans_ori = {}
                    trans_ori['before'] = [str(self.core_id - 1)]
                    trans_ori['after'] = [str(self.core_id)]
                    transwithin.append(trans_ori)
                    self.update_coreType(self.new_type(self.measureType['id'][0]))
                    self.measureType['id'][0] = str(self.core_id)
                    self.update_id()
            elif ((tt == 'networkC' and 'networkQ' not in TypeDict['tag']) or (
                    tt == 'networkQ' and 'networkC' not in TypeDict['tag']) or tt == 'objectQ') and (
                    'destination' in TypeDict['tag'] or 'origin' in TypeDict['tag']) and 'serviceobj' not in \
                    TypeDict[
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
                            trans['after'] = [TypeDict['id'][n_in - 1]]
                        else:
                            trans['after'] = [TypeDict['id'][n_in]]
                        transwithin.append(trans)
                        if 'extremaR' in TypeDict['tag'] and tt == 'networkQ':
                            ex_trans = {}
                            ex_trans['before'] = trans['after']
                            ex_trans['after'] = [str(self.core_id)]
                            ex_trans['key'] = TypeDict['id'][orig_loc][-1]
                            transwithin.append(ex_trans)
                            ex_index = [i for i in range(0, len(self.coreConTrans['types'])) if
                                        self.coreConTrans['types'][i]['id'] == trans['after'][0]][0]
                            self.update_coreType(
                                self.newAmount_type('networkquality', self.coreConTrans['types'][ex_index]['keyword']))
                            self.update_id()
                        elif tt == 'networkC':
                            netC_keywd_in = [i for i in range(0, len(self.coreConTrans['types'])) if
                                             self.coreConTrans['types'][i]['id'] == trans['after'][0]][0]
                            if TypeDict != self.measureType:
                                s_trans = {}
                                s_trans['before'] = trans['after']
                                s_trans['after'] = [str(self.core_id)]
                                transwithin.append(s_trans)
                                self.update_coreType(self.newAmount_type('network', self.coreConTrans['types'][netC_keywd_in]['keyword']))
                                self.update_id()
                    else:  # ['destination', 'networkC'] //'roadData'
                        trans['before'] = TypeDict['id'][desti_loc]
                        if 'extremaR' in TypeDict['tag']:
                            trans['after'] = [TypeDict['id'][n_in - 1]]
                        else:
                            trans['after'] = [TypeDict['id'][n_in]]
                        transwithin.append(trans)
                elif n_in - 1 >= 0 and TypeDict['tag'][
                    n_in - 1] == 'origin':  # ['origin', 'networkC'] //'roadData',
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
    def write_trans(self, parsedResult):
        try:
            parseTree = parsedResult[0]
            self.coreTypeDict = parsedResult[1]
            self.coreConTrans = parsedResult[2]
            self.core_id = parsedResult[3]

            # coretrans = []  # save all the transformation steps

            # functional roles index
            subis = []
            conis = []
            con_supis = []

            self.supis = []
            self.meais = []
            self.mea1is = []
            self.con_meais = []

            if 'subcon' in self.coreTypeDict['funcRole']:
                subis = [x for x, y in enumerate(self.coreTypeDict['funcRole']) if y == 'subcon']
            if 'condition' in self.coreTypeDict['funcRole']:
                conis = [x for x, y in enumerate(self.coreTypeDict['funcRole']) if
                         (y == 'condition' and self.coreTypeDict['types'][x]['tag'])]
            if 'support' in self.coreTypeDict['funcRole']:
                self.supis = [x for x, y in enumerate(self.coreTypeDict['funcRole']) if y == 'support']
            if 'measure' in self.coreTypeDict['funcRole']:
                self.meais = [x for x, y in enumerate(self.coreTypeDict['funcRole']) if y == 'measure']
                self.measureType = self.coreTypeDict['types'][self.meais[0]]
            if 'measure1' in self.coreTypeDict['funcRole']:
                self.mea1is = [x for x, y in enumerate(self.coreTypeDict['funcRole']) if y == 'measure1']

            if self.supis:
                conar = np.array(conis)
                supar = np.array(self.supis)
                con_supis = list(conar[conar < supar])
                self.con_meais = [x for x in conis if x not in con_supis]
            else:
                self.con_meais = conis

            if subis:
                subTypeDict = self.coreTypeDict['types'][subis[0]]
                cur_conTypeDict = self.coreTypeDict['types'][self.con_meais[0]]
                if subTypeDict['tag'] == ['coreC']:
                    if 'amount' not in cur_conTypeDict['text'][0] and 'pro' not in cur_conTypeDict['text'][0] and 'aggre' not in \
                            cur_conTypeDict['text'][0]:
                        self.update_coreTrans(self.gen_trans([cur_conTypeDict['id'][0], subTypeDict['id'][0]], [str(self.core_id)], None))
                        self.update_coreType(self.new_type(cur_conTypeDict['id'][0]))
                        cur_conTypeDict['id'][0] = str(self.core_id)
                        self.update_id()
                elif 'compareR' in subTypeDict['tag']:
                    self.comR_trans(subis[0], subis[0] + 1)
                elif 'extremaR' in subTypeDict['tag']:
                    if subTypeDict['text'][1] == 'closest to':
                        # distance trans
                        self.update_coreTrans(self.gen_trans([cur_conTypeDict['id'][0], subTypeDict['id'][0]], [str(self.core_id)], None))
                        self.update_coreType(self.newAmount_type('distance', None))
                        self.update_id()
                        # because of "closest to", group by trans
                        self.update_coreTrans(self.gen_trans([str(self.core_id-1)], [str(self.core_id)], cur_conTypeDict['id'][0]))
                        self.update_coreType(self.newAmount_type('networkquality', None))
                        self.update_id()
                        # condition input * distance -> new condition input
                        self.update_coreTrans(self.gen_trans([str(self.core_id - 1)], [str(self.core_id)], None))
                        self.update_coreType(self.new_type(cur_conTypeDict['id'][0]))
                        cur_conTypeDict['id'][0] = str(self.core_id)
                        self.update_id()
                    else:
                        self.extR_trans(subis[0], subis[0] + 1)
                else:
                    sub_trans = self.write_trans_within(subTypeDict)
                    if sub_trans:
                        self.update_coreTrans(sub_trans)
                    # update condition input
                    if self.coreTypeDict['funcRole'][subis[0] + 1] == 'condition':
                        input_sub_con = [self.coreTypeDict['types'][subis[0] + 1]['id'][0],
                                         self.coreTypeDict['types'][subis[0]]['id'][-1]]
                        if 'amount' in self.coreTypeDict['types'][subis[0] + 1]['text'][0] and 'distfield' in \
                                self.coreTypeDict['types'][subis[0]]['tag']:
                            distf_index = self.coreTypeDict['types'][subis[0]]['tag'].index('distfield')
                            self.update_coreTrans(self.gen_trans(input_sub_con, [str(self.core_id)],
                                                       self.coreTypeDict['types'][subis[0]]['id'][distf_index]))
                        else:
                            self.update_coreTrans(self.gen_trans(input_sub_con, [str(self.core_id)], None))
                        self.update_coreType(self.new_type(self.coreTypeDict['types'][subis[0] + 1]['id'][0]))
                        # update condition input id for next trans
                        self.coreTypeDict['types'][subis[0] + 1]['id'][0] = str(self.core_id)
                        self.update_id()

            if con_supis:
                consupTypeDict = self.coreTypeDict['types'][con_supis[0]]
                supTypeDict = self.coreTypeDict['types'][self.supis[0]]
                if 'compareR' in consupTypeDict['tag']:
                    self.comR_trans(con_supis[0], self.supis[0])
                elif 'extremaR' in consupTypeDict['tag']:
                    self.extR_trans(con_supis[0], self.supis[0])
                elif consupTypeDict['tag'][-1] == 'conAmount' and 'compareR' not in consupTypeDict['tag'] and 'extremaR' not in consupTypeDict['tag']:
                    self.conAmount_trans(con_supis[0], consupTypeDict)
                    # support * con_sup = support_u
                    self.update_coreTrans(self.gen_trans([supTypeDict['id'][0], consupTypeDict['id'][-1]], [str(self.core_id)], None))
                    self.update_coreType(self.new_type(supTypeDict['id'][0]))
                    # update support id
                    supTypeDict['id'][0] = str(self.core_id)
                    # update self.core_id
                    self.update_id()
                elif len(self.coreTypeDict['types'][con_supis[0]]['tag']) > 1:
                    self.update_coreTrans(self.write_trans_within(consupTypeDict))
                    # support * con_sup = support_u
                    self.update_coreTrans(self.gen_trans([supTypeDict['id'][0], consupTypeDict['id'][-1]], [str(self.core_id)], None))
                    self.update_coreType(self.new_type(supTypeDict['id'][0]))
                    # update support id
                    supTypeDict['id'][0] = str(self.core_id)
                    # update self.core_id
                    self.update_id()

            if self.con_meais:
                for ci in self.con_meais:
                    conTypeDict = self.coreTypeDict['types'][ci]
                    cur_mTypeDict = self.coreTypeDict['types'][self.meais[0]]
                    if conTypeDict['tag'] == ['coreC']:
                        if 'amount' not in cur_mTypeDict['text'][0] and 'pro' not in cur_mTypeDict['text'][0] and 'aggre' not in cur_mTypeDict['text'][0]:
                            self.update_coreTrans(self.gen_trans([cur_mTypeDict['id'][0], conTypeDict['id'][0]], [str(self.core_id)], None))
                            self.update_coreType(self.new_type(cur_mTypeDict['id'][0]))
                            cur_mTypeDict['id'][0] = str(self.core_id)
                            self.update_id()
                    elif conTypeDict['tag'] == ['visible']:
                        self.update_coreTrans(self.gen_trans([cur_mTypeDict['id'][0], conTypeDict['id'][0]], [str(self.core_id)], None))
                        self.update_coreType(self.newAmount_type('visibility', 'visibility surface'))
                    elif 'compareR' in conTypeDict['tag']:
                        self.comR_trans(ci, self.meais[0])
                    elif 'extremaR' in conTypeDict['tag']:
                        if len(conTypeDict['text']) > 1 and conTypeDict['text'][1] == 'closest to':
                            # distance trans
                            self.update_coreTrans(self.gen_trans([cur_mTypeDict['id'][0], conTypeDict['id'][0]], [str(self.core_id)], None))
                            self.update_coreType(self.newAmount_type('distance', None))
                            self.update_id()
                            # because of "closest to", group by networkquality into objectquality
                            self.update_coreTrans(self.gen_trans([str(self.core_id - 1)], [str(self.core_id)], cur_mTypeDict['id'][0]))
                            self.update_coreType(self.newAmount_type('networkquality', None))
                            self.update_id()
                            # objectquality -> new object
                            self.update_coreTrans(self.gen_trans([str(self.core_id - 1)], [str(self.core_id)], None))
                            self.update_coreType(self.new_type(cur_mTypeDict['id'][0]))
                            cur_mTypeDict['id'][0] = str(self.core_id)
                            self.update_id()
                        else:
                            self.extR_trans(ci, self.meais[0])
                    elif conTypeDict['tag'][-1] == 'conAmount' and 'compareR' not in conTypeDict['tag'] and 'extremaR' not in conTypeDict['tag']:
                        self.conAmount_trans(ci, conTypeDict)
                        # update measure
                        self.update_coreTrans(self.gen_trans([cur_mTypeDict['id'][0], conTypeDict['id'][-1]], [str(self.core_id)], None))
                        self.update_coreType(self.new_type(cur_mTypeDict['id'][0]))
                        cur_mTypeDict['id'][0] = str(self.core_id)
                        self.update_id()
                    elif len(conTypeDict['id']) > 1 and 'compareR' not in conTypeDict['tag'] and 'extremaR' not in conTypeDict['tag'] and 'conAmount' not in conTypeDict['tag']:
                        meainp_index = [i for i in range(0, len(self.coreConTrans['types'])) if self.coreConTrans['types'][i]['id'] == cur_mTypeDict['id'][0]][0]
                        if ('object' in conTypeDict['text'][0] or 'event' in conTypeDict['text'][0]) and ('object' in cur_mTypeDict['text'][0] or 'event' in cur_mTypeDict['text'][0]) \
                                and 'boolfield' in conTypeDict['tag'] and 'district' not in self.coreConTrans['types'][meainp_index]['keyword']:
                            # Which neighborhoods are within 100 meters from a school in Utrecht
                            self.update_coreTrans(self.gen_trans([conTypeDict['id'][0], cur_mTypeDict['id'][0]], [str(self.core_id)], None))
                            self.update_coreType(self.newAmount_type('distance', None))
                            self.update_id()
                            # distance -> new distance
                            self.update_coreTrans(self.gen_trans([str(self.core_id-1)], [str(self.core_id)], None))
                            self.update_coreType(self.newAmount_type('distance', None))
                            self.update_id()
                            # new distance -> object
                            self.update_coreTrans(self.gen_trans([str(self.core_id - 1)], [str(self.core_id)], None))
                            self.update_coreType(self.new_type(cur_mTypeDict['id'][0]))
                            cur_mTypeDict['id'][0] = str(self.core_id)
                            self.update_id()
                            self.remove_boolid(conTypeDict)
                        else:
                            con_trans = self.write_trans_within(conTypeDict)
                            self.update_coreTrans(con_trans)
                            if 'serviceobj' in conTypeDict['tag'] or conTypeDict['tag'][-1] == 'networkC':
                                conTypeDict['id'][-1] = con_trans[-1]['after'][0]
                            if 'amount' not in cur_mTypeDict['text'][0] and 'pro' not in cur_mTypeDict['text'][0] and 'aggre' not in cur_mTypeDict['text'][0]:
                                if 'region' in cur_mTypeDict['text'][0] and 'serviceobj' not in conTypeDict['tag']:
                                    # cur_mTypeDict['id'][0] = str(core_id)
                                    self.update_coreTrans(self.gen_trans([conTypeDict['id'][-1]], [cur_mTypeDict['id'][0]], None))
                                elif 'region' not in cur_mTypeDict['text'][0] and 'serviceobj' not in conTypeDict['tag']:
                                    con_mea_trans = self.gen_trans([cur_mTypeDict['id'][0], conTypeDict['id'][-1]], [str(self.core_id)], None)
                                    self.update_coreTrans(con_mea_trans)
                                    self.update_coreType(self.new_type(cur_mTypeDict['id'][0]))
                                    cur_mTypeDict['id'][0] = str(self.core_id)
                                    self.update_id()

            if self.meais:
                m0TypeDict = self.coreTypeDict['types'][self.meais[0]]
                if self.mea1is:
                    m1TypeDict = self.coreTypeDict['types'][self.mea1is[0]]
                    m1TypeDict = self.merge_aggConAmount(m1TypeDict)
                    for i in m0TypeDict:
                        for j in m1TypeDict[i]:
                            m0TypeDict[i].insert(-1, j)
                meaTypeDict = m0TypeDict
                if 'pro' in meaTypeDict['text'][-1]:
                    self.pro_trans(self.meais[0], meaTypeDict)
                elif 'conamount' in meaTypeDict['text'][-1]:
                    self.conAmount_trans(self.meais[0], meaTypeDict)
                elif 'covamount' in meaTypeDict['text'][-1]:
                    if meaTypeDict['tag'] == ['coreC', 'coreC']:
                        if not self.supis and not self.con_meais:
                            self.update_coreTrans(self.gen_trans([meaTypeDict['id'][0]], [meaTypeDict['id'][1]], None))
                        elif self.supis and not self.con_meais:
                            m_supTypeDict = self.coreTypeDict['types'][self.supis[0]]
                            self.update_coreTrans(self.gen_trans([meaTypeDict['id'][0], m_supTypeDict['id'][-1]], [meaTypeDict['id'][1]], None))
                        elif not self.supis and self.con_meais:
                            # new input -> covamount
                            self.update_coreTrans(self.gen_trans([meaTypeDict['id'][0]], [meaTypeDict['id'][1]], None))
                    elif meaTypeDict['tag'] == ['coreC', 'coreC', 'coreC']:
                        if self.supis and not self.con_meais:
                            m_supTypeDict = self.coreTypeDict['types'][self.supis[0]]
                            self.update_coreTrans(self.gen_trans([meaTypeDict['id'][0], meaTypeDict['id'][1], m_supTypeDict['id'][-1]], [meaTypeDict['id'][-1]], None))
                        elif not self.supis and not self.con_meais:
                            self.update_coreTrans(self.gen_trans(meaTypeDict['id'][0:2], [meaTypeDict['id'][-1]], None))
                    elif meaTypeDict['tag'] == ['coreC', 'aggre', 'coreC', 'coreC'] or meaTypeDict['tag'] == ['coreC', 'coreC', 'coreC', 'coreC']:
                        if not self.supis and not self.con_meais:
                            # aggre trans
                            self.update_coreTrans(self.gen_trans([meaTypeDict['id'][0], meaTypeDict['id'][2]], [meaTypeDict['id'][1]], meaTypeDict['id'][2]))
                            # aggre, coreC -> covA
                            self.update_coreTrans(self.gen_trans([meaTypeDict['id'][2], meaTypeDict['id'][1]], [meaTypeDict['id'][-1]], None))
                elif 'aggre' in meaTypeDict['text'][-1]:
                    self.aggre_trans(self.meais[0], meaTypeDict)
                else:
                    if self.supis and not self.con_meais:
                        m_supTypeDict = self.coreTypeDict['types'][self.supis[0]]
                        if meaTypeDict['tag'] == ['coreC']:
                            self.update_coreTrans(self.gen_trans([meaTypeDict['id'][0], m_supTypeDict['id'][-1]], [str(self.core_id)], m_supTypeDict['id'][-1]))
                            self.update_coreType(self.new_type(meaTypeDict['id'][0]))
                            self.update_id()
                        elif meaTypeDict['tag'] == ['coreC', 'coreC']:
                            self.update_coreTrans(self.gen_trans([meaTypeDict['id'][0], m_supTypeDict['id'][-1]], [meaTypeDict['id'][1]],
                                                       m_supTypeDict['id'][-1]))
                        elif meaTypeDict['tag'] == ['networkC', 'objectQ']:
                            self.update_coreTrans(self.gen_trans([meaTypeDict['id'][0], m_supTypeDict['id'][-1]], [meaTypeDict['id'][1]], m_supTypeDict['id'][-1]))
                    elif self.supis and self.con_meais:
                        m_supTypeDict = self.coreTypeDict['types'][self.supis[0]]
                        if meaTypeDict['tag'] == ['coreC']:
                            self.update_coreTrans(self.gen_trans([meaTypeDict['id'][0], m_supTypeDict['id'][-1]], [str(self.core_id)],
                                                       m_supTypeDict['id'][-1] if 'region' not in meaTypeDict['text'][0] else None))
                            self.update_coreType(self.new_type(meaTypeDict['id'][0]))
                            self.update_id()
                    else:
                        m_extent_id = self.coreTypeDict['types'][self.coreTypeDict['funcRole'].index('extent')][0]
                        if not self.supis and not self.con_meais and (meaTypeDict['tag'] == ['coreC'] or meaTypeDict['tag'] == ['networkC']):
                            self.update_coreTrans(self.gen_trans(meaTypeDict['id'], [str(self.core_id)], None))
                            self.update_coreType(self.new_type(meaTypeDict['id'][0]))
                            self.update_id()
                        if meaTypeDict['tag'] == ['coreC', 'location'] or meaTypeDict['tag'] == ['coreC', 'allocation']:
                            self.update_coreTrans(self.write_trans_within(meaTypeDict))
                        elif meaTypeDict['tag'] == ['coreC', 'conAm']:
                            self.update_coreTrans(self.gen_trans([meaTypeDict['id'][0]], [meaTypeDict['id'][1]], m_extent_id))
                        elif meaTypeDict['tag'] == ['coreC', 'coreC']:
                            self.update_coreTrans(self.gen_trans([meaTypeDict['id'][0]], [meaTypeDict['id'][1]], None))
                        elif meaTypeDict['tag'] == ['coreC', 'extremaR', 'location']:
                            if meaTypeDict['text'][1] in TransformHandler.extre_Dict['keyword']:
                                extK_index = TransformHandler.extre_Dict['keyword'].index(meaTypeDict['text'][1])
                                if TransformHandler.extre_Dict['cctag'][extK_index] == 'covamount':
                                    # meaTypeDict['id'][0] -> covamount, e.g., park -> area
                                    self.update_coreTrans(self.gen_trans([meaTypeDict['id'][0]], [str(self.core_id)],None))
                                    self.update_coreType(self.addext_type(meaTypeDict['text'][1]))  # update the type describing extremaR
                                else:
                                    self.update_coreType(self.addext_type(meaTypeDict['text'][1]))
                                # extremaR + meaTypeDict['id']['id'][0] -> new meaTypeDict['id'][0]
                                input0 = [meaTypeDict['id'][0], str(self.core_id)]
                                self.update_id()  # update self.core_id for output
                                self.update_coreTrans(self.gen_trans(input0, [str(self.core_id)], None))
                                self.update_coreType(self.new_type(meaTypeDict['id'][0]))
                                # update id of new meaTypeDict['id'][0]
                                meaTypeDict['id'][0] = str(self.core_id)
                                # location trans
                                self.update_coreTrans(self.write_trans_within(meaTypeDict))
                                self.update_id()
                        elif meaTypeDict['tag'][-1] == 'mergeO':
                            self.update_coreTrans(self.gen_trans(meaTypeDict['id'][:3], [meaTypeDict['id'][-1]], None))
                        elif meaTypeDict['tag'][-1] == 'networkQ' or meaTypeDict['tag'][-1] == 'networkC':
                            self.update_coreTrans(self.write_trans_within(meaTypeDict))
                        elif meaTypeDict['tag'][-1] == 'objectQ' and 'origin' in meaTypeDict['tag']:
                            self.update_coreTrans(self.write_trans_within(meaTypeDict))
                        elif meaTypeDict['tag'] == ['destination', 'origin', 'objectQ', 'coreC']:
                            objQ_TypeDict = {key: value[0: i + 1] for key, value in meaTypeDict.items() for i in range(len(value)) if
                         meaTypeDict['tag'][i] == 'objectQ'}
                            objQ_trans = self.write_trans_within(objQ_TypeDict)
                            self.update_coreTrans(objQ_trans)
                            self.update_coreTrans(self.gen_trans(objQ_trans[-1]['after'], [meaTypeDict['id'][-1]], None))

            # print('final trans\n', self.coreConTrans)

        except:
            print("Cannot generate transformations.\n{}".format(self.coreConTrans))

        return self.coreConTrans
