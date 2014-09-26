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
        #results = conversion_tools.pyalveoQuery(q, limit=True)
        results = conversion_tools.pyalveoQuery(q)
        emu_res = results[0]
        emu_ress = results
        
        # LPath+
        query = "//t[@dada:type=maus:phonetic]"
        q = lpath_parser.lpathToSparql(query)
        #results = conversion_tools.pyalveoQuery(q, limit=True)
        results = conversion_tools.pyalveoQuery(q)
        lpath_res = results[0]
        lpath_ress = results

        self.assertEqual(lpath_res["var1"]["value"], emu_res["var1"]["value"])
        self.assertEqual(len(emu_ress), len(lpath_ress))

    def test_sequence(self):
        """Sequence: Find a 't' followed by a 'Ae', where both are phonetic"""
        # EmuQL
        query = "[maus:phonetic='t'->#maus:phonetic='Ae']"
        q = emu_parser.emuToSparql(query)
        #results = conversion_tools.pyalveoQuery(q, limit=True)
        results = conversion_tools.pyalveoQuery(q)
        emu_res = results[0]
        emu_ress = results
        
        # LPath+
        query = "//t[@dada:type=maus:phonetic]->Ae[@dada:type=maus:phonetic]"
        q = lpath_parser.lpathToSparql(query)
        #results = conversion_tools.pyalveoQuery(q, limit=True)
        results = conversion_tools.pyalveoQuery(q)
        lpath_res = results[0]
        lpath_ress = results

        self.assertEqual(lpath_res["var2"]["value"], emu_res["var2"]["value"])
        self.assertEqual(len(emu_ress), len(lpath_ress))

    def test_dominance(self):
        """Dominance: Find a phonetic 'Ae' dominated by orthography 'time'.
        Same as a parent/child relationship. Same as 'contains' concept."""

        # sparql direct
        q="""select ?var1
        where {
                ?var0 dada:hasChild ?var1.
                ?var0 dada:type maus:orthography.
                ?var0 dada:label 'time'.
                ?var1 dada:type maus:phonetic.
                ?var1 dada:label 'Ae'.
        }"""
        #results = conversion_tools.serverQuery(q, limit=True)
        results = conversion_tools.serverQuery(q)
        
        hand_short_res = results[0]
        hand_short_ress = results

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
        #results = conversion_tools.serverQuery(q, limit=True)
        results = conversion_tools.serverQuery(q)

        hand_long_res = results[0]
        hand_long_ress = results
        
        self.assertEqual(hand_short_res["var1"]["value"], hand_long_res["var0"]["value"])
        self.assertEqual(len(hand_short_ress), len(hand_long_ress))

        # EmuQL
        query = "[maus:orthography='time'^#maus:phonetic='Ae']"
        q = emu_parser.emuToSparql(query)
        #results = conversion_tools.serverQuery(q, limit=True)
        results = conversion_tools.serverQuery(q)
        emu_res = results[0]
        emu_ress = results
        
        # LPath+
        query = "//time[@dada:type=maus:orthography]/Ae[@dada:type=maus:phonetic]"
        q = lpath_parser.lpathToSparql(query)
        #results = conversion_tools.serverQuery(q, limit=True)
        results = conversion_tools.serverQuery(q)
        lpath_res = results[0]
        lpath_ress = results

        self.assertEqual(lpath_res["var2"]["value"], emu_res["var2"]["value"])
        self.assertEqual(len(lpath_ress), len(emu_ress))
        
        self.assertEqual(emu_res["var2"]["value"], hand_long_res["var0"]["value"])
        self.assertEqual(len(emu_ress), len(hand_long_ress))

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

        #for result in results:
        #    print result["text"]["value"]+ ":" + result["var0"]["value"]

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

        #for result in results:
        #    print result["var2"]["value"] + ":" + result["text"]["value"]

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

        #for result in results:
        #    print result["var2"]["value"] + ":" + result["text"]["value"]    
        

    def test_followedby(self):
        """Followedby: Find sounds which are followed by 'r' i.e. sequence query including wildcard usage"""

        q="""select ?var0 ?text0
        where {
                ?var0 dada:followedby ?var1.
                ?var0 dada:type maus:phonetic.
                ?var0 dada:label ?text0.
                ?var1 dada:type maus:phonetic.
                ?var1 dada:label 'r'.
        }"""
        #results = conversion_tools.serverQuery(q, limit=True)
        results = conversion_tools.serverQuery(q)
        
        hand_short_res = results[0]
        hand_short_ress = results

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
        #results = conversion_tools.serverQuery(q, limit=True)
        results = conversion_tools.serverQuery(q)

        hand_long_res = results[0]
        hand_long_ress = results
        
        self.assertEqual(hand_short_res["var0"]["value"], hand_long_res["var0"]["value"])
        self.assertEqual(hand_short_res["text0"]["value"], hand_long_res["text0"]["value"])
        self.assertEqual(len(hand_short_ress), len(hand_long_ress))

        # EmuQL
        query = "[#maus:phonetic!='_'->maus:phonetic='r']"
        q = emu_parser.emuToSparql(query)
        #results = conversion_tools.serverQuery(q, limit=True)
        results = conversion_tools.serverQuery(q)
        emu_res = results[0]
        emu_ress = results
        
        #print q

        self.assertEqual(hand_short_res["var0"]["value"], emu_res["var1"]["value"])
        self.assertEqual(len(hand_short_ress), len(emu_ress))
        
        # LPath+
        #query = "//_[@dada:type=maus:phonetic]->r[@dada:type=maus:phonetic]"
        query = "//_[->r[@dada:type=maus:phonetic]]"
        #query = "//_[@dada:type=maus:orthography]/_[->r[@dada:type=maus:phonetic]]"
        q = lpath_parser.lpathToSparql(query)
        #results = conversion_tools.serverQuery(q, limit=True)
        results = conversion_tools.serverQuery(q)
        lpath_res = results[0]
        lpath_ress = results

        print q
        print len(hand_short_ress)
        print len(lpath_ress)
        
        self.assertEqual(hand_short_res["var0"]["value"], lpath_res["var1"]["value"])
        self.assertEqual(len(hand_short_ress), len(lpath_ress))
        

    def test_not(self):
        """Not: Find words which are not 'time'"""

        q="""select ?var1 ?text
        where {
                ?var1 dada:type maus:orthography.
                ?var1 dada:label ?text.
                filter not exists {
                    ?var1 dada:label 'time'.}
        }"""
        #results = conversion_tools.serverQuery(q, limit=True)
        results = conversion_tools.serverQuery(q)

        #for result in results:
        #    print result["text"]["value"] + ":" + result["var1"]["value"]

        hand_res = results[0]
        hand_ress = results

        # EmuQL
        query = "maus:orthography!='time'"
        q = emu_parser.emuToSparql(query)
        #results = conversion_tools.serverQuery(q, limit=True)
        results = conversion_tools.serverQuery(q)
        emu_res = results[0]
        emu_ress = results
        
        self.assertEqual(hand_res["var1"]["value"], emu_res["var1"]["value"])
        self.assertEqual(len(hand_ress), len(emu_ress))
        
        # LPath+
        query = "//_[not @dada:label='time']"
        q = lpath_parser.lpathToSparql(query)
        #results = conversion_tools.serverQuery(q, limit=True)
        results = conversion_tools.serverQuery(q)
        lpath_res = results[0]
        lpath_ress = results

        print q
        print lpath_res

        self.assertEqual(lpath_res["var1"]["value"], emu_res["var1"]["value"])
        self.assertEqual(len(lpath_ress), len(emu_ress))

    def test_empty(self):
        """Empty: Find a word 'time' that has the sound 'r' i.e. should return zero results"""
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

    def test_sibling(self):
        """Sibling: Find the immediate siblings in 'time'."""

        # direct sparql
        q="""select ?text1 ?text2 ?var1 ?var2
        where {
                ?var0 dada:hasChild ?var1.
                ?var0 dada:hasChild ?var2.
                ?var1 dada:followedby ?var2.
                ?var0 dada:type maus:orthography.
                ?var0 dada:label 'time'.
                ?var1 dada:type maus:phonetic.
                ?var1 dada:label ?text1.
                ?var2 dada:type maus:phonetic.
                ?var2 dada:label ?text2.
        }"""
        #results = conversion_tools.serverQuery(q, limit=True)
        results = conversion_tools.serverQuery(q)
        
        hand_short_res = results[0]
        hand_short_ress = results
        

        # indirect sparql
        q="""select ?text1 ?text2 ?var1 ?var2
        where {
                ?var0 dada:partof ?parent.
                ?var1 dada:partof ?parent.
                ?var2 dada:partof ?parent.
                ?var0 dada:type maus:orthography.
                ?var0 dada:label 'time'.
                ?var1 dada:type maus:phonetic.
                ?var1 dada:label ?text1.
                ?var2 dada:type maus:phonetic.
                ?var2 dada:label ?text2.
                ?var0 dada:targets ?time0.
                ?time0 dada:start ?start0.
                ?time0 dada:end ?end0.
                ?var1 dada:targets ?time1.
                ?time1 dada:start ?start1.
                ?time1 dada:end ?end1.
                ?var2 dada:targets ?time2.
                ?time2 dada:start ?end1.
                ?time2 dada:end ?end2.
                filter (?start1 >= ?start0).
                filter (?end2 <= ?end0).
        }"""
        #results = conversion_tools.serverQuery(q, limit=True)
        results = conversion_tools.serverQuery(q)
        
        hand_long_res = results[0]
        hand_long_ress = results

        #print hand_short_res["text1"]["value"]
        #print hand_long_res["text1"]["value"]

        #print hand_short_res["text2"]["value"]
        #print hand_long_res["text2"]["value"]
        
        
        self.assertEqual(hand_short_res["var1"]["value"], hand_long_res["var1"]["value"])
        self.assertEqual(hand_short_res["text1"]["value"], hand_long_res["text1"]["value"])
        self.assertEqual(hand_short_res["var2"]["value"], hand_long_res["var2"]["value"])
        self.assertEqual(hand_short_res["text2"]["value"], hand_long_res["text2"]["value"])
        self.assertEqual(len(hand_short_ress), len(hand_long_ress))

        # emu
        query = "[maus:orthography='time'^[maus:phonetic!='_'->#maus:phonetic!='_']]"
        q = emu_parser.emuToSparql(query)
        #results = conversion_tools.serverQuery(q, limit=True)
        results = conversion_tools.serverQuery(q)

        print q

        emu_res = results[0]
        emu_ress = results

        self.assertEqual(hand_long_res["var2"]["value"], emu_res["var3"]["value"])
        self.assertEqual(len(hand_long_ress), len(emu_ress))

        # lpath
        query = "//time[@dada:type=maus:orthography]/_[@dada:type=maus:phonetic]->_[@dada:type=maus:phonetic]"
        q = lpath_parser.lpathToSparql(query)
        #results = conversion_tools.serverQuery(q, limit=True)
        results = conversion_tools.serverQuery(q)

        print q

        lpath_res = results[0]
        lpath_ress = results

        self.assertEqual(hand_long_res["var2"]["value"], lpath_res["var10"]["value"])
        self.assertEqual(len(hand_long_ress), len(lpath_ress))


if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)
