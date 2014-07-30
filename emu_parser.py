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
    

    data = treeToSparql(pdict, data)

    data["end_var"] = data["hashed"][1]
    
    #print data
    s = conversion_tools.convertToSparql(data)
    
    return s

def treeToSparql(tree, data):
    exp = tree["exp"]

    if len(exp["left"]) > 2:
        data = treeToSparql(exp["left"], data)

    if exp["connector"] == "=":
        data["varcounter"] += 1
        var_left = data["varcounter"]
        
        data["triples"] += [("?var"+str(var_left), getAxis("type"), exp["left"].text)]
        data["triples"] += [("?var"+str(var_left), getAxis(exp["connector"]), exp["right"].text)]

        if len(exp["left"].hash)>0:
            if data["hashed"][0] == False:
                data["hashed"][0] = True
            data["hashed"].append(exp["left"].text)
        else:
            if data["hashed"][0] == False:
                data["hashed"].append(exp["left"].text)
        
    return data

def xtreeToSparql(tree, hashed, varcounter=0):
    triples = []
    #var_opts = []
    var_opt = None
    bindings = {}
    not_triples = []
    extras = []

    # handling for joined expression
    if len(tree["left"]) > 2:
        varcounter += 1
        var_left = varcounter
        (trips, hashed, bindings_left, not_trips, extra) = treeToSparql(tree["left"], hashed, var_left)
        triples += trips
        not_triples += not_trips
        extras += extra

        varcounter += 1
        var_right = varcounter
        (trips, hashed, bindings_right, not_trips, extra) = treeToSparql(tree["right"], hashed, var_right)
        triples += trips
        not_triples += not_trips
        extras += extra

        bindings = dict(bindings_left.items() + bindings_right.items())

        if tree["connector"] == "&":
            triples += [("?var"+str(var_left), getAxis(tree["connector"]), "?var"+str(var_right))]
        elif tree["connector"] == "->":
            #triples += [("?var"+str(var_right), getAxis(tree["connector"]), "?var"+str(var_left))]

            varcounter += 1
            parent = varcounter
            varcounter += 1
            time1 = varcounter
            varcounter += 1
            time2 = varcounter
            varcounter += 1
            end = varcounter
            varcounter += 1
            start = varcounter

            triples += [("?var"+str(var_left), "dada:partof", "?var"+str(parent))]
            triples += [("?var"+str(var_right), "dada:partof", "?var"+str(parent))]
            triples += [("?var"+str(var_left), "dada:targets", "?var"+str(time1))]
            triples += [("?var"+str(var_right), "dada:targets", "?var"+str(time2))]
            triples += [("?var"+str(time1), "dada:end", "?var"+str(end))]
            triples += [("?var"+str(time2), "dada:start", "?var"+str(start))]

            extras += ["filter( " + "?var"+str(end) + " = " + "?var"+str(start) + ")."]
            
        elif tree["connector"] == "^":
            #triples += [("?var"+str(var_left), getAxis(tree["connector"]), "?var"+str(var_right))]

            varcounter += 1
            parent = varcounter
            varcounter += 1
            time1 = varcounter
            varcounter += 1
            time2 = varcounter
            varcounter += 1
            start1 = varcounter
            varcounter += 1
            start2 = varcounter
            varcounter += 1
            end1 = varcounter
            varcounter += 1
            end2 = varcounter

            triples += [("?var"+str(var_left), "dada:partof", "?var"+str(parent))]
            triples += [("?var"+str(var_right), "dada:partof", "?var"+str(parent))]
            triples += [("?var"+str(var_left), "dada:targets", "?var"+str(time1))]
            triples += [("?var"+str(var_right), "dada:targets", "?var"+str(time2))]
            triples += [("?var"+str(time1), "dada:start", "?var"+str(start1))]
            triples += [("?var"+str(time2), "dada:start", "?var"+str(start2))]
            triples += [("?var"+str(time1), "dada:end", "?var"+str(end1))]
            triples += [("?var"+str(time2), "dada:end", "?var"+str(end2))]

            extras += ["filter( " + "?var"+str(start2) + " >= " + "?var"+str(start1) + ")."]
            extras += ["filter( " + "?var"+str(end2) + " <= " + "?var"+str(end1) + ")."]
        else:
            raise Exception("Unhandled 2nd level connector " + tree["connector"])

    # handling for basic expression
    if tree["connector"][-1] == "=":
        
        var = "?var"+str(varcounter)

        # in ParseResult, if key doesn't exist, it just returns a blank
        if tree.left.hash == "#":
            if hashed[0] == True:
                hashed.append(var)
            else:
                del hashed
                hashed = [True]
                hashed.append(var)
        else:
            if hashed[0] == False:
                hashed.append(var)


        triples.append((var, getAxis("type"), tree.left.text))

        if len(tree["right"]) > 1:
            #or_group case
            
            #be caseful of usage here as lists pass by reference
            var_opts = get_ors(tree.right, [])

            varcounter += 1
            var_opt = "?var"+str(varcounter)
            
            if tree["connector"] == "=":
                triples.append((var, getAxis(tree["connector"]), var_opt))
            elif tree["connector"] == "!=":
                not_triples.append((var, getAxis(tree["connector"]), var_opt))
            else:
                raise Exception("Unrecognised = connector " + tree["connector"])
                
            bindings[var_opt] = var_opts
        else:
            if tree["connector"] == "=":
                triples.append((var, getAxis(tree["connector"]), tree.right.text))
            elif tree["connector"] == "!=":
                not_triples.append((var, getAxis(tree["connector"]), tree.right.text))
            else:
                raise Exception("Unrecognised = connector " + tree["connector"])

    return (triples, hashed, bindings, not_triples, extras)

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

def xemuToSparql(emu):
    p = parser(emu)

    hashed = [False]
    (trips, hashed, bindings, not_trips, extras) = treeToSparql(p, hashed)

    s = "select "
    for var in hashed[1:]:
        s = s + var + " "

    s = s + "\nwhere {\n"
    for trip in trips:
        s = conversion_tools.prettyTriple(s, trip)

    for extra in extras:
        s = s + "\t" + extra + "\n"

    if len(not_trips) > 0:
        s = s + "\tFILTER NOT EXISTS {\n"

        for not_trip in not_trips:
            s = conversion_tools.prettyTriple(s, not_trip, 2)
            
        s = s + "\t}\n"
            
    s = s + "}\n"
    
    for binding in bindings:
        s = s + "BINDINGS " + binding + " {\n"
        for var_opt in bindings[binding]:
            s = s + "\t('"+var_opt+"')\n"
        s = s + "}"

    return s

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
