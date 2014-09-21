import rdflib
import os
import unittest
import re
import pyparsing

import lpath_parser
import conversion_tools


class TestLPathConverter(unittest.TestCase):
    """LPath+ to SPARQL converter"""
    def setUp(self):
        pass

    def test_LpathParser(self):
        pass

    def test_LpathToSparql(self):
        pass

    def test_LpathChild(self):
        query = "//time/Ae"

        # parser
        p = lpath_parser.parser(query)
        self.assertEqual(type(p), pyparsing.ParseResults)
        
        self.assertEqual(p.exp.connector, "//")
        self.assertEqual(p.exp.right.left.text, "time")
        self.assertEqual(p.exp.right.right.text, "Ae")
        self.assertEqual(p.exp.right.connector, "/")
        
        # sparql
        q = lpath_parser.lpathToSparql(query)

        #print q

    def test_LpathSequence(self):
        query = "//t->Ae"
        
        # parser
        p = lpath_parser.parser(query)
        self.assertEqual(type(p), pyparsing.ParseResults)
        
        self.assertEqual(p.exp.connector, "//")
        self.assertEqual(p.exp.right.left.text, "t")
        self.assertEqual(p.exp.right.right.text, "Ae")
        self.assertEqual(p.exp.right.connector, "->")
        
        # sparql
        q = lpath_parser.lpathToSparql(query)
        
    def test_LpathPredicate(self):
        query = "//time[/Ae]"

        # parser
        p = lpath_parser.parser(query)
        self.assertEqual(type(p), pyparsing.ParseResults)
        
        self.assertEqual(p.exp.connector, "//")
        self.assertEqual(p.exp.right.text, "time")
        self.assertEqual(p.exp.right.predicate.right.text, "Ae")
        self.assertEqual(p.exp.right.predicate.connector, "/")
        
        # sparql
        q = lpath_parser.lpathToSparql(query)

    def test_LpathPredicateNest(self):
        pass

    def test_LpathAttribute(self):
        query = "//time[@dada:type=maus:orthography]"
        
        # parser
        p = lpath_parser.parser(query)
        self.assertEqual(type(p), pyparsing.ParseResults)
        
        self.assertEqual(p.exp.connector, "//")
        self.assertEqual(p.exp.right.text, "time")
        self.assertEqual(p.exp.right.attr_test.attr, "dada:type")
        self.assertEqual(p.exp.right.attr_test.attr_val, "maus:orthography")
        
        # sparql
        q = lpath_parser.lpathToSparql(query)

    def test_LpathWildcard(self):
        query = "//_[/t]"
        
        # parser
        p = lpath_parser.parser(query)
        self.assertEqual(type(p), pyparsing.ParseResults)
        
        self.assertEqual(p.exp.connector, "//")
        self.assertEqual(p.exp.right.text, "_")
        self.assertEqual(p.exp.right.predicate.right.text, "t")
        self.assertEqual(p.exp.right.predicate.connector, "/")
        
        # sparql
        q = lpath_parser.lpathToSparql(query)

    def test_LpathNot(self):
        pass

    def test_LpathOr(self):
        pass

    def test_LpathAnd(self):
        pass

    def test_LpathFunction(self):
        pass


if __name__ == "__main__":
    unittest.main(exit=False)
