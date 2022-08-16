from __future__ import annotations

import sys
from pathlib import Path
from rdflib import Graph, RDF
from transformation_algebra import TA
from geo_question_parser.parser import parse_question

for arg in sys.argv[1:]:
    name = Path(arg).stem
    g = Graph()
    g.parse(arg, "ttl")
    root = g.value(None, RDF.type, TA.Task, any=False)
    question = g.value(root, TA.question, any=False) or ""
    if question:
        try:
            query = parse_question(str(question))
            query.graph.serialize(f"graph-{name}.ttl", format="turtle")
            query.sparql()

        except Exception as e:
            print(f"failure on {arg}: {e}")
    else:
        print(f"Skipping {arg}")
