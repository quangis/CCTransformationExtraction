"""
This module contains functions to transforms a natural language query into a
transformation graph. In dire need of modularisation.
"""

import sys
import json
from pathlib import Path
from rdflib import Graph, RDF
from rdflib.term import BNode
from transformation_algebra import \
    TransformationGraph, TransformationQuery, TA
from transformation_algebra.type import Product, Top, TypeOperation
from cct.language import cct, R3
from geo_question_parser.Identify import QuestionParser
from geo_question_parser.Identify import TypesToQueryConverter


def question2query(q: dict) -> TransformationGraph:
    """
    Converts a dictionary returned by Haiqi's natural language parser into a
    `TransformationGraph`, which can be in turn translated to a SPARQL query.
    """
    # This should probably go in a more sane place eventually, when the
    # structure of the modules is more stable
    base = q['cctrans']

    g = TransformationGraph(cct)
    task = BNode()
    types = {}
    for x in base['types']:
        types[x['id']] = x
        x['node'] = node = BNode()
        t = cct.parse_type(x['cct']).concretize(Top)
        if isinstance(t, TypeOperation) and t.params[0].operator == Product:
            assert isinstance(t.params[0], TypeOperation)
            t = R3(t.params[0].params[0], t.params[1], t.params[0].params[1])
        g.add((node, TA.type, cct.uri(t)))

    for edge in base['transformations']:
        for before in edge['before']:
            for after in edge['after']:
                b = types[before]['node']
                a = types[after]['node']
                g.add((b, TA["from"], a))

    g.add((task, RDF.type, TA.Task))
    g.add((task, TA.output, types['0']['node']))
    return g


for arg in sys.argv[1:]:
    name = Path(arg).stem
    g = Graph()
    g.parse(arg, "ttl")
    root = g.value(None, RDF.type, TA.Task, any=False)
    question = g.value(root, TA.question, any=False)
    if question:
        try:
            parser = QuestionParser(None)
            qParsed = parser.parseQuestion(str(question))
            cctAnnotator = TypesToQueryConverter()
            cctAnnotator.algebraToQuery(qParsed, True, True)
            cctAnnotator.algebraToExpandedQuery(qParsed, False, False)
            with open(f"json-{name}.json", 'w') as f:
                json.dump(qParsed, f)
            graph = question2query(qParsed)
            graph.serialize(f"graph-{name}.ttl", format="turtle")
        except Exception as e:
            print(f"failure on {arg}: {e}")
    else:
        print(f"Skipping {arg}")
