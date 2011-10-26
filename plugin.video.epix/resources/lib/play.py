#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import time
import urllib
import demjson
from BeautifulSoup import BeautifulStoneSoup
import xbmcplugin
import xbmc
import xbmcgui
import resources.lib.common as common

pluginhandle = common.pluginhandle

class ResumePlayer( xbmc.Player ) :            
    def __init__ ( self ):
        #xbmc.Player.__init__( self )
        self.player_playing = False
        
    def onPlayBackStarted(self):
        print 'EPIX --> onPlayBackStarted'
        if self.player_playing:
            self.seekPlayback()
        self.player_playing = True
        while self.player_playing:
            try:
                xbmc.sleep(1000)
                self.stoptime = self.getTime()
            except:
                pass

    def onPlayBackStopped(self):
        print "EPIX --> onPlayBackStopped "+str(self.stoptime)
        self.player_playing = False

    def onPlayBackEnded(self):
        print "EPIX --> onPlayBackEnded"
        self.player_playing = False

    def seekPlayback(self):
        try:
            'EPIX --> resuming position: '+str(position)
            self.seekTime(position)
        except: print 'EPIX --> failed to seek'

def buildrtmp(rtmpdata,auth):
    rtmpsplit = rtmpdata.split('?')
    parameters = rtmpsplit[1]+'&auth='+auth
    filename = 'mp4:'+rtmpsplit[0].split('mp4:')[1]
    rtmpbase = rtmpdata.split(filename)[0]
    finalUrl = rtmpbase+'?'+parameters
    finalUrl += ' playpath='+filename
    finalUrl += ' swfurl=http://www.epixhd.com/Epix.v2.0.37.1.swf swfvfy=true'
    return finalUrl

def PLAYVIDEO():
    #common.login()
    #orgin = 'http://dish.epixhd.com/epx/ajax/user/originstatus/'
    #print common.getURL(orgin,useCookie=True)
    #pageurl = 'http://www.epixhd.com/epx/ajax/theater/soloplayer'+common.args.url
    #print common.getURL(pageurl,useCookie=True)
    smilurl = 'http://www.epixhd.com/epx/smil'+common.args.url+'smil.xml'
    data = common.getURL(smilurl,useCookie=True)
    authurl = 'http://www.epixhd.com/epx/ajax/theater/getToken/?url=/'
    auth = common.getURL(authurl,useCookie=True)
    tree = BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    print tree.prettify()
    stackedUrl = 'stack://'
    if common.addon.getSetting("enablepreroll") == 'true':
        for preroll in tree.find('img').findAll('video',recursive=False):
            stackedUrl += buildrtmp(preroll['src'],auth).replace(',',',,')+' , '    
    quality = [0,3000000,2200000,1700000,1200000,900000,500000]
    lbitrate = quality[int(common.addon.getSetting("bitrate"))]
    mbitrate = 0
    streams = []
    for item in tree.find('mbrstream').findAll('video'):
        url = item['src']
        bitrate = int(item['system-bitrate'])
        if lbitrate == 0:
            streams.append([bitrate/1000,url])
        elif bitrate >= mbitrate and bitrate <= lbitrate:
            mbitrate = bitrate
            rtmpdata = url
    if lbitrate == 0:        
        quality=xbmcgui.Dialog().select('Please select a quality level:', [str(stream[0])+'kbps' for stream in streams])
        if quality!=-1:
            rtmpdata = streams[quality][1]
        else:
            return

    stackedUrl += buildrtmp(rtmpdata,auth).replace(',',',,')

    #rtmpsplit = rtmpdata.split('?')
    #parameters = rtmpsplit[1]+'&auth='+auth
    #filename = 'mp4:'+rtmpsplit[0].split('mp4:')[1]
    #rtmpbase = rtmpdata.split(filename)[0]
        
    #finalUrl = rtmpbase+'?'+parameters
    #finalUrl += ' playpath='+filename
    #finalUrl += ' swfurl=http://www.epixhd.com/Epix.v2.0.37.1.swf swfvfy=true'
    
    
    #p=ResumePlayer()
    
    item = xbmcgui.ListItem(path=stackedUrl)
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)
    
    #while not p.isPlaying():
    #    print 'EPIX --> Not Playing'
    #    xbmc.sleep(100)
    #self.p.onPlayBackStarted()    