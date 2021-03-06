#!/usr/bin/python2.7

"""LODLinker, an RDF-SPARQL dataset simple linker"""

from SPARQLWrapper import SPARQLWrapper, JSON
from Levenshtein import ratio
import logging
import math
from LODLArgParser import LODLArgParser

class LODLinker:
    def __init__(self):
        self.ap = LODLArgParser()
        self.log = logging.getLogger("LODLinker")
        if self.ap.args.v == 1:
            logging.basicConfig(level=logging.INFO)
        self.doSPARQL()
        self.doLink()
    def doSPARQL(self):
        sparql = SPARQLWrapper(self.ap.args.e[0])
        sparql.setReturnFormat(JSON)
        sparql.setQuery("""
                        SELECT DISTINCT ?title ?s
                        FROM <""" + self.ap.args.g1[0] + """>
                        WHERE {
                        ?s <""" + self.ap.args.p1[0] + """> ?title .
                        }
                        """)
        self.log.info('Launching first SPARQL query...')
        self.resultsKnuttel = sparql.query().convert()
        self.log.info('First query done.')
        sparql.setQuery("""
                        SELECT DISTINCT ?title ?p
                        FROM <""" + self.ap.args.g2[0] + """> 
                        WHERE {
                        ?p <""" + self.ap.args.p2[0] + """> ?title .
                        }
                        """)
        self.log.info('Launching second SPARQL query...')
        self.resultsSTCN = sparql.query().convert()
        self.log.info('Second query done.')
    def doLink(self):
        self.log.info("Computing similarities...")
        print "@prefix owl: <http://www.w3.org/2002/07/owl#> ."
        for y in self.resultsKnuttel["results"]["bindings"]:
            max_r = 0
            knuttel_title = y["title"]["value"]
            knuttel_uri = y["s"]["value"]
            close_title = ""
            close_uri = ""
            for x in self.resultsSTCN["results"]["bindings"]:
                stcn_title = x["title"]["value"]
                stcn_uri = x["p"]["value"]
                r_title = ratio(knuttel_title,
                                stcn_title)
                if r_title > max_r:
                    max_r = r_title
                    close_title = stcn_title
                    close_uri = stcn_uri
            if max_r > self.ap.args.t[0]:
                print "<{}> owl:sameAs <{}> .".format(knuttel_uri, close_uri)

if __name__ == '__main__':
    lm = LODLinker()

__author__ = "Albert Meronyo-Penyuela"
__copyright__ = "Copyright 2013, VU University Amsterdam"
__credits__ = ["Albert Meronyo-Penyuela"]

__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Albert Meronyo-Penyuela"
__email__ = "albert.merono@vu.nl"
__status__ = "Prototype"
