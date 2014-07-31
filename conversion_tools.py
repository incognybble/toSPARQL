# Created: 27th June 2014
# conversion_tools.py

from pyparsing import ParseResults

def pretty_print(parsed, indent=0):
    d = parsed.asDict()
    for i in d:
        if type(d[i]) == ParseResults:
            print '\t'*indent + str(i) + ":"
            pretty_print(d[i], indent+1)
        else:
            print '\t'*indent + str(i) + ":" + str(d[i])
            

def prettyTriple(s, triple, indent=1):
    if triple[2].startswith("?"):
        s = s + ("\t"*indent) + triple[0] + " " + triple[1] + " " + triple[2] + ".\n"
    elif triple[2].find(":") > -1:
        s = s + ("\t"*indent) + triple[0] + " " + triple[1] + " " + triple[2] + ".\n"
    else:
        s = s + ("\t"*indent) + triple[0] + " " + triple[1] + " '" + triple[2] + "'.\n"

    return s

def convertToSparql(data):
    s = "select "

    end_vars = data["end_var"]

    for end_var in end_vars:
        s = s + end_var + " "

    s = s + "\nwhere {\n"
    
    triples = data["triples"]
    for trip in triples:
        s = prettyTriple(s, trip)

    extras = data["extras"]
    for extra in extras:
        s = s + "\t" + extra + "\n"
    s = s + "}"

    if data.has_key("not_triples"):
        not_trips = data["not_triples"]
        
        if len(not_trips) > 0:
            s = s + "\tFILTER NOT EXISTS {\n"

            for not_trip in not_trips:
                s = prettyTriple(s, not_trip, 2)
                
            s = s + "\t}\n"

    if data.has_key("bindings"):
        bindings = data["bindings"]
        
        for binding in bindings:
            s = s + "BINDINGS " + binding + " {\n"
            for var_opt in bindings[binding]:
                s = s + "\t('"+var_opt+"')\n"
            s = s + "}"

    return s
