import rdflib
import os
import unittest
import re
import pyparsing

import pyalveo

import emu_parser
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

def pyalveoQuery(s):
    query = """
        PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>
        PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX maus:<http://ns.ausnc.org.au/schemas/annotation/maus/>
        PREFIX md:<http://ns.ausnc.org.au/schemas/corpora/mitcheldelbridge/items>
        PREFIX xml:<http://www.w3.org/XML/1998/namespace>
        PREFIX dada:<http://purl.org/dada/schema/0.2#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX ausnc: <http://ns.ausnc.org.au/schemas/ausnc_md_model/>
        %s
        #LIMIT 5
    """%s
    
    client = pyalveo.Client()
    results = client.sparql_query("mitcheldelbridge", query)
    
    return results["results"]["bindings"]

def clean_whitespace(text):
    return re.sub("\s+", " ", text)

class TestEmuConverter(unittest.TestCase):
    """Emu to SPARQL converter"""
    def setUp(self):
        pass

    def test_EmuParser(self):
        query = "maus:orthography='time'"
        p = emu_parser.parser(query)
        p_expected_keys = ['connector', 'left', 'right']

        self.assertEqual(type(p), pyparsing.ParseResults)
        self.assertItemsEqual(p['exp'].keys(), p_expected_keys)
        self.assertEqual(p.exp.left.text, "maus:orthography")
        self.assertEqual(p.exp.right.text, "time")
        self.assertEqual(p.exp.connector, "=")
        
        #conversion_tools.pretty_print(p)
    
    def test_EmuToLocal(self):
        query = "maus:orthography='time'"
        q = emu_parser.emuToSparql(query)
        #result = g.query(q)

        #self.assertGreater(len(results), 0)
    

    def test_EmuToSparql(self):
        """Basic Emu to SPARQL conversion"""
        
        query = "maus:orthography='time'"
        q = emu_parser.emuToSparql(query)
        q_expected="""select ?var1
        where {
                ?var1 dada:type maus:orthography.
                ?var1 dada:label 'time'.
        }"""

        q = clean_whitespace(q)
        q_expected = clean_whitespace(q_expected)
        self.assertEqual(q, q_expected)

    def test_EmuToPyalveo(self):
        """Emu to SPARQL, then query pyalveo"""
        
        query = "maus:orthography='time'"
        q = emu_parser.emuToSparql(query)
        results = pyalveoQuery(q)
        self.assertGreater(len(results), 0)

    def test_EmuSparql2(self):
        """Testing -> """

        query = "[maus:phonetic='t'->maus:phonetic='Ae']"
        q = emu_parser.emuToSparql(query)
        
        # sparql
        #print q
        
        # pyalveo
        results = pyalveoQuery(q)

        self.assertGreater(len(results), 0)

        for key in results[0]:
            self.assertRegexpMatches(results[0][key]["value"],
                                     "http://ns.ausnc.org.au/corpora/mitcheldelbridge/annotation/\d+")

        # local

    def test_EmuSparql3(self):
        """Testing ^ """

        query = "[maus:orthography='time'^maus:phonetic='Ae']"
        q = emu_parser.emuToSparql(query)
        
        # sparql
        print q
        
        # pyalveo
        results = pyalveoQuery(q)

        self.assertGreater(len(results), 0)

        for key in results[0]:
            self.assertRegexpMatches(results[0][key]["value"],
                                     "http://ns.ausnc.org.au/corpora/mitcheldelbridge/annotation/\d+")

        # local

    def test_EmuSparql4(self):
        """Testing & """

        query = "maus:phonetic='t'&rdf:type=dada:Annotation"
        q = emu_parser.emuToSparql(query)
        
        # sparql
        q_expected="""select \?(?P<var1>\w+)
        where {
                \?(?P=var1) dada:type maus:phonetic.
                \?(?P=var1) dada:label 't'.
                \?(?P=var1) rdf:type dada:Annotation.
        }"""

        q = clean_whitespace(q)
        q_expected = clean_whitespace(q_expected)

        self.assertRegexpMatches(q, q_expected)
        
        # pyalveo
        results = pyalveoQuery(q)

        self.assertGreater(len(results), 0)

        for key in results[0]:
            self.assertRegexpMatches(results[0][key]["value"],
                                     "http://ns.ausnc.org.au/corpora/mitcheldelbridge/annotation/\d+")

        # local

    def test_EmuSparql5(self):
        """Testing nesting """

        query = "[[maus:phonetic='t'->#maus:phonetic='Ae']->maus:phonetic='m']"
        q = emu_parser.emuToSparql(query)
        
        # sparql
        print q
        
        # pyalveo
        results = pyalveoQuery(q)

        self.assertGreater(len(results), 0)

        for key in results[0]:
            self.assertRegexpMatches(results[0][key]["value"],
                                     "http://ns.ausnc.org.au/corpora/mitcheldelbridge/annotation/\d+")

        # local

    def test_EmuSparql6(self):
        """Testing # """

        query = "[#maus:phonetic='t'->maus:phonetic='Ae']"
        q = emu_parser.emuToSparql(query)
        
        # sparql
        #print q
        
        # pyalveo
        results = pyalveoQuery(q)

        self.assertGreater(len(results), 0)
        self.assertEqual(len(results[0].keys()), 1)

        for key in results[0]:
            self.assertRegexpMatches(results[0][key]["value"],
                                     "http://ns.ausnc.org.au/corpora/mitcheldelbridge/annotation/\d+")

        # local

    def test_EmuSparql7(self):
        """Testing functions"""

        query = "Num(T,U)=1"
        q = emu_parser.emuToSparql(query)
        
        # sparql
        #print q
        
        # pyalveo
        results = pyalveoQuery(q)

        self.assertGreater(len(results), 0)

        for key in results[0]:
            self.assertRegexpMatches(results[0][key]["value"],
                                     "http://ns.ausnc.org.au/corpora/mitcheldelbridge/annotation/\d+")

        # local

    def test_EmuSparql8(self):
        """Testing | """

        query = "maus:phonetic='t'|'Ae'"
        q = emu_parser.emuToSparql(query)
        
        # sparql
        #print q
        
        # pyalveo
        results = pyalveoQuery(q)

        self.assertGreater(len(results), 0)

        for key in results[0]:
            self.assertRegexpMatches(results[0][key]["value"],
                                     "http://ns.ausnc.org.au/corpora/mitcheldelbridge/annotation/\d+")

        # local

    def test_EmuSparql9(self):
        """Testing != """

        query = "maus:phonetic!='t'"
        q = emu_parser.emuToSparql(query)
        
        # sparql
        #print q
        
        # pyalveo
        results = pyalveoQuery(q)

        self.assertGreater(len(results), 0)

        for key in results[0]:
            self.assertRegexpMatches(results[0][key]["value"],
                                     "http://ns.ausnc.org.au/corpora/mitcheldelbridge/annotation/\d+")

        # local
        

if __name__ == "__main__":
    #g = get_graph()
    unittest.main(exit=False)
