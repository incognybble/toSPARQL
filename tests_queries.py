import unittest
from datetime import datetime

import conversion_tools
import emu_parser
import lpath_parser

class TestQueries(unittest.TestCase):
    def setUp(self):
        self.start = datetime.now()
        #pass

    def tearDown(self):
        self.end = datetime.now()
        print self.end-self.start
        #pass

    def test_basic(self):
        """Basic: Find a phonetic node labelled 't'."""

        # EmuQL
        query = "maus:phonetic='t'"
        q = emu_parser.emuToSparql(query)
        results = conversion_tools.pyalveoQuery(q, limit=True)
        emu_res = results[0]
        
        # LPath+
        query = "//t[@dada:type=maus:phonetic]"
        q = lpath_parser.lpathToSparql(query)
        results = conversion_tools.pyalveoQuery(q, limit=True)
        lpath_res = results[0]

        self.assertEqual(lpath_res["var1"]["value"], emu_res["var1"]["value"])

    def test_sequence(self):
        """Sequence: Find a 't' followed by a 'Ae', where both are phonetic"""
        # EmuQL
        query = "[maus:phonetic='t'->#maus:phonetic='Ae']"
        q = emu_parser.emuToSparql(query)
        results = conversion_tools.pyalveoQuery(q, limit=True)
        emu_res = results[0]
        
        # LPath+
        query = "//t[@dada:type=maus:phonetic]->Ae[@dada:type=maus:phonetic]"
        q = lpath_parser.lpathToSparql(query)
        results = conversion_tools.pyalveoQuery(q, limit=True)
        lpath_res = results[0]

        #self.assertEqual(lpath_res["var1"]["value"], emu_res["var1"]["value"])
        self.assertEqual(lpath_res["var2"]["value"], emu_res["var2"]["value"])

    def test_dominance(self):
        """Dominance: Find a phonetic 'Ae' dominated by orthography 'time'.
        Same as a parent/child relationship."""

        # sparql direct
        q="""select ?var1
        where {
                ?var0 dada:hasChild ?var1.
                ?var0 dada:type maus:orthography.
                ?var0 dada:label 'time'.
                ?var1 dada:type maus:phonetic.
                ?var1 dada:label 'Ae'.
        }"""
        results = conversion_tools.serverQuery(q, limit=True)
        
        hand_short_res = results[0]

        # sparql indirect
        q="""select ?var0
        where {
                ?var0 dada:partof ?parent.
                ?var2 dada:partof ?parent.
                ?var0 dada:type maus:phonetic.
                ?var0 dada:label 'Ae'.
                ?var2 dada:type maus:orthography.
                ?var2 dada:label 'time'.
                ?var0 dada:targets ?time0.
                ?time0 dada:start ?start0.
                ?time0 dada:end ?end0.
                ?var2 dada:targets ?time2.
                ?time2 dada:start ?start2.
                ?time2 dada:end ?end2.
                filter (?start0 >= ?start2).
                filter (?end0 <= ?end2).
        }"""
        results = conversion_tools.serverQuery(q, limit=True)

        hand_long_res = results[0]
        
        self.assertEqual(hand_short_res["var1"]["value"], hand_long_res["var0"]["value"])

        # EmuQL
        query = "[maus:orthography='time'^#maus:phonetic='Ae']"
        q = emu_parser.emuToSparql(query)
        results = conversion_tools.pyalveoQuery(q, limit=True)
        emu_res = results[0]
        
        # LPath+
        query = "//time[@dada:type=maus:orthography]/Ae[@dada:type=maus:phonetic]"
        q = lpath_parser.lpathToSparql(query)
        results = conversion_tools.pyalveoQuery(q, limit=True)
        lpath_res = results[0]

        #self.assertEqual(lpath_res["var1"]["value"], emu_res["var1"]["value"])
        self.assertEqual(lpath_res["var2"]["value"], emu_res["var2"]["value"])

    def test_ancestor(self):
        pass

    def test_kleene(self):
        pass

    def test_last(self):
        """Right-most: Find phonetic 't' which are at the end of words"""

        q="""select ?var0 ?text
        where {
                ?var0 dada:partof ?parent.
                ?var2 dada:partof ?parent.
                
                ?var0 dada:type maus:phonetic.
                ?var0 dada:label 't'.
                
                ?var2 dada:type maus:orthography.
                ?var2 dada:label ?text.

                ?var0 dada:targets ?time0.
                ?time0 dada:end ?end0.
                
                ?var2 dada:targets ?time2.
                ?time2 dada:end ?end0.

        }"""
        results = conversion_tools.pyalveoQuery(q, limit=True)

        for result in results:
            print result["text"]["value"]+ ":" + result["var0"]["value"]

    def test_last2(self):
        """Right-most: Find words which end with phonetic 't'"""

        q="""select ?var2 ?text
        where {
                ?var0 dada:partof ?parent.
                ?var2 dada:partof ?parent.
                ?var0 dada:type maus:phonetic.
                ?var0 dada:label 't'.
                ?var2 dada:type maus:orthography.
                ?var2 dada:label ?text.
                ?var0 dada:targets ?time0.
                ?time0 dada:end ?end.
                ?var2 dada:targets ?time2.
                ?time2 dada:end ?end.
        }"""
        results = conversion_tools.pyalveoQuery(q, limit=True)

        for result in results:
            print result["var2"]["value"] + ":" + result["text"]["value"]

    def test_first(self):
        """Left-most: Find words which start with phonetic 's'"""

        q="""select ?var2 ?text
        where {
                ?var0 dada:partof ?parent.
                ?var2 dada:partof ?parent.
                ?var0 dada:type maus:phonetic.
                ?var0 dada:label 's'.
                ?var2 dada:type maus:orthography.
                ?var2 dada:label ?text.
                ?var0 dada:targets ?time0.
                ?time0 dada:start ?start.
                ?var2 dada:targets ?time2.
                ?time2 dada:start ?start.
        }"""
        results = conversion_tools.pyalveoQuery(q, limit=True)

        for result in results:
            print result["var2"]["value"] + ":" + result["text"]["value"]    

    def test_contains(self):
        """Contains: Find words which contain the phonetic 'r'"""

        q="""select ?var2 ?text
        where {
                ?var0 dada:partof ?parent.
                ?var2 dada:partof ?parent.
                ?var0 dada:type maus:phonetic.
                ?var0 dada:label 'r'.
                ?var2 dada:type maus:orthography.
                ?var2 dada:label ?text.
                ?var0 dada:targets ?time0.
                ?time0 dada:start ?start0.
                ?time0 dada:end ?end0.
                ?var2 dada:targets ?time2.
                ?time2 dada:start ?start2.
                ?time2 dada:end ?end2.
                filter (?start0 >= ?start2).
                filter (?end0 <= ?end2).
        }"""
        results = conversion_tools.pyalveoQuery(q, limit=True)

        #for result in results:
        #    print result["text"]["value"] + ":" + result["var2"]["value"]

        hand_res = results[0]

        # EmuQL
        query = "[#maus:orthography!='_'^maus:phonetic='r']"
        q = emu_parser.emuToSparql(query)
        results = conversion_tools.pyalveoQuery(q, limit=True)
        emu_res = results[0]
        
        self.assertEqual(hand_res["var2"]["value"], emu_res["var1"]["value"])
        
        # LPath+
        #query = "//_[@dada:type=maus:orthography][/r[@dada:type=maus:phonetic]]"
        query = "//_[/r[@dada:type=maus:phonetic]]"
        q = lpath_parser.lpathToSparql(query)
        results = conversion_tools.pyalveoQuery(q, limit=True)
        lpath_res = results[0]

        self.assertEqual(lpath_res["var1"]["value"], emu_res["var1"]["value"])

        

    def test_followedby(self):
        """Followedby: Find sounds which are followed by 'r' i.e. immediate siblings"""

        q="""select ?var0 ?text0
        where {
                ?var0 dada:followedby ?var1.
                ?var0 dada:type maus:phonetic.
                ?var0 dada:label ?text0.
                ?var1 dada:type maus:phonetic.
                ?var1 dada:label 'r'.
        }"""
        results = conversion_tools.serverQuery(q, limit=True)
        
        hand_short_res = results[0]


        q="""select ?var0 ?text0
        where {
                        ?var0 dada:partof ?parent.
                        ?var2 dada:partof ?parent.
                        ?var0 dada:targets ?time0.
                        ?time0 dada:end ?end.
                        ?var2 dada:targets ?time2.
                        ?time2 dada:start ?end.
                        ?var0 dada:label ?text0.
                        ?var2 dada:label 'r'.
                        ?var0 dada:type maus:phonetic.
        }"""
        results = conversion_tools.serverQuery(q, limit=True)

        hand_long_res = results[0]
        
        self.assertEqual(hand_short_res["var0"]["value"], hand_long_res["var0"]["value"])
        self.assertEqual(hand_short_res["text0"]["value"], hand_long_res["text0"]["value"])

        # EmuQL
        query = "[#maus:phonetic!='_'->maus:phonetic='r']"
        q = emu_parser.emuToSparql(query)
        results = conversion_tools.serverQuery(q, limit=True)
        emu_res = results[0]

        #print q

        self.assertEqual(hand_short_res["var0"]["value"], emu_res["var1"]["value"])
        
        # LPath+
        #query = "//_[@dada:type=maus:phonetic]->r[@dada:type=maus:phonetic]"
        query = "//_[->r[@dada:type=maus:phonetic]]"
        q = lpath_parser.lpathToSparql(query)
        results = conversion_tools.serverQuery(q, limit=True)
        lpath_res = results[0]

        print q
        print lpath_res

        self.assertEqual(hand_short_res["var0"]["value"], lpath_res["var1"]["value"])

    def test_not(self):
        """Not: Find words which are not 'time'"""

        q="""select ?var1 ?text
        where {
                ?var1 dada:type maus:orthography.
                ?var1 dada:label ?text.
                filter not exists {
                    ?var1 dada:label 'time'.}
        }"""
        results = conversion_tools.pyalveoQuery(q, limit=True)

        for result in results:
            print result["text"]["value"] + ":" + result["var1"]["value"]

        hand_res = results[0]

        # EmuQL
        query = "maus:orthography!='time'"
        q = emu_parser.emuToSparql(query)
        results = conversion_tools.pyalveoQuery(q, limit=True)
        emu_res = results[0]
        
        self.assertEqual(hand_res["var1"]["value"], emu_res["var1"]["value"])
        
        # LPath+
        query = "//_[not @dada:label='time']"
        q = lpath_parser.lpathToSparql(query)
        results = conversion_tools.pyalveoQuery(q, limit=True)
        lpath_res = results[0]

        #print q
        #print lpath_res

        self.assertEqual(lpath_res["var1"]["value"], emu_res["var1"]["value"])

    def test_empty(self):
        q="""select ?var1
        where {
                ?var0 dada:hasChild ?var1.
                ?var0 dada:type maus:orthography.
                ?var0 dada:label 'time'.
                ?var1 dada:type maus:phonetic.
                ?var1 dada:label 'r'.
        }"""
        results = conversion_tools.serverQuery(q, limit=True)
        self.assertEqual(len(results), 0)

        q="""select ?var0
        where {
                ?var0 dada:partof ?parent.
                ?var2 dada:partof ?parent.
                ?var0 dada:type maus:phonetic.
                ?var0 dada:label 'r'.
                ?var2 dada:type maus:orthography.
                ?var2 dada:label 'time'.
                ?var0 dada:targets ?time0.
                ?time0 dada:start ?start0.
                ?time0 dada:end ?end0.
                ?var2 dada:targets ?time2.
                ?time2 dada:start ?start2.
                ?time2 dada:end ?end2.
                filter (?start0 >= ?start2).
                filter (?end0 <= ?end2).
        }"""
        results = conversion_tools.serverQuery(q, limit=True)
        self.assertEqual(len(results), 0)
        
        query = "[maus:orthography='time'^#maus:phonetic='r']"
        q = emu_parser.emuToSparql(query)
        results = conversion_tools.serverQuery(q, limit=True)
        self.assertEqual(len(results), 0)
        
        query = "//time[@dada:type=maus:orthography]/r[@dada:type=maus:phonetic]"
        q = lpath_parser.lpathToSparql(query)
        results = conversion_tools.serverQuery(q, limit=True)
        self.assertEqual(len(results), 0)

if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)
