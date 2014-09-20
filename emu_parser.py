import re
from pyparsing import Word, alphas, Literal, Group, Optional, OneOrMore, Regex, ZeroOrMore, Forward

import conversion_tools

def parser(text):
    """
    str := \w+
    str := '\w+'
    exp := Var=str
    exp := exp & exp
    exp := exp ^ exp
    """
    
    # grammar
    #g_string = "'"+Word(alphas)+"'" | Word(alphas)
    g_quote = Literal("'").suppress()
    g_text = Regex("[\w\s\:\#\.]+").setResultsName("text")
    g_string = Optional(g_quote) + g_text + Optional(g_quote)
    g_equ =  Literal("!=").setResultsName("connector") | Literal("=").setResultsName("connector")
    g_amp = Literal("&").setResultsName("connector")
    g_hat = Literal("^").setResultsName("connector")
    g_or = Literal("|").suppress()
    g_seq = Literal("->").setResultsName("connector")
    g_hash = Literal("#").setResultsName("hash")

    g_left_brack = Literal("[").suppress()
    g_right_brack = Literal("]").suppress()

    
    g_vals = Forward()
    g_vals << g_string + ZeroOrMore(Group(g_or + g_vals).setResultsName("or_group"))

    # working
    """
    exp_basic = Group(Optional(g_hash) + g_string).setResultsName("left") + g_equ + Group(g_vals).setResultsName("right")
    exp = Group(exp_basic)
    exp = exp.setResultsName("left") + g_amp + exp.setResultsName("right") | \
            g_left_brack + exp.setResultsName("left") + g_hat + exp.setResultsName("right") + g_right_brack | \
            g_left_brack + exp.setResultsName("left") + g_seq + exp.setResultsName("right") + g_right_brack | \
            exp_basic
    """

    # recursion
    simpleq = Forward()
    complexq = Forward()

    exp = (simpleq | complexq).setResultsName("exp")
    exp_basic = Group(Group(Optional(g_hash) + g_string).setResultsName("left") + g_equ + Group(g_vals).setResultsName("right"))
    simpleq << (Group(exp_basic.setResultsName("left") + g_amp + simpleq.setResultsName("right")) | exp_basic)
    complexq << ( Group(g_left_brack + exp.setResultsName("left") + g_hat + exp.setResultsName("right") + g_right_brack) | \
                  Group(g_left_brack + exp.setResultsName("left") + g_seq + exp.setResultsName("right") + g_right_brack) )
    
    
    
    return exp.parseString(text)

def emuToSparql(emu):
    p = parser(emu)

    pdict = p.asDict()

    data = {}
    data["triples"] = []
    data["varcounter"] = 0
    data["extras"] = []
    
    data["hashed"] = [False]
    data["var_opt"] = None
    data["bindings"] = {}
    data["not_triples"] = []
    

    data = treeToSparql(pdict["exp"], data)

    data["end_var"] = set(data["hashed"][1:])
    
    #print data
    s = conversion_tools.convertToSparql(data)
    
    return s

def treeToSparql(tree, data, var=None):
    
    if len(tree["left"]) > 2:
        if var == None:
            data["varcounter"] += 1
            left_var = "?var"+str(data["varcounter"])
        else:
            left_var=var
            
        data = treeToSparql(tree["left"], data, left_var)

        if tree["connector"] != "&":
            data["varcounter"] += 1
            right_var = "?var"+str(data["varcounter"])
        else:
            right_var = left_var
            
        data = treeToSparql(tree["right"], data, right_var)

        if tree["connector"] != "&":
            axisToTriples(tree["connector"], data, left_var, right_var)

    else:
        
        if var == None:
            data["varcounter"] += 1
            var = "?var"+str(data["varcounter"])


        if len(tree["right"]) > 1:
            #or_group case
            
            #be careful of usage here as lists pass by reference
            var_opts = get_ors(tree["right"], [])

            data["varcounter"] += 1
            var_opt = "?var"+str(data["varcounter"])
            
            if tree["connector"] == "=":
                data["triples"] += [(var, getAxis(tree["connector"]), var_opt)]
            elif tree["connector"] == "!=":
                data["not_triples"] += [(var, getAxis(tree["connector"]), var_opt)]
            else:
                raise Exception("Unrecognised = connector " + tree["connector"])
                
            data["bindings"][var_opt] = var_opts

        else:

            if tree["right"]["text"].find(":") > -1:
                if tree["connector"] == "=":
                    data["triples"] += [(var, tree["left"].text, tree["right"].text)]
                elif tree["connector"] == "!=":
                    data["not_triples"] += [(var, tree["left"].text, tree["right"].text)]
                else:
                    raise Exception("Unrecognised connector " + tree["connector"])

            else:
                if tree["connector"] == "=":
                    data["triples"] += [(var, getAxis("type"), tree["left"].text)]
                    data["triples"] += [(var, getAxis(tree["connector"]), tree["right"].text)]
                elif tree["connector"] == "!=":
                    # it's still of this type
                    data["triples"] += [(var, getAxis("type"), tree["left"].text)]
                    # just not of this value
                    data["not_triples"] += [(var, getAxis(tree["connector"]), tree["right"].text)]
                else:
                    raise Exception("Unrecognised connector " + tree["connector"])


        if len(tree["left"].hash)>0:
            if data["hashed"][0] == False:
                # if the list previously stored non-hashed variables,
                # and now is for hashed only, clear out the non-hashed variables
                del data["hashed"]
                data["hashed"] = [True]
            data["hashed"].append(var)
        else:
            if data["hashed"][0] == False:
                data["hashed"].append(var)
        
    return data

def axisToTriples(axis, data, var_left, var_right):

    if axis == "^":
        
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
    if axis == "->":
        axis_str = "emu:follows"
    elif axis == "^":
        axis_str = "emu:contains"
    elif axis == "=":
        axis_str = "dada:label"
    elif axis == "!=":
        axis_str = "dada:label"
    elif axis == "&":
        axis_str = "owl:sameAs"
    elif axis == "type":
        axis_str = "dada:type"
    else:
        axis_str = "unknown_axis"
        
    return axis_str


def get_ors(tree, ors):
    ors.append(tree.text)

    if tree.or_group != "":
        # this assigning isn't necessary since lists pass by reference
        ors = get_ors(tree.or_group, ors)

    # this return isn't necessary, since lists pass by reference
    # it is only here for consistency
    return ors

def test():
    tests = [
             "Word=C",
             "Word!='C'",
             "Word!=C",
             "#Word=C",
             "Accent=Nuclear|a|r",
             "Word=C&Accent=Nuclear",
             "[#Word=C->Accent=Nuclear|a|r]",
             "#Word!=C&Accent=Nuclear|a",
             "#Word!=C&Accent=Nuclear|a|'time space'",
             "#Word!=C|'hedge hog'|r&Accent=Nuclear|a|q",
             #"[Word=C]"
             "maus:orthography='#'",
             "[maus:orthography='time'^maus:phonetic='t']",
             "[maus:phonetic='t'->maus:phonetic='Ae']"
             ]

    for t in tests:
        print "Test: " + t
        s = emuToSparql(t)

        print s
        print '='*8

if __name__ == "__main__":
    pass
