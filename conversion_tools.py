# Created: 27th June 2014
# conversion_tools.py

from SPARQLWrapper import SPARQLWrapper, JSON
import xml

from pyparsing import ParseResults
import pyalveo


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


    if data.has_key("not_triples"):
        not_trips = data["not_triples"]
        
        if len(not_trips) > 0:
            s = s + "\tFILTER NOT EXISTS {\n"

            for not_trip in not_trips:
                s = prettyTriple(s, not_trip, 2)
                
            s = s + "\t}\n"

    s = s + "}"

    if data.has_key("bindings"):
        bindings = data["bindings"]
        
        for binding in bindings:
            s = s + "BINDINGS " + binding + " {\n"
            for var_opt in bindings[binding]:
                s = s + "\t('"+var_opt+"')\n"
            s = s + "}"

    return s


def pyalveoQuery(s, limit=False):
    query = cleanQuery(s, limit)
    
    client = pyalveo.Client()
    results = client.sparql_query("mitcheldelbridge", query)
    
    return results["results"]["bindings"]

def cleanQuery(s, limit=False):
    query = """
        PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>
        PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX maus:<http://ns.ausnc.org.au/schemas/annotation/maus/>
        PREFIX md:<http://ns.ausnc.org.au/schemas/corpora/mitcheldelbridge/items>
        PREFIX xml:<http://www.w3.org/XML/1998/namespace>
        PREFIX dada:<http://purl.org/dada/schema/0.2#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX ausnc: <http://ns.ausnc.org.au/schemas/ausnc_md_model/>
        %s
    """%s

    if limit == True:
        query = query + "\tLIMIT 1"
    
    return query


def get_config(filename="config.xml"):
    dom = xml.dom.minidom.parse(filename)
    config = dom.getElementsByTagName("config")[0]

    server_text = (config.getElementsByTagName("server")[0]).firstChild.nodeValue
    db_text = (config.getElementsByTagName("db")[0]).firstChild.nodeValue
    url_text = (config.getElementsByTagName("url")[0]).firstChild.nodeValue
    path_text = (config.getElementsByTagName("path")[0]).firstChild.nodeValue
    location_text = (config.getElementsByTagName("location")[0]).firstChild.nodeValue

    data = {}
    data["server"] = server_text
    data["db"] = db_text
    data["url"] = url_text
    data["path"] = path_text
    data["location"] = location_text
    return data


def serverQuery(s, limit=False, config=None):
    query = cleanQuery(s, limit)

    if config == None:
        conf = get_config()
    else:
        conf = config
        
    sparql = SPARQLWrapper(conf["url"])

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    return results["results"]["bindings"]
