name = 'name'
category = 'category'
description = 'description'
url = 'url'
regex = 'regex'
version = 'version'
download = 'download'
downloadtype = 'downloadtype'
regexpos = 'regexpos'
silentflags = 'silentflags'
installversion = 'installversion'
key = 'key'
subkey = 'subkey'
value = 'value'
querytype = "querytype"

minimal_list = [ 'Ghostscript', 'GSview 32bit', 'Gimp', 'ImageMagick',
    '7-Zip', 'Firefox', 'Scribus' ]
broken_localversion_minimal_list = [ 'Gimp', 'AdobeReader' ]
broken_download_minimal_list = [ 'Inkscape', 'TrueCrypt', 'AdobeReader' ]
broken_silent_minimal_list = [ 'GSview 32bit', 'AdobeReader' ]

catalog={
    'EMPTY':{
        name:'',
        category:'',
        description:'',
        url:'',
        version:{
            url:'',
            regex:'',
            regexpos:0},
        download:{
            url:'',
            regex:'',
            regexpos:0},
        silentflags:'/verysilent',
        installversion:{
            querytype:'',
            key:'HKLM',
            subkey:'SOFTWARE\\',
            value:'',
            regex:'([0-9]+(?:\.[0-9]+)+)',
            regexpos:0
            }
        },
    'AdobeReader':{
        name:'AdobeReader',
        category:'Editors and Viewers',
        description:'PDF viewer',
        url:'http://get.adobe.com/reader/',
        version:{
            url:'',
            regex:'',
            regexpos:0},
        download:{
            downloadtype:'direct', #not implemented yet
            #enterprise URL can not be shared but may be substituted below
            url:'http://download\.adobe\.com/pub/adobe/reader/win/##MAJOR##.x/##VERSION##/en_US/AdbeRdr##DOTLESSVERSION##_en_US.exe',
            },
        silentflags:'',
        installversion:{
            querytype:'',
            key:'HKLM',
            subkey:'SOFTWARE\\',
            value:'',
            regex:'([0-9]+(?:\.[0-9]+)+)',
            regexpos:0
            }
        },
    'Scribus':{
        name:'Scribus',
        category:'Editors and Viewers',
        description:'Opensource Page Layout',
        url:'http://www.scribus.net/',
        version:{
            url:'http://wiki.scribus.net/canvas/Download',
            regex:'Current stable version is ([0-9]+(?:\.[0-9])+)',
            regexpos:0},
        download:{
            url:'http://wiki.scribus.net/canvas/Download',
            regex:'http://sourceforge\.net/projects/scribus/files/scribus/[0-9]+(?:\.[0-9]+)+/scribus-[0-9]+(?:\.[0-9]+)+-win32-install.exe/download',
            regexpos:0},
        silentflags:'/S',
        installversion:{
            querytype:'regkey',
            key:'HKLM',
            subkey:'SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall',
            regex:'Scribus ([0-9]+(?:\.[0-9]+)+)',
            regexpos:-1
            }
        },
    'Inkscape':{
        name:'Inkscape',
        category:'Multimedia',
        description:'Opensource Vector Graphics Editor',
        url:'http://inkscape.org/',
        version:{
            url:'http://inkscape.org/download/',
            regex:'Stable release <b>([0-9]+(?:\.[0-9]+)+)</b>',
            regexpos:0},
        download:{
            url:'http://sourceforge.net/projects/inkscape/files/inkscape/##VERSION##/',
            regex:'<a href="(http://sourceforge\.net/projects/inkscape/files/inkscape/[0-9]+(?:\.[0-9]+)+/Inkscape-[0-9]+(?:\.[0-9]+)+-[0-9]-win32\.exe/download)" ',
            regexpos:0},
        silentflags:'/S',
        installversion:{
            querytype:'regval',
            key:'HKLM',
            subkey:'SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Inkscape',
            value:'DisplayVersion',
            regex:'([0-9]+(?:\.[0-9]+)+)',
            regexpos:0
            }
        },
    'Gimp':{
        name:'Gimp',
        category:'Multimedia',
        description:'GNU Image Manipulation Program.',
        url:'http://www.gimp.org/',
        version:{
            url:'http://www.gimp.org/downloads/',
            regex:'<a href="http://downloads\.sourceforge\.net/gimp-win/gimp-([0-9](?:\.[0-9]+)+)-i686-setup-[0-9]+.exe">',
            regexpos:0},
        download:{
            url:'http://www.gimp.org/downloads/',
            regex:'<a href="(http://downloads\.sourceforge\.net/gimp-win/gimp-[0-9](?:\.[0-9]+)+-i686-setup-[0-9]+.exe)">',
            regexpos:0},
        silentflags:'/verysilent',
        installversion:{
            querytype:'regvalsearch', #not yet implemented
            key:'HKLM',
            subkey:'SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall',
            value:'DisplayName',
            regex:'GIMP ([0-9]+(?:\.[0-9]+)+)',
            regexpos:-1
            }
        },
    'TrueCrypt':{
        name:'TrueCrypt',
        category:'Encryption',
        description:'Virtual disk encryption',
        url:'http://www.truecrypt.org/',
        version:{
            url:'http://www.truecrypt.org/downloads',
            regex:'Latest Stable Version - ([0-9]+(?:\.[0-9]+)+[a-zA-Z]?)',
            regexpos:0},
        download:{
            url:'',
            regex:'',
            regexpos:0},
        silentflags:'/verysilent',
        installversion:{
            querytype:'regval',
            key:'HKLM',
            subkey:'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\TrueCrypt',
            value:'DisplayVersion',
            regex:'([0-9]+(?:\.[0-9]+)+[a-zA-Z]?)',
            regexpos:0
            }
        },
    'ImageMagick':{
        name:'ImageMagick',
        category:'Multimedia',
        description:'A software suite to create, edit, compose, or convert bitmap images.',
        url:'http://www.imagemagick.org',
        version:{
            url:'http://www.imagemagick.org/www/binary-releases.html',
            regex:'<a href= "http://www\.imagemagick\.org/download/binaries/ImageMagick-([0-9]+(?:\.[0-9]+)+-[0-9]+)-Q16-windows-dll\.exe">',
            regexpos:0},
        download:{
            url:'http://www.imagemagick.org/www/binary-releases.html',
            regex:'<a href= "(http://www\.imagemagick\.org/download/binaries/ImageMagick-[0-9]+(?:\.[0-9]+)+-[0-9]+-Q16-windows-dll\.exe)">',
            regexpos:0},
        silentflags:'/VERYSILENT',
        installversion:{
            querytype:'regval',
            key:'HKLM',
            subkey:'SOFTWARE\\ImageMagick\\Current',
            value:'Version',
            regex:'([0-9]+(?:\.[0-9]+)+)',
            regexpos:0
            }
        },
    'GSview 32bit':{
        name:'GSview 32bit',
        category:'Utilities',
        description:'GSview is a graphical interface for Ghostscript',
        url:'http://pages.cs.wisc.edu/~ghost/gsview/index.htm',
        version:{
            url:'http://pages.cs.wisc.edu/~ghost/gsview/index.htm',
            regex:'>Obtaining GSview ([0-9]+(?:\.[0-9]+)+)<',
            regexpos:0},
        download:{
            url:'http://pages.cs.wisc.edu/~ghost/gsview/get##DOTLESSVERSION##.htm',
            regex:'<a href="(http://mirror\.cs\.wisc\.edu/pub/mirrors/ghost/ghostgum/gsv[0-9]+w32\.exe)">',
            regexpos:0},
        silentflags:'/auto',
        installversion:{
            querytype:'regvalname',
            key:'HKLM',
            subkey:'SOFTWARE\\Ghostgum\\GSView',
            regex:'([0-9]+(?:\.[0-9]+)+)',
            regexpos:-1
            }
        },
    'Ghostscript':{
        name:'Ghostscript',
        category:'Utilities',
        description:'An interpreter for the PostScript language and for PDF.',
        url:'http://www.ghostscript.com/',
        version:{
            url:'http://www.ghostscript.com/download/',
            regex:'<a href="gsdnld.html">Ghostscript ([0-9]+(?:\.[0-9]+)+)</a>',
            regexpos:0},
        download:{
            url:'http://www.ghostscript.com/download/gsdnld.html',
            regex:'<a href="(http://downloads\.ghostscript\.com/public/gs[0-9]+w32\.exe)">',
            regexpos:0},
        silentflags:'/S',
        installversion:{
            querytype:'regkey',
            key:'HKLM',
            subkey:'SOFTWARE\\GPL Ghostscript',
            regex:'([0-9]+(?:\.[0-9]+)+)',
            regexpos:-1
            }
        },
    '7-Zip':{
        name:'7-Zip',
        category:'Utilities',
        description:'Multiple format file compression and decompression',
        url:'http://7-zip.org',
        version:{
            url:'http://7-zip.org',
            regex:'<P><B>Download 7-Zip ([0-9]+(?:\.[0-9]+)+) \(',
            regexpos:0},
        download:{
            url:'http://7-zip.org',
            regex:'<A href="(.*/sevenzip/7z[0-9]+.exe)',
            regexpos:0},
        silentflags:'/S',
        installversion:{
            querytype:'regval',
            key:'HKLM',
            subkey:'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\7-Zip',
            value:'DisplayName',
            regex:'([0-9]+(?:\.[0-9]+)+)',
            regexpos:0
            }
        },
    'Firefox':{
        name:'Firefox',
        category:'Internet Tools',
        description:'The Mozilla Firefox browser',
        url:'http://www.mozilla.org/en-US/firefox/new/',
        version:{
            url:'http://www.mozilla.org/en-US/firefox/new/',
            regex:'<li><a href="http://download\.mozilla\.org/\?product=firefox-([0-9]+(?:\.[0-9]+)+)&amp;os=win&amp;lang=en-US">Windows</a></li>',
            regexpos:0},
        download:{
            url:'http://www.mozilla.org/en-US/firefox/new/',
            regex:'<li><a href="(http://download\.mozilla\.org/\?product=firefox-[0-9]+(?:\.[0-9]+)+&amp;os=win&amp;lang=en-US)">Windows</a></li>',
            regexpos:0},
        silentflags:'-ms',
        installversion:{
            querytype:'regval',
            key:'HKLM',
            subkey:'SOFTWARE\\Mozilla\\Mozilla Firefox',
            value:'CurrentVersion',
            regex:'([0-9]+(?:\.[0-9]+)+)',
            regexpos:0
            }
        }
    }
