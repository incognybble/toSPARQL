import rdflib
import os
import unittest
import re
import pyparsing

import lpath_parser
import conversion_tools


def get_files():
    path = "" # needs data!
    total_files = []
    
    files = os.listdir(path)

    for f in files:
        loc = os.path.join(path, f)
        if not os.path.isdir(loc):
            ext = os.path.splitext(loc)[1]
            if ext == ".rdf":
                total_files.append(loc)


    return total_files

def get_graph():
    g = rdflib.graph.Graph()
    files = get_files()

    total = float(len(files))
    counter = float(1)

    print total
    
    for f in files:
        if counter%500==0:
            print str((counter/total)*100) + "% - " + f
        g.parse(f, format="n3")
        counter += 1

    return g



def clean_whitespace(text):
    return re.sub("\s+", " ", text)


class TestLPathConverter(unittest.TestCase):
    """LPath+ to SPARQL converter"""
    def setUp(self):
        pass

if __name__ == "__main__":
    #g = get_graph()
    unittest.main(exit=False)
