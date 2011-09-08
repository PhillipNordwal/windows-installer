""" \file utils.py
\brief Utility functions to help with windows package management.
"""

import urllib2
import re
import os
import _winreg

def getPage(url):
    """Returns the contents of a url as a string.

    This currently doesn't do anything to handle exceptions.

    \param url The url to grab a page from.
    \return A string containing the page contents of url.
    """
    try:
        f=urllib2.urlopen(url)
        page = f.read()
        f.close()
    except urllib2.URLError:
        print 'Couldn not connect to and read from %s' % url
    except:
        print 'unknown error running  getPage(%s)' % url
        raise
    else:
        return page

def scrapePage(reg, url, pos=0):
    """Scrapes the page from url for the reg at position pos.

    This will return the pos'th match of the regular expression reg from the
    page at url. pos defaults to 0.

    \param reg The regular expression to match.
    \param url The page to scrape.
    \param pos Which regulare expression match to return, defaults to 0.
    \return The pos'th reg match on the page at url.
    """
    try:
        ret = re.findall(reg, getPage(url))[pos]
    except TypeError as strerror:
        if strerror == 'first argument must be a string or compiled pattern':
            print 'you are missing or have an invalid regex in %s' % reg
        elif strerror == 'expected string or buffer':
            print 'your have no page being returned by getPage()'
        print 'when calling scrapePage(%s, %s, %d)' %(reg, url, pos)
    except IndexError:
        print 'regexpos entry larger then the number of results mathing regex '
        print 'when calling scrapePage(%s, %s, %d)' %(reg, url, pos)
    except:
        print 'unknown error running  scrapePage(%s, %s, %d)' % (reg, url, pos)
        raise
    else:
        return ret

def scrapePageDict(d):
    """Scrapes the page from d['url'] for the d['regex'] at position 
    d['regexpos'].

    This will return the d['regexpos']'th match of the regular expression
    d['regex'] from the page at d['url'].

    \param d A dictionary that contains 'regex' The regular expression to match.
    'url' The page to scrape.
    'regexpos' Which regular expression match to return, defaults to 0.
    \return The regexpos'th reg match on the page at url.
    """
    try:
        ret = re.findall(d['regex'], getPage(d['url']))[d['regexpos']]
    except TypeError as strerror:
        if strerror == 'first argument must be a string or compiled pattern':
            print 'you are missing or have an invalid regex in %s' %d
        elif strerror == 'expected string or buffer':
            print 'your have no page being returned by getPage()'
        print 'when calling scrapePageDict(%s)' %d
    except IndexError:
        print 'regexpos entry larger then the number of results mathing regex '
        print 'when calling scrapePageDict(%s)' %d
    except KeyError as strerror:
        print 'd did not contain a "%s" entry' % strerror
        print 'when calling scrapePage(%s)' %d
    except:
        print 'unknown error running scrapePage(%s)' % d
        raise
    else:
        return ret

def getWebVersion(d):
    """Get the version from the web of the catalog entry in d

    Use the page at the url specified in d['version']['url'], and the regular
    expression specified in d['version']['regex'] to find the latest version
    number of the passed package. The d['version']['regexpos']'th match of the
    regular expression is returned.

    \param d The dictionary entry for a package, containing at least an entry
    for 'version' that is a dictionary that contains a 'url', 'regex', and
    'regexpos'
    \return the version number matched by the regular expression and page
    passed in.
    """
    try:
        ret = scrapePageDict(d['version'])
    except KeyError:
        print 'd did not contain a "version" entry'
        print 'when calling getWebVersion(%s)' %d
    except:
        print 'unknown error running getWebVersion(%s)' % d
        raise
    else:
        return ret

def getDownloadURL(d):
    """Get the DownloadURL from the web of the catalog entry in d

    Use the page at the url specified in d['download']['url'], and the regular
    expression specified in d['download']['regex'] to find the download url of
    the latest version of the passed package. The d['download']['regexpos']'th
    match of the regular expression is returned.

    \param d The dictionary entry for a package, containing at least an entry
    for 'download' that is a dictionary that contains a 'url', 'regex' and
    'regexpos'
    \return the download url matched by the regular expression and page passed
    in.
    """
    try:
        downurl = scrapePageDict(d['download'])
        fredirectedurl = urllib2.urlopen(downurl)
        redirectedurl = fredirectedurl.geturl()
        fredirectedurl .close()
    except urllib2.URLError:
        print 'could not connect to %s' %d['download']['url']
        print 'when calling getDownloadURL(%s)' %d
    except KeyError:
        print 'd did not contain a "download" entry'
        print 'when calling getDownloadURL(%s)' %d
    except:
        print 'unknown error running getDownloadURL(%s)' % d
        raise
    else:
        return redirectedurl

def downloadLatest(d, location='downloads\\'):
    """Download the latest version of the package d.

    Use the information specified in the package d to download the latest
    version of the package from the web. The default download location is
    './downloads'

    \param d The dictionary entry for a package, containing at least a 'name', 
    as well as a 'version', and 'download' dict containing 'url', 'regex', and
    'regexpos'.
    \param location The location to download the file to.
    \return the path to the downloaded file.
    """
    try:
        name = d['name']
        version = getWebVersion(d)
        downurl = getDownloadURL(d)
        furl = urllib2.urlopen(downurl)
        filecontents = furl.read()
        furl.close()
        parsed=urllib2.urlparse.urlparse(furl.geturl())
        pathname = urllib2.url2pathname(parsed.path)
        filename = pathname.split("\\")[-1]
        newfileloc = location + name + '---' + version + '---' + filename
        with open(newfileloc, "wb") as f:
            f.write(filecontents)
    except IOError as (errno, strerror):
        print 'could not open file, I/O error({0}): {1}'.format(errno, strerror)
        print 'when calling downloadLatest(%s, %s)' %(d, location)
    except TypeError as strerror:
        print "TypeError: %s, location may not be a string" % strerror
        print 'when calling downloadLatest(%s, %s)' %(d, location)
    except urllib2.URLError:
        print 'could not connet to and read from %s' % downurl
        print 'when calling downloadLatest(%s, %s)' %(d, location)
    except KeyError:
        print 'd did not contain a "name" entry'
        print 'when calling downloadLatest(%s, %s)' %(d, location)
    except:
        print 'unknown error running downloadLatest(%s, %s)' %(d, location)
        raise
    else:
        return newfileloc

def getInstalledVersion(d):
    """Get the version of the installed package.

    Use the information specified in the package d to lookup the installed
    version on the computer. 

    \param d The dictionary entry for a package containing at least a
    'installversion' dictionary, which itself must contain a 'type' entry.
    Currently supported types are 'reg' which must have a key, subkey and value
    entry.
    \return The version installed or None.
    """
    try:
        if d['installversion']['querytype'] == 'reg':
            # should do a lookup table here
            if d['installversion']['key'] == 'HKLM':
                tempkey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
                    d['installversion']['subkey'])
                value = str(_winreg.QueryValueEx(tempkey,
                    d['installversion']['value'])[0])
                version = re.findall(d['installversion']['regex'],
                    value)[d['installversion']['regexpos']]
                return version
    except TypeError as strerror:
        if strerror == 'first argument must be a string or compiled pattern':
            print 'you are missing or have an invalid regex in %s' %d
        elif strerror == 'expected string or buffer':
            print 'your have no value being pulled from the registry'
        print 'when calling getInstalledVersion(%s)' %d
    except WindowsError:
        print 'The registry key or value could not be found'
        print 'when calling getInstalledVersion(%s)' %d
    except KeyError as strerror:
        print 'd did not contain a "%s" entry' % strerror
        print 'when calling getInstalledVersion(%s)' %d
    except:
        print 'unkown error running getInstalledVersion(%s)' %d
    else:
        return None

def installPackage(d, location):
    """Install the package at location.

    Use the information specified in the package d to run the installer at 
    location with the correct commandline options.

    \param d The dictionary entry for a package, containing at least a 'name', 
    as well as a 'version', a 'download' dict containing 'url', 'regex', and
    'regexpos' a 'silentflags' entry containing silent command line options for
    the installer.
    \param location The location to install from.
    \return The value returned by the installer
    """
    try:
        ret = os.system(location + " " + d['silentflags'])
    except:
        print 'unknown error running installPackage(%s, %s)' %(d, location)
    else:
        return ret

def downloadAndInstallLatest(d, location='downloads\\', keep=True):
    """Download the latest version of the package d and install it.

    Use the information specified in the package d to download the latest
    version of the package from the web. The default download location is
    './downloads' and install it.

    \param d The dictionary entry for a package, containing at least a 'name', 
    as well as a 'version', and 'download' dict containing 'url', 'regex', and
    'regexpos'.
    \param location The location to download the file to.
    \param keep Should we keep the download?
    \return The value returned by the installer
    """
    try:
        fpath = downloadLatest(d, location)
        ret = installPackage(d, fpath)
        
        if not keep and ret == 0:
            os.remove(fpath)
    except WindowsError as (errno, strerror):
        print 'could not remove the file, WindowsError({0}): {1}'.format(errno,
            strerror)
        print 'when calling installPackage(%s, %s)' %(d, location)
    except:
        print 'unknown error running installPackage(%s, %s)' %(d, location)
    else:
        return ret

def uninstall(d):
    """TODO: XXX: STUB NEEDS FILLED OUT"""
    raise Exception("This is a stub")
    return 0

def upgrade(d):
    """TODO: XXX: STUB NEEDS FILLED OUT"""
    raise Exception("This is a stub")
    return 0

def installAll(catalog, collection):
    """TODO: XXX: STUB NEEDS FILLED OUT"""
    raise Exception("This is a stub")
    return 0

def getAllInstalledVersions(catalog, collection):
    """TODO: XXX: STUB NEEDS FILLED OUT"""
    raise Exception("This is a stub")
    return 0

def getAllWebVersions(catalog, collection):
    """TODO: XXX: STUB NEEDS FILLED OUT"""
    raise Exception("This is a stub")
    return 0
