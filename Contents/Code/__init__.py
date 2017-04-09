# Debug
DEBUG           = True
DEBUG_STRUCTURE = False

# General
TITLE      = 'Wish 107.5'
PREFIX     = '/video/wish1075'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/600.3.18 (KHTML, like Gecko) Version/8.0.3 Safari/600.3.18'

# Resources
ART      = 'wish-logo.png'
ICON     = 'wish-logo.png'
LOGO     = 'wish-logo.png' #'http://wish1075.com/wp-content/themes/wishfm-2016/images/wish-logo-share.png'

# Wish 107.5 URLs

# Youtube URLs
BASE_URL      = 'https://youtube.com/user/WishFM1075official'
URL_VIDEOS    = BASE_URL + '/videos'
URL_PLAYLISTS = BASE_URL + '/playlists?sort=lad&view=1&flow=list'
URL_SEARCH    = BASE_URL + '/search?query={QUERY}'

# WISH URLs
URL_ARTISTS = 'http://wish1075.com/wishclusives/'

# Max number of items to show in one listing
MAX_NUM_VIDEOS   = 10

# Set default cache to 3 hours
CACHE_TIME = 3 * CACHE_1HOUR # seconds

# Regex
#RE_ARTISTS          = Regex( r'<a href="(?P<url>http:\/\/wish1075.com\/artist\/[^\/]+\/)">[^>]+>(?P<name>[^<]+)<\/h4> <\/a>(?P<summary>[^<]+)<\/div>', Regex.MULTILINE )
#RE_VIDEOS           = Regex( r'<a href="(?P<url>http:\/\/wish1075.com\/wishclusive\/[^\/]+\/)">[^>]+>(?P<name>[^<]+)<\/h4> <\/a>\s*<p>(?P<summary>[^<]+)<\/p>', Regex.MULTILINE )
RE_VIDEO_IMAGE_URL   = Regex( r'background-image\: url\((?P<url>[^)]+)\)' )
RE_VIDEO_TITLE_CLEAN = Regex( r'^WATCH:' )

####################################################################################################
def Start( **kwargs ):

    InputDirectoryObject.thumb = R('Search.png')
    DirectoryObject.art  = R(LOGO)

    ObjectContainer.title1 = TITLE

    HTTP.CacheTime = CACHE_TIME

    HTTP.Headers['User-Agent'] = USER_AGENT
    

####################################################################################################
@handler(PREFIX, TITLE, art=LOGO, thumb=LOGO)
def MainMenu( **kwargs ):

    try:
    
        oc = ObjectContainer()

        oc.add(InputDirectoryObject(key = Callback(Search), title='Search', summary='Search Wish 107.5', prompt='Search for...'))
        #oc.add(SearchDirectoryObject(identifier='com.plexapp.plugins.wish1075', title='Search', summary='Search Wish 107.5', prompt='Search:', thumb=R('search.png')))

        oc.add( DirectoryObject( key = Callback( Alphabetical, title = TITLE, name = 'Artists'       ), title = 'Artists'       ) )
        oc.add( DirectoryObject( key = Callback( Playlists   , title = TITLE, name = 'Playlists'     ), title = 'Playlists'     ) )

        #Log.Debug("after USE_YOUTUBE")

        html = HTML.ElementFromURL( BASE_URL )

        #Log.Debug("html: '%s'" % (HTML.StringFromElement(html)) )

        content = html.xpath('//ul[@id="browse-items-primary"]/li[contains(@class,"browse-list-item-container")]')[0]

        #Log.Debug("content: '%s'" % (HTML.StringFromElement(content)) )

        sections = content.xpath('//h2/a[contains(@class,"branded-page-module-title-link")]')

        for section in sections:

            #Log.Debug("in sections" )
            #Log.Debug("section: '%s'" % (HTML.StringFromElement(section)) )

            section_name = section.xpath('./span/span//text()')[0]
            section_name = String.DecodeHTMLEntities( section_name ).strip()
            #Log.Debug("WISH section_name: '%s'" % (section_name) )

            section_url = section.xpath('./@href')[0]
            if section_url.startswith('/'):
                section_url = 'https://www.youtube.com' + section_url

            #Log.Debug("WISH section_url: '%s'" % (section_url) )

            oc.add( DirectoryObject( key = Callback( Section, title = TITLE, name = section_name, url = section_url ), title = section_name ) )


        return oc
        
    except:

        return NothingFound(TITLE, 'name', 'content')


####################################################################################################
@route(PREFIX + '/playlists', first=int )
def Playlists( first=0, **kwargs ):

    try:
    
        oc = ObjectContainer()

        html = HTML.ElementFromURL( URL_PLAYLISTS )

        #Log.Debug("html: '%s'" % (HTML.StringFromElement(html)) )

        content = html.xpath('//ul[@id="browse-items-primary"]/li[contains(@class,"browse-list-item-container")]')[0]

        #Log.Debug("content: '%s'" % (HTML.StringFromElement(content)) )

        sections = content.xpath('//div[contains(@class,"yt-lockup-content")]')

        for section in sections:

            #Log.Debug("in sections" )
            #Log.Debug("section: '%s'" % (HTML.StringFromElement(section)) )

            section_name = section.xpath('./h3[contains(@class,"yt-lockup-title")]/a/text()')[0]
            section_name = String.DecodeHTMLEntities( section_name ).strip()
            #Log.Debug("WISH section_name: '%s'" % (section_name) )

            section_url = section.xpath('./div[contains(@class,"yt-lockup-meta")]/a/@href')[0]
            if section_url.startswith('/'):
                section_url = 'https://www.youtube.com' + section_url

            #Log.Debug("WISH section_url: '%s'" % (section_url) )

            oc.add( DirectoryObject( key = Callback( Section, title = TITLE, name = section_name, url = section_url ), title = section_name ) )

        # Sort in alphabetical order
        oc.objects.sort(key = lambda obj: obj.title)

        return oc
        
    except:

        return NothingFound(TITLE, 'name', 'content')


####################################################################################################
@route(PREFIX + '/search', first=int )
def Search( query, first=0, **kwargs ):

    try:

        Log.Debug('#### IN SEARCH ####')

        url = URL_SEARCH.replace('{QUERY}',String.Quote(query))

        Log.Debug("SEARCH URL: %s", url )

        oc = ObjectContainer( title2 = 'Search Results' )

        html = HTML.ElementFromURL( url )

        videos = html.xpath('//div[contains(@class,"yt-lockup-video")]')[first:first+MAX_NUM_VIDEOS]

        for video in videos:

            video_image = video.xpath('.//img/@data-thumb')[0]
            video_image = video_image.split('?')[0]
            Log.Debug("SEARCH video_image: '%s'" % (video_image) )

            video_url = video.xpath('.//h3/a/@href')[0]
            video_url = video_url.split('&')[0]
            if video_url.startswith('/'):
                video_url = 'https://www.youtube.com' + video_url
            Log.Debug("SEARCH video_url: '%s'" % (video_url) )

            video_title = video.xpath('.//h3/a/text()')[0]
            video_title = String.DecodeHTMLEntities( video_title ).strip()
            Log.Debug("SEARCH video_title: '%s'" % (video_title) )

            summary = video.xpath('.//div[contains(@class,"yt-lockup-description")]/text()')[0]
            summary = String.DecodeHTMLEntities( summary ).strip()
            Log.Debug("SEARCH summary: '%s'" % (summary) )

            oc.add( VideoClipObject( url = video_url, title = video_title, summary = summary, thumb = video_image, art = video_image ) )

        if len(videos) == MAX_NUM_VIDEOS:
            oc.add( NextPageObject(key = Callback( Search, query, first = first + MAX_NUM_VIDEOS ) ) )

        if len(oc) < 1:
            return NothingFound('Search Results', query, 'items')
                
        return oc 
    
    except:

        return NothingFound('Search Results', query, 'content')


####################################################################################################
@route(PREFIX + '/section', first=int )
def Section( title, name, url, first=0, **kwargs ):

    try:
    
        oc = ObjectContainer( title1 = title, title2 = name )

        #Log.Debug("url: '%s'" % url )

        html = HTML.ElementFromURL( url )

        #Log.Debug("html: '%s'" % (HTML.StringFromElement(html)) )

        videos = html.xpath('//table[@id="pl-video-table"]//tr')[first:first+MAX_NUM_VIDEOS]

        for video in videos:

            #Log.Debug("video: '%s'" % (HTML.StringFromElement(video)) )

            video_image = video.xpath('.//img/@data-thumb')[0]
            video_image = video_image.split('?')[0]
            #Log.Debug("WISH video_image: '%s'" % (video_image) )

            video_url = video.xpath('.//a[contains(@class,"pl-video-title-link")]/@href')[0]
            video_url = video_url.split('&')[0]
            if video_url.startswith('/'):
                video_url = 'https://www.youtube.com' + video_url
            #Log.Debug("WISH video_url: '%s'" % (video_url) )

            video_title = video.xpath('.//a[contains(@class,"pl-video-title-link")]/text()')[0]
            video_title = String.DecodeHTMLEntities( video_title ).strip()
            #Log.Debug("WISH video_title: '%s'" % (video_title) )

            oc.add( VideoClipObject( url = video_url, title = video_title, summary = 'by Wish 107.5', thumb = video_image, art = video_image ) )

        if len(videos) == MAX_NUM_VIDEOS:
            oc.add( NextPageObject(key = Callback( Section, title = title, name = name, url = url, first = first + MAX_NUM_VIDEOS ) ) )

        return oc
        
    except:
    
        return NothingFound(title, name, 'videos')


####################################################################################################
@route(PREFIX + '/alphabetical' )
def Alphabetical( title, name, **kwargs ):

    oc = ObjectContainer( title1 = title, title2 = name )

    for letters in ['ABC','DEF','GHI','JKL','MNO','PQR','STU','VWX','YZ']:
        oc.add( DirectoryObject( key = Callback( Artists, title = TITLE, letters = letters ), title = letters ) )
            
    return oc


####################################################################################################
@route(PREFIX + '/artists' )
def Artists( title, letters, **kwargs ):

    try:
    
        oc = ObjectContainer( title1 = title, title2 = letters )

        #Log.Debug("Artists URL: '%s'" % (URL_ARTISTS) )


        html = HTML.ElementFromURL( URL_ARTISTS )
        #Log.Debug("Artists html: '%s'" % (HTML.StringFromElement(html)) )

        artists = html.xpath('//div[@class="container content"]//h2[contains(text(),"Artists")]/..//div[contains(@class,"artist-list")]')

        for artist in artists:

            try:

                #Log.Debug("in artist loop: " )

                url = artist.xpath('./a/@href')[0]
                #Log.Debug("Wishclusive url: '%s'" % (url) )

                artist_name = artist.xpath('./a/h4/text()')[0]
                artist_name = String.DecodeHTMLEntities( ''.join(artist_name) ).strip()
                #Log.Debug("Wishclusive artist_name: '%s'" % (artist_name) )

                if artist_name[0] in letters:
                    #Log.Debug("match(%s): '%s'" % (letters,artist_name) )
                    oc.add( DirectoryObject( key = Callback( Artist, title = letters, name = artist_name, url = url ), title = artist_name ) )

            except:
                continue

        if len(oc) < 1:
            return NothingFound(title, letters, 'artists')

        # Sort in alphabetical order
        oc.objects.sort(key = lambda obj: obj.title)

        return oc

        
    except:
    
        return NothingFound(title, letters, 'content')


####################################################################################################
@route(PREFIX + '/artist' )
def Artist( title, name, url, **kwargs ):

    try:
    
        oc = ObjectContainer( title1 = title, title2 = name )

        html = HTML.ElementFromURL( url )

        #artist_info = html.xpath('//div[@class="container content"]//h2[contains(text(),name)]/../..//div[@class="post artist"]//p/text()')
        artist_info = html.xpath('//div[@class="post artist"]//p/text()')[0]
        artist_info = String.DecodeHTMLEntities( artist_info ).strip()

        Log.Debug( "Artist: %s", artist_info )

        videos = html.xpath('//div[contains(@class,"artist-video")]')

        for video in videos:

            #Log.Debug("video: '%s'" % (HTML.StringFromElement(video)) )

            '''style = video.xpath('./div[@class="image"]/@style')
            Log.Debug("style: '%s'" % (HTML.StringFromElement(style)) )

            m = RE_VIDEO_IMAGE_URL.match( style )
            if m:
                video_image = m.group('url')
                video_image = video_image.split('?')[0]
            else:
            '''
            video_image = R(ICON)
            Log.Debug("WISH video_image: '%s'" % (video_image) )

            video_url = video.xpath('.//div[@class="details center"]/a/@href')[0]
            video_url = video_url.split('&')[0]
            if video_url.startswith('/'):
                video_url = 'https://www.youtube.com' + video_url
            Log.Debug("WISH video_url: '%s'" % (video_url) )

            video_title = video.xpath('.//div[@class="details center"]/a/h4/text()')[0]
            video_title = String.DecodeHTMLEntities( video_title )
            #video_title = RE_VIDEO_TITLE_CLEAN.sub( video_title, '' ).strip()
            Log.Debug("WISH video_title: '%s'" % (video_title) )

            oc.add( DirectoryObject( key = Callback( Video, title = name, name = video_title, url = video_url ), title = video_title, thumb = video_image, art = video_image ) )

        return oc

    except:
    
        return NothingFound(title, name, 'content')


####################################################################################################
@route(PREFIX + '/video')
def Video( title, name, url, **kwargs ):

    try:
    
        oc = ObjectContainer( title1 = title, title2 = name )

        #Log.Debug("url: '%s'" % url )

        html = HTML.ElementFromURL( url )

        #Log.Debug("html: '%s'" % (HTML.StringFromElement(html)) )

        video_image = html.xpath('//meta[@name="twitter:image"]/@content')[0]
        video_image = video_image.split('?')[0]
        Log.Debug("WISH video_image: '%s'" % (video_image) )

        video_url = html.xpath('//div[@class="container content"]//iframe/@src')[0]
        video_url = video_url.split('/')[-1]
        video_url = 'https://www.youtube.com/watch?v=' + video_url
        Log.Debug("WISH video_url: '%s'" % (video_url) )

        video_title = html.xpath('//meta[@name="twitter:title"]/@content')[0]
        video_title = String.DecodeHTMLEntities( video_title )
        #video_title = RE_VIDEO_TITLE_CLEAN.sub( video_title, '' ).strip()
        Log.Debug("WISH video_title: '%s'" % (video_title) )

        summary = html.xpath('//meta[@name="twitter:description"]/@content')[0]
        summary = String.DecodeHTMLEntities( summary ).strip()
        Log.Debug("WISH summary: '%s'" % (summary) )

        oc.add( VideoClipObject( url = video_url, title = video_title, summary = summary, thumb = video_image, art = video_image ) )

        return oc
        
    except:
    
        return NothingFound(title, name, 'video')


'''
####################################################################################################
def ExtractHtmlText( html, fallback=''):
    try:
        text = String.DecodeHTMLEntities( dict[key] ).strip()
    except: 
        text = fallback
        Log.Debug("# Using fallback text: '%s' instead of json['%s'] #" % (fallback,key) )
    #Log.Debug("# ExtractHtmlText: json['%s'] = '%s' #" % (key,text) )
    return text


####################################################################################################
def ExtractImageUrl(url, fallback):
    try:
        url = url.replace(r"http://","")
        url = "http://" + String.Quote(url)
        url = Resource.ContentsOfURLWithFallback( url, fallback=fallback )
    except: 
        url = fallback
        Log.Debug("# Using fallback image: '%s' instead of json['%s'] #" % (fallback,key) )
    #Log.Debug("# ExtractImageUrl: json['%s'] = '%s'#" % (key,url) )
    return url
'''

####################################################################################################
def NothingFound(title, name, items):

    oc = ObjectContainer( title1 = title, title2 = name )

    oc.header  = name
    oc.message = "No %s found." % str(items)
    
    return oc

    
## EOF ##
    
