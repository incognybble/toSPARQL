import unittest
#from datetime import datetime

import conversion_tools
import emu_parser
import lpath_parser

class TestTiming(unittest.TestCase):
    def setUp(self):
        #self.start = datetime.now()
        pass

    def tearDown(self):
        #self.end = datetime.now()
        #self.runtime = self.end-self.start
        #print self.runtime
        pass

    def test_basic_emu(self):
        query = "maus:phonetic='t'"
        q = emu_parser.emuToSparql(query)
        results = conversion_tools.serverQuery(q, limit=False, timing=True)

    def test_basic_lpath(self):
        query = "//t[@dada:type=maus:phonetic]"
        q = lpath_parser.lpathToSparql(query)
        results = conversion_tools.serverQuery(q, limit=False, timing=True)

    def test_sequence_emu(self):
        query = "[maus:phonetic='t'->#maus:phonetic='Ae']"
        q = emu_parser.emuToSparql(query)
        results = conversion_tools.serverQuery(q, limit=False, timing=True)

    def test_sequence_lpath(self):
        query = "//t[@dada:type=maus:phonetic]->Ae[@dada:type=maus:phonetic]"
        q = lpath_parser.lpathToSparql(query)
        results = conversion_tools.serverQuery(q, limit=False, timing=True)

    def test_dominance_direct(self):
        q="""select ?var1
        where {
                ?var0 dada:hasChild ?var1.
                ?var0 dada:type maus:orthography.
                ?var0 dada:label 'time'.
                ?var1 dada:type maus:phonetic.
                ?var1 dada:label 'Ae'.
        }"""
        results = conversion_tools.serverQuery(q, limit=False, timing=True)

    def test_dominance_indirect(self):
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
        results = conversion_tools.serverQuery(q, limit=False, timing=True)

    def test_dominance_emu(self):
        query = "[maus:orthography='time'^#maus:phonetic='Ae']"
        q = emu_parser.emuToSparql(query)
        results = conversion_tools.serverQuery(q, limit=False, timing=True)

    def test_dominance_lpath(self):
        query = "//time[@dada:type=maus:orthography]/Ae[@dada:type=maus:phonetic]"
        q = lpath_parser.lpathToSparql(query)
        results = conversion_tools.serverQuery(q, limit=False, timing=True)

    def test_empty_direct(self):
        q="""select ?var1
        where {
                ?var0 dada:hasChild ?var1.
                ?var0 dada:type maus:orthography.
                ?var0 dada:label 'time'.
                ?var1 dada:type maus:phonetic.
                ?var1 dada:label 'r'.
        }"""
        results = conversion_tools.serverQuery(q, limit=False, timing=True)

    def test_empty_indirect(self):
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
        results = conversion_tools.serverQuery(q, limit=False, timing=True)
        
    def test_empty_emu(self):
        query = "[maus:orthography='time'^#maus:phonetic='r']"
        q = emu_parser.emuToSparql(query)
        results = conversion_tools.serverQuery(q, limit=False, timing=True)

    def test_empty_lpath(self):
        query = "//time[@dada:type=maus:orthography]/r[@dada:type=maus:phonetic]"
        q = lpath_parser.lpathToSparql(query)
        results = conversion_tools.serverQuery(q, limit=False, timing=True)

    def test_followedby_direct(self):
        q="""select ?var0 ?text0
        where {
                ?var0 dada:followedby ?var1.
                ?var0 dada:type maus:phonetic.
                ?var0 dada:label ?text0.
                ?var1 dada:type maus:phonetic.
                ?var1 dada:label 'r'.
        }"""
        results = conversion_tools.serverQuery(q, limit=False, timing=True)

    def test_followedby_indirect(self):
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
        results = conversion_tools.serverQuery(q, limit=False, timing=True)

    def test_followedby_emu(self):
        query = "[#maus:phonetic!='_'->maus:phonetic='r']"
        q = emu_parser.emuToSparql(query)
        results = conversion_tools.serverQuery(q, limit=False, timing=True)

    def test_followedby_lpath(self):
        query = "//_[->r[@dada:type=maus:phonetic]]"
        q = lpath_parser.lpathToSparql(query)
        results = conversion_tools.serverQuery(q, limit=False, timing=True)

    def test_not_emu(self):
        query = "maus:orthography!='time'"
        q = emu_parser.emuToSparql(query)
        results = conversion_tools.serverQuery(q, limit=False, timing=True)

    def test_not_lpath(self):
        query = "//_[not @dada:label='time']"
        q = lpath_parser.lpathToSparql(query)
        results = conversion_tools.serverQuery(q, limit=False, timing=True)

    def test_sibling_direct(self):
        q="""select ?text1 ?text2 ?var1 ?var2
        where {
                ?var0 dada:hasChild ?var1.
                ?var0 dada:hasChild ?var2.
                ?var1 dada:followedby ?va2.
                ?var0 dada:type maus:orthography.
                ?var0 dada:label 'time'.
                ?var1 dada:type maus:phonetic.
                ?var1 dada:label ?text1.
                ?var2 dada:type maus:phonetic.
                ?var2 dada:label ?text2.
        }"""
        results = conversion_tools.serverQuery(q, limit=False, timing=True)
        
    def test_sibling_indirect(self):
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
        results = conversion_tools.serverQuery(q, limit=False, timing=True)
        
    def test_sibling_emu(self):
        query = "[maus:orthography='time'^[maus:phonetic!='_'->#maus:phonetic!='_']]"
        q = emu_parser.emuToSparql(query)
        results = conversion_tools.serverQuery(q, limit=False, timing=True)

    def test_sibling_lpath(self):
        query = "//time[@dada:type=maus:orthography]/_[@dada:type=maus:phonetic]->_[@dada:type=maus:phonetic]"
        q = lpath_parser.lpathToSparql(query)
        results = conversion_tools.serverQuery(q, limit=False, timing=True)


if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)
