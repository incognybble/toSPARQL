import datetime

import conversion_tools
import emu_parser
import lpath_parser

def fn_name(func):
    def inner():
        print func.func_name
        return func()
    return inner

def test_basic_emu():
    query = "maus:phonetic='t'"
    q = emu_parser.emuToSparql(query)
    sparql = """select ?var1
    where {
            ?var1 dada:type maus:phonetic.
            ?var1 dada:label 't'.
    }"""
    results = conversion_tools.serverQuery(q, limit=False, timing=True)

def test_basic_lpath():
    query = "//t[@dada:type=maus:phonetic]"
    q = lpath_parser.lpathToSparql(query)
    sparql = """select ?var1
    where {
            ?var1 dada:label 't'.
            ?var1 dada:type maus:phonetic.
    }"""
    results = conversion_tools.serverQuery(q, limit=False, timing=True)

#@fn_name
def test_dominance_direct():
    q="""select ?var1
    where {
            ?var0 dada:hasChild ?var1.
            ?var0 dada:type maus:orthography.
            ?var0 dada:label 'time'.
            ?var1 dada:type maus:phonetic.
            ?var1 dada:label 'Ae'.
    }"""
    results = conversion_tools.serverQuery(q, limit=False, timing=True)

def test_dominance_indirect():
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


def test_dominance_emu():
    query = "[maus:orthography='time'^#maus:phonetic='Ae']"
    q = emu_parser.emuToSparql(query)
    sparql = """select ?var2
    where {
            ?var1 dada:type maus:orthography.
            ?var1 dada:label 'time'.
            ?var2 dada:type maus:phonetic.
            ?var2 dada:label 'Ae'.
            ?var1 dada:partof ?var3.
            ?var2 dada:partof ?var3.
            ?var1 dada:targets ?var4.
            ?var2 dada:targets ?var5.
            ?var4 dada:start ?var6.
            ?var5 dada:start ?var7.
            ?var4 dada:end ?var8.
            ?var5 dada:end ?var9.
            filter( ?var7 >= ?var6).
            filter( ?var9 <= ?var8).
    }"""
    results = conversion_tools.serverQuery(sparql, limit=False, timing=True)

def test_dominance_lpath():
    query = "//time[@dada:type=maus:orthography]/Ae[@dada:type=maus:phonetic]"
    q = lpath_parser.lpathToSparql(query)
    sparql = """select ?var2
    where {
            ?var1 dada:label 'time'.
            ?var1 dada:type maus:orthography.
            ?var1 dada:partof ?var3.
            ?var2 dada:partof ?var3.
            ?var1 dada:targets ?var4.
            ?var2 dada:targets ?var5.
            ?var4 dada:start ?var6.
            ?var5 dada:start ?var7.
            ?var4 dada:end ?var8.
            ?var5 dada:end ?var9.
            ?var2 dada:label 'Ae'.
            ?var2 dada:type maus:phonetic.
            filter( ?var7 >= ?var6).
            filter( ?var9 <= ?var8).
    }"""
    results = conversion_tools.serverQuery(sparql, limit=False, timing=True)

def test_dominance_optimise1():
    # Grouped type and labels
    sparql = """select ?var2
    where {
            ?var1 dada:type maus:orthography.
            ?var2 dada:type maus:phonetic.
            ?var1 dada:label 'time'.
            ?var2 dada:label 'Ae'.
            ?var1 dada:partof ?var3.
            ?var2 dada:partof ?var3.
            ?var1 dada:targets ?var4.
            ?var2 dada:targets ?var5.
            ?var4 dada:start ?var6.
            ?var5 dada:start ?var7.
            ?var4 dada:end ?var8.
            ?var5 dada:end ?var9.
            filter( ?var7 >= ?var6).
            filter( ?var9 <= ?var8).
    }"""
    results = conversion_tools.serverQuery(sparql, limit=False, timing=True)

def test_dominance_optimise2():
    # Moved labels to the top
    sparql = """select ?var2
    where {
            ?var1 dada:label 'time'.
            ?var2 dada:label 'Ae'.
            ?var1 dada:type maus:orthography.
            ?var2 dada:type maus:phonetic.
            ?var1 dada:partof ?var3.
            ?var2 dada:partof ?var3.
            ?var1 dada:targets ?var4.
            ?var2 dada:targets ?var5.
            ?var4 dada:start ?var6.
            ?var5 dada:start ?var7.
            ?var4 dada:end ?var8.
            ?var5 dada:end ?var9.
            filter( ?var7 >= ?var6).
            filter( ?var9 <= ?var8).
    }"""
    results = conversion_tools.serverQuery(sparql, limit=False, timing=True)

def test_dominance_optimise3():
    # types and labels to the bottom
    sparql = """select ?var2
    where {
            ?var1 dada:partof ?var3.
            ?var2 dada:partof ?var3.
            ?var1 dada:targets ?var4.
            ?var2 dada:targets ?var5.
            ?var4 dada:start ?var6.
            ?var5 dada:start ?var7.
            ?var4 dada:end ?var8.
            ?var5 dada:end ?var9.
            ?var1 dada:type maus:orthography.
            ?var2 dada:type maus:phonetic.
            ?var1 dada:label 'time'.
            ?var2 dada:label 'Ae'.
            filter( ?var7 >= ?var6).
            filter( ?var9 <= ?var8).
    }"""
    results = conversion_tools.serverQuery(sparql, limit=False, timing=True)

def test_dominance_optimise4():
    # types and labels at the bottom, but labels first
    sparql = """select ?var2
    where {
            ?var1 dada:partof ?var3.
            ?var2 dada:partof ?var3.
            ?var1 dada:targets ?var4.
            ?var2 dada:targets ?var5.
            ?var4 dada:start ?var6.
            ?var5 dada:start ?var7.
            ?var4 dada:end ?var8.
            ?var5 dada:end ?var9.
            ?var1 dada:label 'time'.
            ?var2 dada:label 'Ae'.
            ?var1 dada:type maus:orthography.
            ?var2 dada:type maus:phonetic.
            filter( ?var7 >= ?var6).
            filter( ?var9 <= ?var8).
    }"""
    results = conversion_tools.serverQuery(sparql, limit=False, timing=True)

def test_dominance_optimise5():
    # direct reordered
    q="""select ?var1
    where {
            ?var0 dada:label 'time'.
            ?var1 dada:label 'Ae'.
            ?var0 dada:hasChild ?var1.
            ?var0 dada:type maus:orthography.
            ?var1 dada:type maus:phonetic.
    }"""
    results = conversion_tools.serverQuery(q, limit=False, timing=True)


def test_empty_indirect():
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
    
def test_empty_emu():
    query = "[maus:orthography='time'^#maus:phonetic='r']"
    q = emu_parser.emuToSparql(query)
    sparql = """select ?var2
    where {
            ?var1 dada:type maus:orthography.
            ?var1 dada:label 'time'.
            ?var2 dada:type maus:phonetic.
            ?var2 dada:label 'r'.
            ?var1 dada:partof ?var3.
            ?var2 dada:partof ?var3.
            ?var1 dada:targets ?var4.
            ?var2 dada:targets ?var5.
            ?var4 dada:start ?var6.
            ?var5 dada:start ?var7.
            ?var4 dada:end ?var8.
            ?var5 dada:end ?var9.
            filter( ?var7 >= ?var6).
            filter( ?var9 <= ?var8).
    }"""
    results = conversion_tools.serverQuery(sparql, limit=False, timing=True)

def test_empty_lpath():
    query = "//time[@dada:type=maus:orthography]/r[@dada:type=maus:phonetic]"
    q = lpath_parser.lpathToSparql(query)
    sparql = """select ?var2
    where {
            ?var1 dada:label 'time'.
            ?var1 dada:type maus:orthography.
            ?var1 dada:partof ?var3.
            ?var2 dada:partof ?var3.
            ?var1 dada:targets ?var4.
            ?var2 dada:targets ?var5.
            ?var4 dada:start ?var6.
            ?var5 dada:start ?var7.
            ?var4 dada:end ?var8.
            ?var5 dada:end ?var9.
            ?var2 dada:label 'r'.
            ?var2 dada:type maus:phonetic.
            filter( ?var7 >= ?var6).
            filter( ?var9 <= ?var8).
    }"""
    results = conversion_tools.serverQuery(sparql, limit=False, timing=True)

def test_empty_optimise():
    sparql = """select ?var2
    where {
            ?var1 dada:label 'time'.
            ?var2 dada:label 'r'.
            ?var1 dada:type maus:orthography.
            ?var2 dada:type maus:phonetic.
            ?var1 dada:partof ?var3.
            ?var2 dada:partof ?var3.
            ?var1 dada:targets ?var4.
            ?var2 dada:targets ?var5.
            ?var4 dada:start ?var6.
            ?var5 dada:start ?var7.
            ?var4 dada:end ?var8.
            ?var5 dada:end ?var9.
            filter( ?var7 >= ?var6).
            filter( ?var9 <= ?var8).
    }"""
    results = conversion_tools.serverQuery(sparql, limit=False, timing=True)

def test_followedby_direct():
    q="""select ?var0 ?text0
    where {
            ?var0 dada:followedby ?var1.
            ?var0 dada:type maus:phonetic.
            ?var0 dada:label ?text0.
            ?var1 dada:type maus:phonetic.
            ?var1 dada:label 'r'.
    }"""
    results = conversion_tools.serverQuery(q, limit=False, timing=True)

def test_followedby_indirect():
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

def test_followedby_emu():
    query = "[#maus:phonetic!='_'->maus:phonetic='r']"
    q = emu_parser.emuToSparql(query)
    sparql = """select ?var1
    where {
            ?var1 dada:type maus:phonetic.
            ?var2 dada:type maus:phonetic.
            ?var2 dada:label 'r'.
            ?var1 dada:partof ?var3.
            ?var2 dada:partof ?var3.
            ?var1 dada:targets ?var4.
            ?var2 dada:targets ?var5.
            ?var4 dada:end ?var6.
            ?var5 dada:start ?var7.
            filter( ?var6 = ?var7).
            FILTER NOT EXISTS {
                    ?var1 dada:label '_'.
            }
    }"""
    results = conversion_tools.serverQuery(sparql, limit=False, timing=True)

def test_followedby_lpath():
    query = "//_[->r[@dada:type=maus:phonetic]]"
    q = lpath_parser.lpathToSparql(query)
    sparql = """select ?var1
    where {
            ?var1 dada:partof ?var3.
            ?var2 dada:partof ?var3.
            ?var1 dada:targets ?var4.
            ?var2 dada:targets ?var5.
            ?var4 dada:end ?var6.
            ?var5 dada:start ?var7.
            ?var2 dada:label 'r'.
            ?var2 dada:type maus:phonetic.
            filter( ?var6 = ?var7).
    }"""
    results = conversion_tools.serverQuery(sparql, limit=False, timing=True)

def test_followedby_optimise1():
    # like emu but without the not filter
    sparql="""select ?var1
    where {
            ?var1 dada:type maus:phonetic.
            ?var2 dada:type maus:phonetic.
            ?var2 dada:label 'r'.
            ?var1 dada:partof ?var3.
            ?var2 dada:partof ?var3.
            ?var1 dada:targets ?var4.
            ?var2 dada:targets ?var5.
            ?var4 dada:end ?var6.
            ?var5 dada:start ?var7.
            filter( ?var6 = ?var7).
    }"""
    results = conversion_tools.serverQuery(sparql, limit=False, timing=True)

def test_followedby_optimise2():
    # like emu reordered
    sparql="""select ?var1
    where {
            ?var2 dada:label 'r'.
            ?var1 dada:type maus:phonetic.
            ?var2 dada:type maus:phonetic.
            ?var1 dada:partof ?var3.
            ?var2 dada:partof ?var3.
            ?var1 dada:targets ?var4.
            ?var2 dada:targets ?var5.
            ?var4 dada:end ?var6.
            ?var5 dada:start ?var7.
            filter( ?var6 = ?var7).
            FILTER NOT EXISTS {
                    ?var1 dada:label '_'.
            }
    }"""
    results = conversion_tools.serverQuery(sparql, limit=False, timing=True)

def test_followedby_optimise3():
    # like emu reordered but without the not filter
    sparql="""select ?var1
    where {
            ?var2 dada:label 'r'.
            ?var1 dada:type maus:phonetic.
            ?var2 dada:type maus:phonetic.
            ?var1 dada:partof ?var3.
            ?var2 dada:partof ?var3.
            ?var1 dada:targets ?var4.
            ?var2 dada:targets ?var5.
            ?var4 dada:end ?var6.
            ?var5 dada:start ?var7.
            filter( ?var6 = ?var7).
    }"""
    results = conversion_tools.serverQuery(sparql, limit=False, timing=True)

def test_followedby_optimise4():
    # like reordered without filter
    sparql="""select ?var1
    where {
            ?var2 dada:label 'r'.
            ?var1 dada:type maus:phonetic.
            ?var2 dada:type maus:phonetic.
            ?var1 dada:partof ?var3.
            ?var2 dada:partof ?var3.
            ?var1 dada:targets ?var4.
            ?var2 dada:targets ?var5.
            ?var4 dada:end ?var6.
            ?var5 dada:start ?var6.
    }"""
    results = conversion_tools.serverQuery(sparql, limit=False, timing=True)

def test_sibling_direct():
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
    results = conversion_tools.serverQuery(q, limit=False, timing=True)
    
def test_sibling_indirect():
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

def test_sibling_emu():
    query = "[maus:orthography='time'^[maus:phonetic!='_'->#maus:phonetic!='_']]"
    q = emu_parser.emuToSparql(query)
    sparql = """select ?var3
    where {
            ?var1 dada:type maus:orthography.
            ?var1 dada:label 'time'.
            ?var2 dada:type maus:phonetic.
            ?var3 dada:type maus:phonetic.
            ?var2 dada:partof ?var4.
            ?var3 dada:partof ?var4.
            ?var2 dada:targets ?var5.
            ?var3 dada:targets ?var6.
            ?var5 dada:end ?var7.
            ?var6 dada:start ?var8.
            ?var1 dada:partof ?var9.
            ?var2 dada:partof ?var9.
            ?var1 dada:targets ?var10.
            ?var2 dada:targets ?var11.
            ?var10 dada:start ?var12.
            ?var11 dada:start ?var13.
            ?var10 dada:end ?var14.
            ?var11 dada:end ?var15.
            filter( ?var7 = ?var8).
            filter( ?var13 >= ?var12).
            filter( ?var15 <= ?var14).
            FILTER NOT EXISTS {
                    ?var2 dada:label '_'.
                    ?var3 dada:label '_'.
            }
    }"""
    results = conversion_tools.serverQuery(sparql, limit=False, timing=True)

def test_sibling_lpath():
    query = "//time[@dada:type=maus:orthography]/_[@dada:type=maus:phonetic]->_[@dada:type=maus:phonetic]"
    q = lpath_parser.lpathToSparql(query)
    sparql = """select ?var10
    where {
            ?var1 dada:label 'time'.
            ?var1 dada:type maus:orthography.
            ?var1 dada:partof ?var3.
            ?var2 dada:partof ?var3.
            ?var1 dada:targets ?var4.
            ?var2 dada:targets ?var5.
            ?var4 dada:start ?var6.
            ?var5 dada:start ?var7.
            ?var4 dada:end ?var8.
            ?var5 dada:end ?var9.
            ?var2 dada:type maus:phonetic.
            ?var2 dada:partof ?var11.
            ?var10 dada:partof ?var11.
            ?var2 dada:targets ?var12.
            ?var10 dada:targets ?var13.
            ?var12 dada:end ?var14.
            ?var13 dada:start ?var15.
            ?var10 dada:type maus:phonetic.
            filter( ?var7 >= ?var6).
            filter( ?var9 <= ?var8).
            filter( ?var14 = ?var15).
    }"""
    results = conversion_tools.serverQuery(sparql, limit=False, timing=True)


if __name__ == "__main__":
    # dominance
    print "Dominance"
    test_dominance_direct()
    test_dominance_indirect()
    test_dominance_emu()
    test_dominance_lpath()
    test_dominance_optimise1()
    test_dominance_optimise2()
    test_dominance_optimise3()
    test_dominance_optimise4()
    test_dominance_optimise5()

    # empty / bad dominance
    print "\nEmpty/bad dominance"
    test_empty_indirect()
    test_empty_emu()
    test_empty_lpath()
    test_empty_optimise()

    # followedby
    print "\nFollowed by"
    test_followedby_direct()
    test_followedby_indirect()
    test_followedby_emu()
    test_followedby_lpath()
    test_followedby_optimise1()
    test_followedby_optimise2()
    test_followedby_optimise3()
    test_followedby_optimise4()

    #sibling
    print "\nSibling"
    test_sibling_direct()
    test_sibling_indirect()
    test_sibling_emu()
    test_sibling_lpath()

