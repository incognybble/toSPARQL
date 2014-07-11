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
    g_text = Regex("[\w\s\:\#]+").setResultsName("text")
    g_string = Optional(g_quote) + g_text + Optional(g_quote)
    g_equ =  Literal("!=").setResultsName("connector") | Literal("=").setResultsName("connector")
    g_amp = Literal("&").setResultsName("connector")
    g_hat = Literal("^").setResultsName("connector")
    g_or = Literal("|").suppress()
    g_seq = Literal("->").setResultsName("connector")
    g_hash = Literal("#").setResultsName("hash")

    g_left_brack = Literal("[").suppress()
    g_right_brack = Literal("]").suppress()
    

    #g_val = g_string + Optional(g_or)
    #g_vals = OneOrMore(g_val)

    # use with or-suppress
    #g_val = g_or + g_string
    #g_vals = g_string + OneOrMore(g_val)


    g_vals = Forward()
    g_vals << g_string + ZeroOrMore(Group(g_or + g_vals).setResultsName("or_group"))

    #exp_basic = Optional(g_left_brack) + Group(Optional(g_hash) + g_string).setResultsName("left") + g_equ + Group(g_vals).setResultsName("right") + Optional(g_right_brack)
    exp_basic = Group(Optional(g_hash) + g_string).setResultsName("left") + g_equ + Group(g_vals).setResultsName("right")
    exp = Group(exp_basic)
    exp = exp.setResultsName("left") + g_amp + exp.setResultsName("right") | \
            exp.setResultsName("left") + g_hat + exp.setResultsName("right") | \
            exp.setResultsName("left") + g_seq + exp.setResultsName("right") | \
            exp_basic
    
    return exp.parseString(text)

def treeToSparql(tree, hashed, varcounter=0):
    triples = []
    #var_opts = []
    var_opt = None
    bindings = {}
    not_triples = []

    # handling for joined expression
    if len(tree["left"]) > 2:
        varcounter += 1
        var_left = varcounter
        (trips, hashed, bindings_left, not_trips) = treeToSparql(tree["left"], hashed, var_left)
        triples += trips
        not_triples += not_trips

        varcounter += 1
        var_right = varcounter
        (trips, hashed, bindings_right, not_trips) = treeToSparql(tree["right"], hashed, var_right)
        triples += trips
        not_triples += not_trips

        bindings = dict(bindings_left.items() + bindings_right.items())

        if tree["connector"] == "&":
            triples += [("?var"+str(var_left), getAxis(tree["connector"]), "?var"+str(var_right))]
        elif tree["connector"] == "->":
            triples += [("?var"+str(var_right), getAxis(tree["connector"]), "?var"+str(var_left))]
        elif tree["connector"] == "^":
            triples += [("?var"+str(var_left), getAxis(tree["connector"]), "?var"+str(var_right))]
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

    return (triples, hashed, bindings, not_triples)

def getAxis(axis):
    if axis == "->":
        axis_str = "emu:follows"
    elif axis == "^":
        axis_str = "emu:contains"
    elif axis == "=":
        axis_str = "maus:val"
    elif axis == "!=":
        axis_str = "maus:val"
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

def emuToSparql(emu):
    p = parser(emu)

    hashed = [False]
    (trips, hashed, bindings, not_trips) = treeToSparql(p, hashed)

    s = "select "
    for var in hashed[1:]:
        s = s + var + " "

    s = s + "\nwhere {\n"
    for trip in trips:
        s = conversion_tools.prettyTriple(s, trip)

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
             "#Word=C->Accent=Nuclear|a|r",
             "#Word!=C&Accent=Nuclear|a",
             "#Word!=C&Accent=Nuclear|a|'time space'",
             "#Word!=C|'hedge hog'|r&Accent=Nuclear|a|q",
             #"[Word=C]"
             "maus:orthography='#'"
             ]

    for t in tests:
        print "Test: " + t
        s = emuToSparql(t)

        print s
        print '='*8

if __name__ == "__main__":
    pass
