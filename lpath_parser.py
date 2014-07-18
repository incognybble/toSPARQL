# Created: 13th June 2014

import re
from pyparsing import Word, alphas, Literal, Group, Optional, OneOrMore, Regex, ZeroOrMore, Forward

from pyparsing import ParseResults

import conversion_tools

def parser(text):
    var_any = Literal("_")
    p = Regex("[\w:]+")#.setResultsName("text")
    var_any = Regex(".+?")
    attribute = Literal("@")
    eq = Literal("=")
    closure = Literal("?") | Literal("*") | Literal("+")

    test = Literal("^") + p | p + Literal("$") | p | var_any
    axis = Literal("\\\\*") | \
           Literal("\\\\") | \
           Literal("\\") | \
           Literal(".") | \
           Literal("//*") | \
           Literal("//") | \
           Literal("/") | \
           Literal("-->") | \
           Literal("<--") | \
           Literal("->") | \
           Literal("<-") | \
           Literal("==>") | \
           Literal("<==") | \
           Literal("=>") | \
           Literal("<=")

    abspath = Forward()
    locstep = Forward()

    node = test.setResultsName("node")
    attr_test = Group(attribute.suppress() + node.setResultsName("attr") + eq.suppress() + node.setResultsName("attr_val")).setResultsName("attr_test")
    predicate = (Group(Literal("[").suppress() + attr_test + Literal("]").suppress()).setResultsName("predicate") |\
                 Group(Literal("[").suppress() + abspath + Literal("]").suppress()).setResultsName("predicate"))
    locstep << Group(axis.setResultsName("axis") + node + \
              Optional(predicate + Optional(closure).setResultsName("closure"))).setResultsName("locstep")

    abs2 = abspath
    abspath << (Group(locstep.setResultsName("left_step") + abs2).setResultsName("abspath") | locstep.setResultsName("right_step"))

    # TODO
    locpath = abspath
    fexpr = locpath
    
    return fexpr.parseString(text)

def xlpathToSparql(lpath):
    p = parser(lpath)

    pdict = p.asDict()

    (triples, varcounter, end_var) = treeToSparql(pdict)

    s = "select " + end_var

    s = s + "\nwhere {\n"
    for trip in triples:
        s = conversion_tools.prettyTriple(s, trip)
    s = s + "}"
    
    return s

def lpathToSparql(lpath):
    p = parser(lpath)

    pdict = p.asDict()

    data = {}
    data["triples"] = []
    data["varcounter"] = 0

    data = treeToSparql(pdict, data)

    s = conversion_tools.convertToSparql(data)
    
    return s

def xtreeToSparql(tree, left_step="?root", varcounter = 0, end_var=None):

    triples = []

    if not tree.has_key("abspath"):
        # edge case, one node only
        locstep = tree["right_step"]["locstep"].asDict()
        varcounter += 1
        var = "?var"+str(varcounter)

        triples.append((left_step, getAxis(locstep["axis"]), var))
        triples.append((var, "rdf:val", locstep["node"]))
        left_step = var
        end_var = var

        if locstep.has_key("predicate"):
            (pred_triples, varcounter, dump_var) = treeToSparql(locstep["predicate"].asDict(), left_step=left_step, varcounter=varcounter)
            triples += pred_triples
    else:
        abspath = tree["abspath"].asDict()
        
        locstep = abspath["left_step"]["locstep"].asDict()
        varcounter += 1
        var = "?var"+str(varcounter)

        triples.append((left_step, getAxis(locstep["axis"]), var))
        triples.append((var, "rdf:val", locstep["node"]))
        left_step = var

        if locstep.has_key("predicate"):
            (pred_triples, varcounter, dump_var) = treeToSparql(locstep["predicate"].asDict(), left_step=left_step, varcounter=varcounter)
            triples += pred_triples

        if abspath.has_key("right_step"):
            locstep = abspath["right_step"]["locstep"].asDict()
            varcounter += 1
            var = "?var"+str(varcounter)

            triples.append((left_step, getAxis(locstep["axis"]), var))
            triples.append((var, "rdf:val", locstep["node"]))

            left_step = var
            end_var = var

            if locstep.has_key("predicate"):
                (pred_triples, varcounter, dump_var) = treeToSparql(locstep["predicate"].asDict(), left_step=left_step, varcounter=varcounter)
                triples += pred_triples
        else:
            (nest_triples, varcounter, end_var) = treeToSparql(abspath, left_step=left_step, varcounter=varcounter, end_var = var)
            triples += nest_triples

    return (triples, varcounter, end_var)

def treeToSparql(tree, data, left_step="?root"):

    if not tree.has_key("abspath"):
        # edge case, one node only
        locstep = tree["right_step"]["locstep"].asDict()
        data["varcounter"] += 1
        var = "?var"+str(data["varcounter"])

        data["triples"].append((left_step, getAxis(locstep["axis"]), var))
        data["triples"].append((var, "dada:label", locstep["node"]))
        left_step = var
        
        if locstep.has_key("predicate"):
            pred = locstep["predicate"].asDict()
            if pred.has_key("attr_test"):
                attr = pred["attr_test"]["attr"]
                attr_val = pred["attr_test"]["attr_val"]

                data["triples"].append((left_step, attr, attr_val))
            else:
                data = treeToSparql(pred, data, left_step=left_step)

        data["end_var"] = var
        
    else:
        abspath = tree["abspath"].asDict()
        
        locstep = abspath["left_step"]["locstep"].asDict()
        data["varcounter"] += 1
        var = "?var"+str(data["varcounter"])

        data["triples"].append((left_step, getAxis(locstep["axis"]), var))
        data["triples"].append((var, "dada:label", locstep["node"]))
        left_step = var

        if locstep.has_key("predicate"):
            pred = locstep["predicate"].asDict()
            if pred.has_key("attr_test"):
                attr = pred["attr_test"]["attr"]
                attr_val = pred["attr_test"]["attr_val"]

                data["triples"].append((left_step, attr, attr_val))
            else:
                data = treeToSparql(pred, data, left_step=left_step)

        data["end_var"] = var
            
        if abspath.has_key("right_step"):
            locstep = abspath["right_step"]["locstep"].asDict()
            data["varcounter"] += 1
            var = "?var"+str(data["varcounter"])

            data["triples"].append((left_step, getAxis(locstep["axis"]), var))
            data["triples"].append((var, "dada:label", locstep["node"]))

            left_step = var

            if locstep.has_key("predicate"):
                pred = locstep["predicate"].asDict()
                if pred.has_key("attr_test"):
                    attr = pred["attr_test"]["attr"]
                    attr_val = pred["attr_test"]["attr_val"]

                    data["triples"].append((left_step, attr, attr_val))
                else:
                    data = treeToSparql(pred, data, left_step=left_step)

            data["end_var"] = var
            
        else:
            data = treeToSparql(abspath, data, left_step=left_step)
            
    return data
        

def getAxis(axis):
    if axis == "//":
        axis_str = "descendant"
    elif axis == "/":
        axis_str = "dominates" #child
    elif axis == "//*":
        axis_str = "descendant_or_self"
    elif axis == "\\":
        axis_str = "parent"
    elif axis == "\\\\":
        axis_str = "ancestor"
    elif axis == "\\\\*":
        axis_str = "ancestor_or_self"
    elif axis == "->":
        axis_str = "immediate_following"
    elif axis == "-->":
        axis_str = "following"
    elif axis == "<-":
        axis_str = "immediate_preceding"
    elif axis == "<--":
        axis_str = "preceding"
    elif axis == "=>":
        axis_str = "immediate_following_sibling"
    elif axis == "==>":
        axis_str = "following_sibling"
    elif axis == "<=":
        axis_str = "immediate_preceding_sibling"
    elif axis == "<==":
        axis_str = "preceding_sibling"
    elif axis == ".":
        axis_str = "self"
    else:
        axis_str = "unknown_axis"

    return axis_str


def test():
    tests = [
        "//V->NP",
        "//cat",
        "//cat/dog",
        "//cat/dog->bird",
        "//cat[->fur/red]/dog",
        "//cat[/pogo->fish]\hedgehog<-pink",
        r"\\bird[=>lizard]"
        ]

    for t in tests:
        print '-'*8
        print "\nTest: " + t

        #debug(t)
        
        s = lpathToSparql(t)
        print s

def debug(exp):
    p = parser(exp)
    pretty_print(p)

def pretty_print(parsed, indent=0):
    
    d = parsed.asDict()
    for i in d:
        if type(d[i]) == ParseResults:
            print '\t'*indent + str(i) + ":"
            pretty_print(d[i], indent+1)
        else:
            print '\t'*indent + str(i) + ":" + str(d[i])
    
if __name__ == "__main__":
    #test()
    #lpathToSparql("//cat")
    pass

