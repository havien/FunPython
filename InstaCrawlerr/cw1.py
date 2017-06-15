"""
내가 제일 좋아하는 시바견 마메스케(豆助) 'instagram.com/mamesuke0318' 의 인스타그램의 사진과 비디오를 간직하기 위해 만듬
"""

# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from time import gmtime, strftime


import urllib.request
import traceback, re
import sys, os, platform
import time, datetime
import sqlite3
import ssl
import codecs
#import platform

#ssl._create_default_https_context = ssl._create_unverified_context

context = ssl._create_unverified_context()

crawlerName = "crawFirst_instagram"
mainURL = "https://www.instagram.com/"
directURL = mainURL + "p/"

instaID = ""
instaURL = ""
nextInstaMaxID = ""

wantTagPosition = 15
curMaxID = ""
nextMaxIDEndPosition = 0
terminate = False

totalInstaPageCount = 0
totalSavedPhotoCount = 0
totalSavedVideoCount = 0

lastCrawlingCode = ""
pageFirstInstaCode = ""

def PrintLocalTimeNow():
    print("[current time : " + str( strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "]" )

def FindOutOS():
    systemName = platform.system()
    #platform.release()

    return systemName

    """
    if systemName == "linux" or systemName == "linux2":
        return "linux"
    elif systemName == "Darwin":
        return "macOS"
    elif systemName == "Windows" 
    # Windows
    """

def DownloadFileOnmacOS( fileURL, wishFileName, extension ):
    cmd = "curl \"" + fileURL + "\" -o " + wishFileName + "." + extension 
    os.system( cmd )

def DownloadFileLinux( fileURL, wishFileName, extension ):
    cmd = "wget \"" + fileURL #+ "\" -o " + wishFileName + "." + extension 
    os.system( cmd )

def DownloadFile( fileURL, wishFileName, extension ):
    if "Linux" == FindOutOS():
        DownloadFileLinux( fileURL, wishFileName, extension )
    elif "Darwin" == FindOutOS():
        DownloadFileOnmacOS( fileURL, wishFileName, extension )
    elif "Windows" == FindOutOS():
        DownloadFileOnmacOS( fileURL, wishFileName, extension )

def DownloadVideoFile( pageURL, wishFileName ):
    videocontents = urllib.request.urlopen( pageURL, context = context )
    videosoup = BeautifulSoup( videocontents.read(), "html.parser" )

    videoFileTag = videosoup.find( "meta", property = "og:video" )
    if None != type( videoFileTag ):
        DownloadFile( videoFileTag["content"], wishFileName, "mp4" )


def getContent( url, delay = 5 ):
    #"Download Web Page.."
    print( url + '\n' )

    try:
        """opener = urllib.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4')]*/"""
        contents = urllib.request.urlopen( url ).read()
    except:
        traceback.print_exc()
        return None
    
    return contents

def searchNextMaxID2( firstPos, urlString ):
    lastPos = (firstPos+65)

    tempCurMaxID = ""

    nextMaxID = urlString.find( "\"GraphSidecar\", \"id\"", firstPos, lastPos )
    nextMaxIDEndPosition = urlString.find( "\"", nextMaxID+23, (nextMaxID+23+20) )
    tempCurMaxID = urlString[nextMaxID+23:nextMaxIDEndPosition]

    if -1 != nextMaxID:
        return tempCurMaxID


    nextMaxID = urlString.find( "\"GraphImage\", \"id\"", firstPos, lastPos )
    nextMaxIDEndPosition = urlString.find( "\"", nextMaxID+21, (nextMaxID+21+20) )
    tempCurMaxID = urlString[nextMaxID+21:nextMaxIDEndPosition]

    if -1 != nextMaxID:
        return tempCurMaxID


    nextMaxID = urlString.find( "\"GraphVideo\", \"id\"", firstPos, lastPos )
    nextMaxIDEndPosition = urlString.find( "\"", nextMaxID+21, (nextMaxID+21+20) )
    tempCurMaxID = urlString[nextMaxID+21:nextMaxIDEndPosition]

    if -1 != nextMaxID:
        return tempCurMaxID

    return ""


def searchNextMaxID( lastSearchPos, urlString, depth ):
    #find next max_id = next instagram page!
    # HTML Source = {"__typename": "GraphSidecar", "id": "1526488312511364573"

    abcdefg = ""
    curMinusPos = 300

    while curMinusPos <= 1000:
        abcdefg = searchNextMaxID2( (lastSearchPos-curMinusPos), urlString )
        if len( abcdefg ) > 5:
            break

        curMinusPos += 20
    
    return abcdefg


def IsPhotoSidecar( urlString, startPosition ):
    startIndex = urlString.find( "GraphSidecar", startPosition-670, startPosition )

    if -1 != startIndex:
        return True
    else:
        return False

    #return urlString[(jpgFindIndex+16):(jpdEndIndex+4)]

def DetermineInstaPhotoURL( urlString, startPosition ):
    jpgFindIndex = urlString.find( "\"display_src\": \"", startPosition )
    jpgEndIndex = urlString.find( ".jpg", jpgFindIndex+1 )

    if -1 != jpgFindIndex and -1 != jpgEndIndex:
        return urlString[(jpgFindIndex+16):(jpgEndIndex+4)]
    else:
        return ""

def DetermineInstaMultiPhotoURL( urlString, startPosition ):
    jpgFindIndex = urlString.find( "\"display_url\": \"", startPosition )
    jpgEndIndex = urlString.find( ".jpg", jpgFindIndex+1 )

    if -1 != jpgFindIndex and -1 != jpgEndIndex:
        return urlString[(jpgFindIndex+16):(jpgEndIndex+4)]
    else:
        return ""

def DetermineInstaPhotosVideoURL( urlString, startPosition ):
    FindIndex = urlString.find( "\"video_url\": \"", startPosition )
    EndIndex = urlString.find( ".mp4", jpgFindIndex+1 )

    if -1 != FindIndex and -1 != EndIndex:
        return urlString[(FindIndex+14):(EndIndex+4)]
    else:
        return ""

def DetermineInstaPhotoTakenTime( urlString ):
    startIndex = urlString.find( "\"taken_at_timestamp\": \"", 5000 )
    if -1 == startIndex:
        return ""

    endIndex = urlString.find( ",", startIndex+1 )

    #print( startIndex )
    #print( endIndex )

    return urlString[(startIndex):(endIndex+10)]
    

class InstagramInfo:
    code = ""
    photoURL = ""
    isVideo = False
    isSideCar = False

    def __init__(self, code, url, isVideo, isSideCar ):
        self.code = code
        self.url = url
        self.isVideo = isVideo
        self.isSideCar = isSideCar

if __name__ == '__main__':
    print( "crap Instagram crawler version 0.1" )

    instaID = input( "please input crawling target Instagram ID: " )

    if len( instaID ) == 0:
        instaID = "mamesuke0318"

    saveDir = input( "please input save directory: " )

    if len( saveDir ) == 0:
        saveDir = "/Users/jiyeolpyo/Downloads/Instagram/"

    startTime = datetime.datetime.now().replace( microsecond=0 )
    PrintLocalTimeNow()

    dbcon = sqlite3.connect( "InstagramInfo.db" )
    dbcon.isolation_level = None
    dbcursor = dbcon.cursor()

    dbcursor.execute( "CREATE TABLE IF NOT EXISTS tb_latest_code( id varchar(64), code varchar(30) )" )
    dbcursor.execute( "SELECT id FROM tb_latest_code WHERE id = :id", {"id": instaID})

    row = dbcursor.fetchone()
    if row is None:
        dbcursor.execute( "INSERT INTO tb_latest_code( id ) VALUES ( :id )", {"id": instaID} )

    dbcursor.execute( "SELECT code FROM tb_latest_code WHERE id = :Id", {"Id": instaID} )
    latestWorkCode = dbcursor.fetchone()[0]

    isSavedFirstPageCode = False


    while True:
        if True == terminate:
            dbcursor.execute( "UPDATE tb_latest_code SET code = :code WHERE id = :id",
                              {"id": instaID, "code": pageFirstInstaCode} )

            print( "pageFirstInstaCode : " + pageFirstInstaCode )

            print( "no more instagram page! end work!" )

            endTime = datetime.datetime.now().replace(microsecond=0)
            PrintLocalTimeNow()

            print( "working time: " + str(endTime - startTime) )
            print( "total instagram page count : " + str( len( instagramPhotos ) ) )
            print( "total saved photo count: " + str( totalSavedPhotoCount ) )
            print( "total saved video count: " + str( totalSavedVideoCount ) )

            break

        if 0 == len( nextInstaMaxID ):
            instaURL = mainURL + instaID
        else:
            instaURL = mainURL + instaID + "/?max_id=" + nextInstaMaxID
        
        time.sleep( 0.3 )

        print( "try begin do crawling" )
        print( "[" + instaURL + "]" )
        time.sleep( 0.1 )

        #instaURL = "https://www.instagram.com/mamesuke0318/?max_id=1513469714222072146"

        try:
            contents = contents = urllib.request.urlopen( instaURL, context=context )
            soup = BeautifulSoup( contents.read(), "html.parser" )

            findResult = soup.find( string = re.compile( "window._sharedData" ) )

            thirdExtensionLen = 4
            codeStringLen = 6+3 # "code" + ": \"""

            photoCountOf1Page = 12

            findIndex = 0
            prevFindIndex = 0
            videofindIndex = 0
            jpgFindIndex = 0
            instaCodeStartPos = 0

            instagramPhotos = set()
            nextMaxID = 0

            isVideo = False

            if -1 == findIndex:
                break

            while -1 != findIndex:
                """
                with open( 'body.txt', 'w', encoding='utf-8' ) as fp:
                    fp.write( str( findResult ) )
                    fp.close()
                raise SystemExit
                """

                ## find individual instagram photo's URL code.
                findIndex = findResult.find( "\"code\"", findIndex+1 )
                
                nextInstaMaxID = ""

                if -1 == findIndex:
                    nextInstaMaxID = searchNextMaxID( prevFindIndex, findResult, 1 )

                    if 5 > len( nextInstaMaxID ):
                        nextInstaMaxID = searchNextMaxID( prevFindIndex, findResult, 2 )
                            
                        if 5 > len( nextInstaMaxID ):
                            nextInstaMaxID = searchNextMaxID( prevFindIndex, findResult, 3 )

                    if 5 > len( nextInstaMaxID ):
                        lastCrawlingCode = instaCode
                        terminate = True

                    break
                
                prevFindIndex = findIndex
                codeEndIndex = findResult.find( "\",", findIndex+codeStringLen )

                instaCode = findResult[(findIndex+codeStringLen):codeEndIndex]

                if False == isSavedFirstPageCode:
                    pageFirstInstaCode = instaCode
                    isSavedFirstPageCode = True

                if latestWorkCode == instaCode:
                    print( "this instagram page(" + instaCode + ") already crawling" )
                    terminate = True
                    break

                startFindVideoPosition = (findIndex-20)
                endFindVideoPosition = (startFindVideoPosition+50)

                isVideo = False
                videofindIndex = findResult.find( "\"is_video\": true", startFindVideoPosition, endFindVideoPosition )

                ## is video ?
                if -1 != videofindIndex:
                    isVideo = True

                # is photo Sidecar? (multi-photo)
                isSideCar = IsPhotoSidecar( findResult, findIndex )

                # instaCode save
                if 1 >= len( instaCode ):
                    print( "find code error!!!!" + instaCode )

                #print( DetermineInstaPhotoTakenTime( findResult ) )
                photoURL = DetermineInstaPhotoURL( findResult, (findIndex+1) )

                newInstagram = InstagramInfo( instaCode, photoURL, isVideo, isSideCar )
                instagramPhotos.add( newInstagram )

                #for instaCode in videoCodes:
                    #print( instaCode + "\n" )

            if 0 < len( instagramPhotos ):
                fullsaveDir = saveDir + instaID
                
                if False == os.path.exists( saveDir ):
                    os.mkdir( saveDir )
                
                os.chdir( saveDir )

                if False == os.path.exists( instaID ):
                    print( "try create to instagram identifier directory [" + instaID + "]" )
                    os.mkdir( instaID )
                    #print( "instagram identifier directory [" + instaID + "] is already exists!" )

                listDir = os.listdir( instaID )
                numberOfFiles = len( listDir )

                for eachInstaPhoto in instagramPhotos:
                    numberOfFiles += 1

                    # normal photo.
                    if False == eachInstaPhoto.isSideCar and False == eachInstaPhoto.isVideo:
                        DownloadFile( eachInstaPhoto.url, instaID + "/" + str( numberOfFiles ), "jpg" )

                    # multi-photo page's photo download.
                    if True == eachInstaPhoto.isSideCar:
                        instaPageURL = directURL + eachInstaPhoto.code
                        print( "try crawling instagram multi-photo! directURL: [" + instaPageURL + "]" )

                        time.sleep( 0.2 )

                        pContents = urllib.request.urlopen( instaPageURL, context=context )
                        pSoup = BeautifulSoup( pContents.read(), "html.parser" )

                        findResult = pSoup.find( string = re.compile( "window._sharedData" ) )
                        pFindIndex = 1000

                        multiNumber = 1
                        multiPhotos = set()
                        multiVideos = set()

                        while True:
                            photoURL = DetermineInstaMultiPhotoURL( findResult, (pFindIndex+1) )
                            if "" == photoURL:
                                break

                            videoURL = DetermineInstaPhotosVideoURL( findResult, (pFindIndex + 1) )

                            if "" != videoURL:
                                multiVideos.add( videoURL )

                            pFindIndex += 300
                            multiPhotos.add( photoURL )

                        for eachPhotoURL in multiPhotos:
                            multiPhotoFileName = instaID + "/" + str( numberOfFiles ) + "_" + str( multiNumber )
                            DownloadFile( eachPhotoURL, multiPhotoFileName, "jpg" )

                            multiNumber += 1
                            totalSavedPhotoCount += 1
                            time.sleep( 0.1 )

                        for eachVideoURL in multiVideos:
                            multivideoFileName = instaID + "/" + str( numberOfFiles ) + "_" + str( multiNumber )
                            DownloadFile( eachVideoURL, multivideoFileName, "mp4" )

                            multiNumber += 1
                            totalSavedVideoCount += 1
                            time.sleep( 0.1 )

                    # video download.
                    if True == eachInstaPhoto.isVideo:
                        fullVideoPageURL = directURL + eachInstaPhoto.code
                        print( "try crawling instagram video! directURL: [" + fullVideoPageURL + "]" )

                        time.sleep( 0.1 )

                        #numberOfFiles += 1
                        DownloadVideoFile( fullVideoPageURL,  instaID + "/" + str( numberOfFiles ) + "_video" )
                        totalSavedVideoCount += 1

                        time.sleep( 0.1 )

                    totalSavedPhotoCount += 1

        except urllib.error.HTTPError as err:
            if err.code == 404:
                print( "not found web page!!!" )
        except Exception as e:
            print( e )
            traceback.print_exc()

    dbcon.close()
