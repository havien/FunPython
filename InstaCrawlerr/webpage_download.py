# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from time import gmtime, strftime

#import robotparser
#import urllib2
import urllib.request

import traceback, re, sys, os
import time, datetime
import sqlite3
import ssl
import codecs

ssl._create_default_https_context = ssl._create_unverified_context

if __name__ == '__main__':
    print( "crap Instagram whole page crawler version 0.1" )

    inputURL = input( "please input crawling target Instagram Page URL: " )

    if len( inputURL ) == 0:
        raise SystemExit

    fileName = input( "please input you want file name: " )
    if 0 == len( fileName ):
        raise SystemExit

    print( "try begin do crawling" )
    time.sleep( 0.1 )
    print( "[" + inputURL + "]" )
    time.sleep( 0.1 )

    contents = contents = urllib.request.urlopen( inputURL )
    soup = BeautifulSoup( contents.read(), "html.parser" )
    findResult = soup.find( string = re.compile( "window._sharedData" ) )

    with open( fileName, 'w', encoding='utf-8' ) as fp:
        fp.write( str( findResult ) )
        fp.close()
    raise SystemExit