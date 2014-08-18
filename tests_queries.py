import unittest
from datetime import datetime

import conversion_tools
import emu_parser
import lpath_parser

class TestQueries(unittest.TestCase):
    def setUp(self):
        self.start = datetime.now()

    def tearDown(self):
        self.end = datetime.now()
        #print "Start: " + str(self.start)
        #print "End: " + str(self.end)
        #print "Timing: " + str(self.end-self.start)
        print self.end-self.start

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
        pass
    

if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)
