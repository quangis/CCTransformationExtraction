"""
This module contains functions to transforms a natural language query into a
transformation graph. In dire need of modularisation.
"""

from __future__ import annotations

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

def question2query(qParsed: dict) -> TransformationGraph:
    # This should probably go in a more sane place eventually, when the
    # structure of the modules is more stable

    g = TransformationGraph(cct)
    task = BNode()
    g.add((task, RDF.type, TA.Task))

    def f(q: dict | str) -> BNode:
        """
        Converts a dictionary returned by Haiqi's natural language parser into a
        `TransformationGraph`, which can be in turn translated to a SPARQL query.
        """

        node = BNode()

        t = cct.parse_type(q['after']['cct']).concretize(Top)
        if isinstance(t, TypeOperation) and t.params[0].operator == Product:
            assert isinstance(t.params[0], TypeOperation)
            t = R3(t.params[0].params[0], t.params[1], t.params[0].params[1])
        g.add((node, TA.type, cct.uri(t)))

        for b in q.get('before') or ():
            g.add((node, TA['from'], f(b)))

        return node

    g.add((task, TA.output, f(qParsed['queryEx'])))
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
                json.dump(qParsed, f, indent=4)
            graph = question2query(qParsed)
            graph.serialize(f"graph-{name}.ttl", format="turtle")
        except Exception as e:
            print(f"failure on {arg}: {e}")
    else:
        print(f"Skipping {arg}")
