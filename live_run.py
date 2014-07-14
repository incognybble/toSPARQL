from emu_parser import emuToSparql

import pyalveo

if __name__ == "__main__" :
    s = emuToSparql("maus:orthography='time'^maus:phonetic='t'")
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
        LIMIT 5
    """%s

    query1 = """
        PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>
        PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX maus:<http://ns.ausnc.org.au/schemas/annotation/maus/>
        PREFIX md:<http://ns.ausnc.org.au/schemas/corpora/mitcheldelbridge/items>
        PREFIX xml:<http://www.w3.org/XML/1998/namespace>
        PREFIX dada:<http://purl.org/dada/schema/0.2#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX ausnc: <http://ns.ausnc.org.au/schemas/ausnc_md_model/>
        select ?var1  ?var2 ?start1 ?start2 ?end1 ?end2
        where {
        ?var1 dada:type maus:orthography.
        ?var1 dada:label 'time'.
        ?var2 dada:type maus:phonetic.
        ?var2 dada:label 't'.
        ?var1 dada:targets ?time1.
        ?var2 dada:targets ?time2.
        ?time1 dada:start ?start1.
        ?time2 dada:start ?start2.
        ?time1 dada:end ?end1.
        ?time2 dada:end ?end2.
        filter( ?start2 >= ?start1 ).
        filter( ?end2 <= ?end1 ).
        }
        LIMIT 10
    """
    # ?var1 emu:contains ?var2.
    # ?var2 dada:start '5.02'^^xsd:float.
    # filter( ?number < 50.0 )


    print query
    
    client = pyalveo.Client()
    results = client.sparql_query("mitcheldelbridge", query)
    
    for result in results["results"]["bindings"]:
        #print result["var0"]["value"]
        for r in result:
            print str(r) + ": " + result[r]["value"]
        print ''
            

