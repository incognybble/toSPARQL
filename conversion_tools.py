# Created: 27th June 2014
# conversion_tools.py

def prettyTriple(s, triple, indent=1):
    if triple[2].startswith("?"):
        s = s + ("\t"*indent) + triple[0] + " " + triple[1] + " " + triple[2] + ".\n"
    elif triple[2].find(":") > -1:
        s = s + ("\t"*indent) + triple[0] + " " + triple[1] + " " + triple[2] + ".\n"
    else:
        s = s + ("\t"*indent) + triple[0] + " " + triple[1] + " '" + triple[2] + "'.\n"

    return s

def convertToSparql(data):
    s = "select " + data["end_var"]

    s = s + "\nwhere {\n"
    triples = data["triples"]
    for trip in triples:
        s = prettyTriple(s, trip)
    s = s + "}"

    if data.has_key("not_trips"):
        not_trips = data["not_trips"]
        
        if len(not_trips) > 0:
            s = s + "\tFILTER NOT EXISTS {\n"

            for not_trip in not_trips:
                s = prettyTriple(s, not_trip, 2)
                
            s = s + "\t}\n"
                
        s = s + "}\n"

    if data.has_key("bindings"):
        bindings = data["bindings"]
        
        for binding in bindings:
            s = s + "BINDINGS " + binding + " {\n"
            for var_opt in bindings[binding]:
                s = s + "\t('"+var_opt+"')\n"
            s = s + "}"

    return s
