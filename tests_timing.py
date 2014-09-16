import unittest
from datetime import datetime

import conversion_tools
import emu_parser
import lpath_parser

class TestTiming(unittest.TestCase):
    def setUp(self):
        self.start = datetime.now()

    def tearDown(self):
        self.end = datetime.now()
        self.runtime = self.end-self.start
        print self.runtime

    def test_basic_emu(self):
        query = "maus:phonetic='t'"
        q = emu_parser.emuToSparql(query)
        results = conversion_tools.serverQuery(q, limit=False)

    def test_basic_lpath(self):
        query = "//t[@dada:type=maus:phonetic]"
        q = lpath_parser.lpathToSparql(query)
        results = conversion_tools.serverQuery(q, limit=False)

    def test_sequence_emu(self):
        query = "[maus:phonetic='t'->#maus:phonetic='Ae']"
        q = emu_parser.emuToSparql(query)
        results = conversion_tools.serverQuery(q, limit=False)

    def test_sequence_lpath(self):
        query = "//t[@dada:type=maus:phonetic]->Ae[@dada:type=maus:phonetic]"
        q = lpath_parser.lpathToSparql(query)
        results = conversion_tools.serverQuery(q, limit=False)

    def test_dominance_direct(self):
        q="""select ?var1
        where {
                ?var0 dada:hasChild ?var1.
                ?var0 dada:type maus:orthography.
                ?var0 dada:label 'time'.
                ?var1 dada:type maus:phonetic.
                ?var1 dada:label 'Ae'.
        }"""
        results = conversion_tools.serverQuery(q, limit=False)

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
        results = conversion_tools.serverQuery(q, limit=False)

    def test_dominance_emu(self):
        query = "[maus:orthography='time'^#maus:phonetic='Ae']"
        q = emu_parser.emuToSparql(query)
        results = conversion_tools.serverQuery(q, limit=False)

    def test_dominance_lpath(self):
        query = "//time[@dada:type=maus:orthography]/Ae[@dada:type=maus:phonetic]"
        q = lpath_parser.lpathToSparql(query)
        results = conversion_tools.serverQuery(q, limit=False)

    def test_contains_emu(self):
        query = "[#maus:orthography!='x'^maus:phonetic='r']"
        q = emu_parser.emuToSparql(query)
        results = conversion_tools.serverQuery(q, limit=False)

    def test_contains_lpath(self):
        query = "//_[/r[@dada:type=maus:phonetic]]"
        q = lpath_parser.lpathToSparql(query)
        results = conversion_tools.serverQuery(q, limit=False)

    def test_followedby_direct(self):
        q="""select ?var0 ?text0
        where {
                ?var0 dada:followedby ?var1.
                ?var0 dada:type maus:phonetic.
                ?var0 dada:label ?text0.
                ?var1 dada:type maus:phonetic.
                ?var1 dada:label 'r'.
        }"""
        results = conversion_tools.serverQuery(q, limit=False)

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
        results = conversion_tools.serverQuery(q, limit=False)

    def test_followedby_emu(self):
        query = "[#maus:phonetic!='_'->maus:phonetic='r']"
        q = emu_parser.emuToSparql(query)
        results = conversion_tools.serverQuery(q, limit=False)

    def test_followedby_lpath(self):
        query = "//_[->r[@dada:type=maus:phonetic]]"
        q = lpath_parser.lpathToSparql(query)
        results = conversion_tools.serverQuery(q, limit=False)


if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)
