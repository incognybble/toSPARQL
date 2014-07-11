from emu_parser import emuToSparql

import pyalveo

if __name__ == "__main__" :
    s = emuToSparql("md:orthography='#'")
    query = """
        PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>
        PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX maus:<http://ns.ausnc.org.au/schemas/annotation/maus/>
        PREFIX md:<http://ns.ausnc.org.au/schemas/corpora/mitcheldelbridge/items>
        PREFIX xml:<http://www.w3.org/XML/1998/namespace>
        PREFIX dada:<http://purl.org/dada/schema/0.2#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#> 
        %s
        LIMIT 5
    """%s

    query = """
    PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>
    PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX maus:<http://ns.ausnc.org.au/schemas/annotation/maus/>
    PREFIX md:<http://ns.ausnc.org.au/corpora/mitcheldelbridge/items/>
    PREFIX xml:<http://www.w3.org/XML/1998/namespace>
    PREFIX dada:<http://purl.org/dada/schema/0.2#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX ausnc: <http://ns.ausnc.org.au/schemas/ausnc_md_model/>
    select ?var0 ?var1
    where {?var0 ausnc:date_of_recording ?var1}
    limit 5
    """
    # md:S1217s1
    
    client = pyalveo.Client()
    results = client.sparql_query("mitcheldelbridge", query)
    print query
    for result in results["results"]["bindings"]:
        print result["var0"]["value"] + " " + result["var1"]["value"]
