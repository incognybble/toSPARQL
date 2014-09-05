import rdflib
import os
import unittest
import re
import pyparsing
from datetime import datetime


import emu_parser
import lpath_parser
import conversion_tools



def get_files(config):
    path = config["location"]
    total_files = []
    
    files = os.listdir(path)

    for f in files:
        loc = os.path.join(path, f)
        if not os.path.isdir(loc):
            ext = os.path.splitext(loc)[1]
            if ext == ".rdf":
                total_files.append(loc)


    return total_files

def get_graph(config):
    g = rdflib.graph.Graph()
    files = get_files(config)

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

class TestGeneral(unittest.TestCase):
    def setUp(self):
        self.start = datetime.now()
        self.config = conversion_tools.get_config()

    def tearDown(self):
        self.end = datetime.now()
        #print "Start: " + str(self.start)
        #print "End: " + str(self.end)
        #print "Timing: " + str(self.end-self.start)
        print self.end-self.start

    def test_localQuery(self):
        """Testing handwritten and generated queries against local data store"""
        g = get_graph(self.config)
        
        # handwritten query
        q="""select ?var0
        where {
                ?var0 dada:type maus:phonetic.
                ?var0 dada:label 't'.
        }"""
        q = conversion_tools.cleanQuery(q, limit=True)
        results = g.query(q)

        self.assertEqual(len(results), 1)
        for result in results:
            first_result_hand = result

        self.assertEqual(type(first_result_hand["var0"]), rdflib.term.URIRef)
        self.assertRegexpMatches(str(first_result_hand["var0"]),
                                     "http://ns.ausnc.org.au/corpora/mitcheldelbridge/annotation/\d+")

        
        # EmuQL generated query
        query = "maus:phonetic='t'"
        q = emu_parser.emuToSparql(query)
        q = conversion_tools.cleanQuery(q, limit=True)
        results = g.query(q)

        self.assertEqual(len(results), 1)
        for result in results:
            first_result_emu = result
            #print first_result_emu
            
        self.assertGreater(len(first_result_emu), 0)
        self.assertEqual(type(first_result_emu["var1"]), rdflib.term.URIRef)
        self.assertRegexpMatches(str(first_result_emu["var1"]),
                                     "http://ns.ausnc.org.au/corpora/mitcheldelbridge/annotation/\d+")

        self.assertEqual(first_result_hand["var0"], first_result_emu["var1"])


        # LPath+ generated query
        query = "//t[@dada:type=maus:phonetic]"
        q = lpath_parser.lpathToSparql(query)
        q = conversion_tools.cleanQuery(q, limit=True)
        results = g.query(q)

        #print q

        self.assertEqual(len(results), 1)
        for result in results:
            first_result_lpath = result
            #print first_result_lpath
            
        self.assertGreater(len(first_result_lpath), 0)
        self.assertEqual(type(first_result_lpath["var1"]), rdflib.term.URIRef)
        self.assertRegexpMatches(str(first_result_lpath["var1"]),
                                     "http://ns.ausnc.org.au/corpora/mitcheldelbridge/annotation/\d+")

        self.assertEqual(first_result_hand["var0"], first_result_lpath["var1"])


    def test_serverQuery(self):
        """Testing handwritten and generated queries against own server"""

        # handwritten query
        q="""select ?var0
        where {
                ?var0 dada:type maus:phonetic.
                ?var0 dada:label 't'.
        }"""

        results = conversion_tools.serverQuery(q, True, self.config)

        self.assertGreater(len(results), 0)
        first_result_hand = results[0]
        self.assertTrue(first_result_hand.has_key("var0"))
        self.assertEqual(first_result_hand["var0"]["type"], "uri")
        self.assertRegexpMatches(first_result_hand["var0"]["value"],
                                     "http://ns.ausnc.org.au/corpora/mitcheldelbridge/annotation/\d+")


        # EmuQL generated query
        query = "maus:phonetic='t'"
        q = emu_parser.emuToSparql(query)

        results = conversion_tools.serverQuery(q, True, self.config)

        self.assertGreater(len(results), 0)
        first_result_emu = results[0]
        self.assertGreater(len(first_result_emu.keys()), 0)
        key = first_result_emu.keys()[0]
        self.assertEqual(first_result_emu[key]["type"], "uri")
        self.assertRegexpMatches(first_result_emu[key]["value"],
                                     "http://ns.ausnc.org.au/corpora/mitcheldelbridge/annotation/\d+")

        self.assertDictContainsSubset(first_result_hand["var0"], first_result_emu[key])


        # LPath+ generated query
        query = "//t[@dada:type=maus:phonetic]"
        q = lpath_parser.lpathToSparql(query)

        results = conversion_tools.serverQuery(q, True, self.config)

        self.assertGreater(len(results), 0)
        first_result_lpath = results[0]
        self.assertGreater(len(first_result_lpath.keys()), 0)
        key = first_result_lpath.keys()[0]
        self.assertEqual(first_result_lpath[key]["type"], "uri")
        self.assertRegexpMatches(first_result_lpath[key]["value"],
                                     "http://ns.ausnc.org.au/corpora/mitcheldelbridge/annotation/\d+")

        self.assertDictContainsSubset(first_result_hand["var0"], first_result_lpath[key])



    def test_PyalveoQuery(self):
        """Testing handwritten and generated queries against pyalveo"""
        # handwritten query
        q="""select ?var0
        where {
                ?var0 dada:type maus:phonetic.
                ?var0 dada:label 't'.
        }"""
        results = conversion_tools.pyalveoQuery(q, limit=True)

        self.assertGreater(len(results), 0)
        first_result_hand = results[0]
        self.assertTrue(first_result_hand.has_key("var0"))
        self.assertEqual(first_result_hand["var0"]["type"], "uri")
        self.assertRegexpMatches(first_result_hand["var0"]["value"],
                                     "http://ns.ausnc.org.au/corpora/mitcheldelbridge/annotation/\d+")

        
        # EmuQL generated query
        query = "maus:phonetic='t'"
        q = emu_parser.emuToSparql(query)
        results = conversion_tools.pyalveoQuery(q, limit=True)

        self.assertGreater(len(results), 0)
        first_result_emu = results[0]
        self.assertGreater(len(first_result_emu.keys()), 0)
        key = first_result_emu.keys()[0]
        self.assertEqual(first_result_emu[key]["type"], "uri")
        self.assertRegexpMatches(first_result_emu[key]["value"],
                                     "http://ns.ausnc.org.au/corpora/mitcheldelbridge/annotation/\d+")

        self.assertDictContainsSubset(first_result_hand["var0"], first_result_emu[key])

        # LPath+ generated query
        query = "//t[@dada:type=maus:phonetic]"
        q = lpath_parser.lpathToSparql(query)
        results = conversion_tools.pyalveoQuery(q, limit=True)

        self.assertGreater(len(results), 0)
        first_result_lpath = results[0]
        self.assertGreater(len(first_result_lpath.keys()), 0)
        key = first_result_lpath.keys()[0]
        self.assertEqual(first_result_lpath[key]["type"], "uri")
        self.assertRegexpMatches(first_result_lpath[key]["value"],
                                     "http://ns.ausnc.org.au/corpora/mitcheldelbridge/annotation/\d+")

        self.assertDictContainsSubset(first_result_hand["var0"], first_result_lpath[key])



if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)
