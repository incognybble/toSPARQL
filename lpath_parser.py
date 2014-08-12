# Created: 13th June 2014

import re
from pyparsing import Word, alphas, Literal, Group, Optional, OneOrMore, Regex, ZeroOrMore, Forward

from pyparsing import ParseResults

import conversion_tools

def parser(text):
    var_any = Literal("_")
    p = Regex("[\w:]+").setResultsName("text")
    var_any = Regex("_") #handled by p anyway
    attribute = Literal("@").suppress()
    eq = Literal("=").suppress()
    closure = (Literal("?") | Literal("*") | Literal("+")).setResultsName("closure")

    test = Literal("^").setResultsName("modifier") + p | p + Literal("$").setResultsName("modifier") | p #| var_any
    axis = (Literal("\\\\*") | \
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
            Literal("<=")).setResultsName("connector")

    g_left_brack = Literal("[").suppress()
    g_right_brack = Literal("]").suppress()

    # working
    """
    abspath = Forward()
    locstep = Forward()
    
    node = test.setResultsName("node")
    attr_test = Group(attribute.suppress() + node.setResultsName("attr") + eq.suppress() + node.setResultsName("attr_val")).setResultsName("attr_test")
    predicate = (Group(Literal("[").suppress() + attr_test + Literal("]").suppress()).setResultsName("predicate") |\
                 Group(Literal("[").suppress() + abspath + Literal("]").suppress()).setResultsName("predicate"))
    locstep << Group(axis.setResultsName("axis") + node + \
              Optional(predicate + Optional(closure).setResultsName("closure"))).setResultsName("locstep")

    abs2 = abspath
    abspath << ( Group(locstep.setResultsName("left_step") + abs2).setResultsName("abspath") | \
                 locstep.setResultsName("right_step") )

    # TODO
    locpath = abspath
    fexpr = locpath.setResultsName("exp")
    """

    # clean
    locpath = Forward()

    attr_test = Group(attribute + p.setResultsName("attr") + eq + p.setResultsName("attr_val"))

    fexpr = locpath.setResultsName("exp")
    
    # axis as part of nodetest
    """
    nodetest = ( Group(axis.setResultsName("connector") + test.setResultsName("text") + g_left_brack + fexpr.setResultsName("predicate") + g_right_brack + Optional(closure)) | \
                 Group(axis.setResultsName("connector") + test.setResultsName("text") + g_left_brack + attr_test.setResultsName("attr_test") + g_right_brack ) | \
                 Group(axis.setResultsName("connector") + test.setResultsName("text")))
    locpath << ( Group(nodetest.setResultsName("left") + fexpr.setResultsName("right")) | \
                  nodetest)
    """
    
    pred_opt = (fexpr.setResultsName("predicate") | attr_test.setResultsName("attr_test"))
    nodetest = Group(test + Optional(g_left_brack + pred_opt + g_right_brack + Optional(closure)))
    locpath << ( Group( axis + nodetest.setResultsName("left") + fexpr.setResultsName("right")) | \
                 Group( axis + test + Optional(g_left_brack + pred_opt + g_right_brack + Optional(closure))) ) 
    
    return fexpr.parseString(text)

def lpathToSparql(lpath):
    p = parser(lpath)

    pdict = p.asDict()

    data = {}
    data["triples"] = []
    data["varcounter"] = 0
    data["extras"] = []

    data = treeToSparql(pdict, data)

    s = conversion_tools.convertToSparql(data)
    
    return s

def treeToSparql(tree, data, left_step=None):

    if not tree.has_key("abspath"):
        # edge case, one node only
        locstep = tree["right_step"]["locstep"].asDict()
        data["varcounter"] += 1
        var = "?var"+str(data["varcounter"])

        if left_step != None:
            #data["triples"].append((left_step, getAxis(locstep["axis"]), var))
            axisToTriples(locstep["axis"], data, left_step, var)
            
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

        if left_step != None:
            #data["triples"].append((left_step, getAxis(locstep["axis"]), var))
            axisToTriples(locstep["axis"], data, left_step, var)

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

            #data["triples"].append((left_step, getAxis(locstep["axis"]), var))
            axisToTriples(locstep["axis"], data, left_step, var)
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

def axisToTriples(axis, data, var_left, var_right):
    
    if axis == "/":
        
        data["varcounter"] += 1
        parent = data["varcounter"]
        data["varcounter"] += 1
        time1 = data["varcounter"]
        data["varcounter"] += 1
        time2 = data["varcounter"]
        data["varcounter"] += 1
        start1 = data["varcounter"]
        data["varcounter"] += 1
        start2 = data["varcounter"]
        data["varcounter"] += 1
        end1 = data["varcounter"]
        data["varcounter"] += 1
        end2 = data["varcounter"]

        data["triples"] += [(""+str(var_left), "dada:partof", "?var"+str(parent))]
        data["triples"] += [(""+str(var_right), "dada:partof", "?var"+str(parent))]
        data["triples"] += [(""+str(var_left), "dada:targets", "?var"+str(time1))]
        data["triples"] += [(""+str(var_right), "dada:targets", "?var"+str(time2))]
        data["triples"] += [("?var"+str(time1), "dada:start", "?var"+str(start1))]
        data["triples"] += [("?var"+str(time2), "dada:start", "?var"+str(start2))]
        data["triples"] += [("?var"+str(time1), "dada:end", "?var"+str(end1))]
        data["triples"] += [("?var"+str(time2), "dada:end", "?var"+str(end2))]

        data["extras"] += ["filter( " + "?var"+str(start2) + " >= " + "?var"+str(start1) + ")."]
        data["extras"] += ["filter( " + "?var"+str(end2) + " <= " + "?var"+str(end1) + ")."]

    elif axis == "->":
        
        data["varcounter"] += 1
        parent = data["varcounter"]
        data["varcounter"] += 1
        time1 = data["varcounter"]
        data["varcounter"] += 1
        time2 = data["varcounter"]
        data["varcounter"] += 1
        end = data["varcounter"]
        data["varcounter"] += 1
        start = data["varcounter"]

        data["triples"] += [(""+str(var_left), "dada:partof", "?var"+str(parent))]
        data["triples"] += [(""+str(var_right), "dada:partof", "?var"+str(parent))]
        data["triples"] += [(""+str(var_left), "dada:targets", "?var"+str(time1))]
        data["triples"] += [(""+str(var_right), "dada:targets", "?var"+str(time2))]
        data["triples"] += [("?var"+str(time1), "dada:end", "?var"+str(end))]
        data["triples"] += [("?var"+str(time2), "dada:start", "?var"+str(start))]

        data["extras"] += ["filter( " + "?var"+str(end) + " = " + "?var"+str(start) + ")."]
            
    else:
        data["triples"].append((var_left, getAxis(axis), var_right))

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
    conversion_tools.pretty_print(p)

    
if __name__ == "__main__":
    #test()
    #lpathToSparql("//cat")
    pass

