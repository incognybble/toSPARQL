import rdflib
import os
import unittest
import pyparsing
from datetime import datetime

import emu_parser
import conversion_tools


class TestEmuConverter(unittest.TestCase):
    """Emu to SPARQL converter"""
    def setUp(self):
        self.start = datetime.now()

    def tearDown(self):
        self.end = datetime.now()
        print self.end-self.start

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

    def test_EmuToSparql(self):
        """Basic Emu to SPARQL conversion"""
        
        query = "maus:orthography='time'"
        q = emu_parser.emuToSparql(query)
        q_expected="""select ?var1
        where {
                ?var1 dada:type maus:orthography.
                ?var1 dada:label 'time'.
        }"""

        q = conversion_tools.clean_whitespace(q)
        q_expected = conversion_tools.clean_whitespace(q_expected)
        self.assertEqual(q, q_expected)


    def test_EmuSparql2(self):
        """Testing -> """

        query = "[maus:phonetic='t'->maus:phonetic='Ae']"
        
        # parser
        p = emu_parser.parser(query)
        p_expected_keys = ['connector', 'left', 'right']

        self.assertEqual(type(p), pyparsing.ParseResults)
        self.assertItemsEqual(p['exp'].keys(), p_expected_keys)

        self.assertEqual(p.exp.connector, "->")

        self.assertEqual(type(p.exp.left), pyparsing.ParseResults)
        self.assertEqual(p.exp.left.left.text, "maus:phonetic")
        self.assertEqual(p.exp.left.right.text, "t")
        self.assertEqual(p.exp.left.connector, "=")

        self.assertEqual(p.exp.right.left.text, "maus:phonetic")
        self.assertEqual(p.exp.right.right.text, "Ae")
        self.assertEqual(p.exp.right.connector, "=")
        
        # to sparql
        sparql = emu_parser.emuToSparql(query)
        
        #print sparql
        q_expected="""select [\?\s\w]*\?(?P<var1>\w+)[\?\s\w]*
        where {.*?
                \?(?P=var1) dada:type maus:phonetic\..*?
                \?(?P=var1) dada:label 't'\..*?
        }"""
        
        q = conversion_tools.clean_whitespace(sparql)
        q_expected = conversion_tools.clean_whitespace(q_expected)
        
        self.assertRegexpMatches(q, q_expected)


    def test_EmuSparql3(self):
        """Testing ^ """

        query = "[maus:orthography='time'^maus:phonetic='Ae']"

       # parser
        p = emu_parser.parser(query)
        p_expected_keys = ['connector', 'left', 'right']

        self.assertEqual(type(p), pyparsing.ParseResults)
        self.assertItemsEqual(p['exp'].keys(), p_expected_keys)

        self.assertEqual(p.exp.connector, "^")

        self.assertEqual(type(p.exp.left), pyparsing.ParseResults)
        self.assertEqual(p.exp.left.left.text, "maus:orthography")
        self.assertEqual(p.exp.left.right.text, "time")
        self.assertEqual(p.exp.left.connector, "=")

        self.assertEqual(p.exp.right.left.text, "maus:phonetic")
        self.assertEqual(p.exp.right.right.text, "Ae")
        self.assertEqual(p.exp.right.connector, "=")
        
        # to sparql
        sparql = emu_parser.emuToSparql(query)
        
        q_expected="""select [\?\s\w]*\?(?P<var1>\w+)[\?\s\w]*
        where {.*?
                \?(?P=var1) dada:type maus:orthography\..*?
                \?(?P=var1) dada:label 'time'\..*?
        }"""
        
        q = conversion_tools.clean_whitespace(sparql)
        q_expected = conversion_tools.clean_whitespace(q_expected)
        
        self.assertRegexpMatches(q, q_expected)
        
        # pyalveo
        results = conversion_tools.pyalveoQuery(q, limit=True)

        self.assertGreater(len(results), 0)

        for key in results[0]:
            self.assertRegexpMatches(results[0][key]["value"],
                                     "http://ns.ausnc.org.au/corpora/mitcheldelbridge/annotation/\d+")


    def test_EmuSparql4(self):
        """Testing & """

        query = "maus:phonetic='t'&rdf:type=dada:Annotation"

       # parser
        p = emu_parser.parser(query)
        p_expected_keys = ['connector', 'left', 'right']

        self.assertEqual(type(p), pyparsing.ParseResults)
        self.assertItemsEqual(p['exp'].keys(), p_expected_keys)

        self.assertEqual(p.exp.connector, "&")

        self.assertEqual(type(p.exp.left), pyparsing.ParseResults)
        self.assertEqual(p.exp.left.left.text, "maus:phonetic")
        self.assertEqual(p.exp.left.right.text, "t")
        self.assertEqual(p.exp.left.connector, "=")

        self.assertEqual(p.exp.right.left.text, "rdf:type")
        self.assertEqual(p.exp.right.right.text, "dada:Annotation")
        self.assertEqual(p.exp.right.connector, "=")

        # sparql
        sparql = emu_parser.emuToSparql(query)
        q_expected="""select \?(?P<var1>\w+)
        where {
                \?(?P=var1) dada:type maus:phonetic.
                \?(?P=var1) dada:label 't'.
                \?(?P=var1) rdf:type dada:Annotation.
        }"""

        q = conversion_tools.clean_whitespace(sparql)
        q_expected = conversion_tools.clean_whitespace(q_expected)

        self.assertRegexpMatches(q, q_expected)
        
        # pyalveo
        results = conversion_tools.pyalveoQuery(q, limit=True)

        self.assertGreater(len(results), 0)

        for key in results[0]:
            self.assertRegexpMatches(results[0][key]["value"],
                                     "http://ns.ausnc.org.au/corpora/mitcheldelbridge/annotation/\d+")


    def test_EmuSparql5(self):
        """Testing nesting : NEEDS FIXING"""

        query = "[[maus:phonetic='t'->#maus:phonetic='Ae']->maus:phonetic='m']"

        # parser
        
        
        # sparql
        q = emu_parser.emuToSparql(query)
        print q
        
        # pyalveo
        results = conversion_tools.pyalveoQuery(q)

        self.assertGreater(len(results), 0)

        for key in results[0]:
            self.assertRegexpMatches(results[0][key]["value"],
                                     "http://ns.ausnc.org.au/corpora/mitcheldelbridge/annotation/\d+")


    def test_EmuSparql6(self):
        """Testing # """

        query = "[#maus:phonetic='t'->maus:phonetic='Ae']"
        
        # parser
        p = emu_parser.parser(query)
        p_expected_keys = ['connector', 'left', 'right']

        self.assertEqual(type(p), pyparsing.ParseResults)
        self.assertItemsEqual(p['exp'].keys(), p_expected_keys)

        self.assertEqual(p.exp.connector, "->")

        self.assertEqual(type(p.exp.left), pyparsing.ParseResults)
        self.assertEqual(p.exp.left.left.hash, "#")
        self.assertEqual(p.exp.left.left.text, "maus:phonetic")
        self.assertEqual(p.exp.left.right.text, "t")
        self.assertEqual(p.exp.left.connector, "=")

        self.assertEqual(p.exp.right.left.text, "maus:phonetic")
        self.assertEqual(p.exp.right.right.text, "Ae")
        self.assertEqual(p.exp.right.connector, "=")
        
        # to sparql
        sparql = emu_parser.emuToSparql(query)

        q_expected="""select \?(?P<var1>\w+)
        where {.*?
                \?(?P=var1) dada:type maus:phonetic\..*?
                \?(?P=var1) dada:label 't'\..*?
        }"""
        
        q = conversion_tools.clean_whitespace(sparql)
        q_expected = conversion_tools.clean_whitespace(q_expected)
        
        self.assertRegexpMatches(q, q_expected)

        
    def test_EmuSparql7(self):
        """Testing functions : NOT IMPLEMENTED"""

        query = "Num(T,U)=1"

        # parser

        # sparql
        q = emu_parser.emuToSparql(query)


    def test_EmuSparql8(self):
        """Testing | : NEED TO CHECK SPARQL"""

        query = "maus:phonetic='t'|'Ae'"
        q = emu_parser.emuToSparql(query)
        
        # sparql
        #print q
        
        # pyalveo
        results = conversion_tools.pyalveoQuery(q)

        self.assertGreater(len(results), 0)

        for key in results[0]:
            self.assertRegexpMatches(results[0][key]["value"],
                                     "http://ns.ausnc.org.au/corpora/mitcheldelbridge/annotation/\d+")


    def test_EmuSparql9(self):
        """Testing !="""

        query = "rdf:type=dada:Annotation&maus:phonetic!='t'"
        
        # parser
        p = emu_parser.parser(query)
        p_expected_keys = ['connector', 'left', 'right']

        self.assertEqual(type(p), pyparsing.ParseResults)
        self.assertItemsEqual(p['exp'].keys(), p_expected_keys)

        self.assertEqual(p.exp.connector, "&")

        self.assertEqual(type(p.exp.left), pyparsing.ParseResults)
        self.assertEqual(p.exp.left.left.text, "rdf:type")
        self.assertEqual(p.exp.left.right.text, "dada:Annotation")
        self.assertEqual(p.exp.left.connector, "=")
        
        self.assertEqual(p.exp.right.left.text, "maus:phonetic")
        self.assertEqual(p.exp.right.right.text, "t")
        self.assertEqual(p.exp.right.connector, "!=")

        # sparql
        sparql = emu_parser.emuToSparql(query)
        q_expected="""select \?(?P<var1>\w+)
        where {.*?
                \?(?P=var1) rdf:type dada:Annotation\..*?
                \?(?P=var1) dada:type maus:phonetic\..*?
                FILTER NOT EXISTS {.*?
                    \?(?P=var1) dada:label 't'\..*?
                }
        }"""
        
        q = conversion_tools.clean_whitespace(sparql)
        q_expected = conversion_tools.clean_whitespace(q_expected)
        
        self.assertRegexpMatches(q, q_expected)

        # pyalveo
        results = conversion_tools.pyalveoQuery(q, limit=True)

        self.assertGreater(len(results), 0)

        for key in results[0]:
            self.assertRegexpMatches(results[0][key]["value"],
                                     "http://ns.ausnc.org.au/corpora/mitcheldelbridge/annotation/\d+")



if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)
