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
    steps = Forward()

    fexpr = locpath.setResultsName("exp")

    attr_test = Group(attribute + p.setResultsName("attr") + eq + p.setResultsName("attr_val"))
    pred_opt = (fexpr.setResultsName("predicate") | attr_test.setResultsName("attr_test"))

    # connector order handling is the same as EmuQL, but the root lacks a left, as it refers to context node
    nodetest = Group(test + Optional(g_left_brack + pred_opt + g_right_brack + Optional(closure)))
    steps << ( Group(nodetest("left") + axis + steps("right")) | \
               Group(test + Optional(g_left_brack + pred_opt + g_right_brack + Optional(closure))))

    locpath << Group(axis + steps.setResultsName("right"))
    
    return fexpr.parseString(text)

def lpathToSparql(lpath):
    p = parser(lpath)

    pdict = p.asDict()

    data = {}
    data["triples"] = []
    data["varcounter"] = 0
    data["extras"] = []
    data["end_var"] = [None]

    data = treeToSparql(pdict["exp"].asDict(), data)

    s = conversion_tools.convertToSparql(data)
    
    return s

def treeToSparql(tree, data, left_step=None):

    node = tree["right"].asDict()

    data["varcounter"] += 1
    var = "?var"+str(data["varcounter"])

    # if context is available, make sure to connect the current node to it
    if left_step != None:
        axisToTriples(tree["connector"], data, left_step, var)


    if node.has_key("text"):
        # if reached right leaf node
        # add right leaf
        if node["text"] != "_":
            data["triples"].append((var, "dada:label", node["text"]))

        # square bracket handling
        if node.has_key("predicate"):
            pred = node["predicate"].asDict()
            data = treeToSparql(pred, data, left_step=var)
        elif node.has_key("attr_test"):
            attr = node["attr_test"]["attr"]
            attr_val = node["attr_test"]["attr_val"]
            data["triples"].append((var, attr, attr_val))
        
        data["end_var"][0] = var
        
    else:
        # still recursion to go!
        # add left leaf
        left = node["left"].asDict()
        if left["text"] != "_":
            data["triples"].append((var, "dada:label", left["text"]))

        # square bracket handling
        if left.has_key("predicate"):
            pred = left["predicate"].asDict()
            data = treeToSparql(pred, data, left_step=var)
        elif left.has_key("attr_test"):
            attr = left["attr_test"]["attr"]
            attr_val = left["attr_test"]["attr_val"]
            data["triples"].append((var, attr, attr_val))

        # recurse!
        data = treeToSparql(node, data, left_step=var)


    return data


def axisToTriples(axis, data, var_left, var_right):
    #data["triples"].append((var_left, getAxis(axis), var_right))
    
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

