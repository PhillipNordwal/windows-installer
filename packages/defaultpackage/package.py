# package.py Contains the class package which implements the default functions to
# Find the installed version of a program, find latest version of a program,
# Download the latest version of a program, uninstall a program and handle
# dependencies for a program.

from ..utils import findInstalledVersions,findHighestVersion,scrapePage,parsePage,downloadFile
import ConfigParser, ourlogging

import re, os
from subprocess import call
import zipfile
import shutil

class PackageError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


packageDir = "\\".join(__file__.split("\\")[:-3])

class Package:
    """A Base class to be used as a starting point for every package
    It implements the default functions for finding the latest version
    of a program, install, uninstall etc."""
    
    #Note: packageDir is the directory that the packages folder is located
    def __init__(self):
        logger = ourlogging.packageLogger(self.name())

        ### CONFIG ###
        # These are values which may appear in a config File

        #General
        self.programName = "" # Name of the program that the user sees Used mostly for documenation purposes
        self.arch = "" # 32bit or 64bit or both specified as x86 or x86_64 or both
                       # Note: Both is for installers like virtualbox that work for both arch and auto select


        #Web Fetch Information
        self.url = "" # Main Website URL used as a last resort for searches
        self.versionRegex = "" # Regular expression that matches versions on a page
        self.versionURL = "" # URL used to find latest version used before downloadURL to find version
        self.downloadURL = "" # URL used to find the download for a file
        self.downloadRegex = "" #File to search for (This is depricated and is kept only for legacy purposes)
        self.linkRegex = "" #To be used with Beautiful Soup to scan a page for probable download links


        #Install Information
        self.dependencies = [] #Software that the program Has to have to run
                               #Note: for dependencies that have options such as the Java Runtime Environment or Java Development kit
                               #This can contain lists of lists: [["JDK", "JRE"] "FOO"]. This means that either the JDK or JRE are
                               #Required but either will work and that the package FOO is required
        self.recommended = [] #Software that the program runs better with (ex: camstudio and camstudio codecs)
        self.installMethod = "" # Installation method exe, msi, or zip (Normally auto determined)
        self.installSilentArgs = "" # Arguments to pass to installer for silent install
        self.betaOK = "" # Has a value if beta versions are acceptable
        self.alphaOK = "" # Has a value if alpha versions are acceptable
        self.rcOK = "" # Has a value if rc versions are acceptable

        #Local Version Registry Information
        self.regQueryType=""#Registry Search Method
        self.regKey=""#Registry Hive Location
        self.regSubKey="" #Where to search within hive
        self.regValue="" #Used when gettting installed version by registry value (as opposed to key)
        self.regRegEx="" #Ick, a regular expression to match key/vals in the registry
        self.regExPos=""# A Registry key offset
        self.regVenderName = "" #Name of the vendor in the registry
        self.regProgName = "" #Name of the program in the registry (defaults to programName)
      
        """
        Under 64 bit windows opening hklm\software opens a different key depending on the architecture of the CALLING application (sry for caps)
        So 32 bit python would be default open hklm\software\wow6432node, even if it was trying to go to wow6464 node
        To make things more complicated, it is only possible for a 64 bit app to naviagte to the wow6432node, so there is no path that
        explictely ends up in the 64 node area for 32 node

        To solve this winreg.OpenKey needs to be called with a permissions mask depending on where it is looking if and only if the underlying
        architecture is 64 bit.

        TLDR Make things go by:
        1) If the arch is not 32 bit (platform.platform()!=i386
            searchPath32=_winreg.KEY_READ|_winreg.KEY_WOW64_32KEY
            searchPath64=_winreg.KEY_READ|_winreg.KEY_WOW64_64KEY
	
        2) winreg.OpenKey(winreg.hklm,yourSubkey,0,searchPath)
        """
        self.regArchMask="" #E


        #Local Version Version Info by File. Hopefullly the above works
        self.localVersionFilePath=""#A Path to a file that can be searched for a version number
        self.localVersionFileRegex=""#A Regex to match a version number from the file



        self.installDir = "" #Directory that files should be installed to auto fills in "Program Files" or "Program Files (x86)"
                             #Should be handled scanning arch but if more flexability is needed then it can be specified
        ### LEAVE THIS LAST ###
        self.readConfig(logger) 
        ### END CONFIG ###

        #These values are not read from the config file
        self.logger = logger
        self.currentVersion = "" #Currently installed version
        self.versions = "" #List of versions found on the webpage
        self.latestVersion = "" #Latest verison online
        self.downloadedPath = "" #Path installer was downloaded to
        self.actualURL = "" #Actual URL that was downloaded (after redirects)
        self.installed = False
        self.uninstalled = False

        #Default logic to find the correct Program Files Directory
        #TODO: add logic to pull this from package name
        if (self.installDir == "") and (self.arch.find("64") > -1):
            self.installDir = "C:\\Program Files"
        elif (self.installDir == "") and ((self.arch.find("32") > -1) or (self.arch.find("86") > -1)):
            self.installDir = "C:\\Program Files (x86)"
        else:
            self.logger.debug("Arch could not be determined defaulting installDir to C:\\Program Files")
            self.installDir = "C:\\Program Files"

        #Get the dependencies as a list
        if self.dependencies != [] and self.dependencies != "":
            exec "self.dependencies = " + self.dependencies
        #TODO: add code to exec recommended
        
    def readConfig(self,logger):
        """Reads the configuration file
        which must be named the same as the class"""
        global packageDir
        
        # The config path is necessary to find the config file
        # because the cwd could change and we need to know where the module is located
        # There be dragons in the following code
        config = ConfigParser.RawConfigParser()
        packageDir = packageDir.rstrip("\\") #clean input just in case
        configpath = str(self.__class__).rstrip(self.__class__.__name__).rstrip(".")
        configpath = packageDir + "\\" + configpath.replace(".", "\\") + ".cfg"
        config.read(configpath)
        if configpath == []:
            raise PackageError("Config File could not be read; path was: " + configpath)
        
        # Note One cannot itearate over a dict
        # and change its contents. Thus the following
        names = []
        for name in self.__dict__:
            names.append(name)
        for name in names:
            try:
                self.__dict__[name] = config.get('main', name)
            except ConfigParser.NoOptionError as NoOption:
                logger.debug("Config read error: " + str(NoOption))
        
    def findLocalVersion(self):
        """Finds the local version of a program on the system.
        """
        self.currentVersion=findInstalledVersions(self)
        return self.currentVersion
                    
        
    def findLatestVersion(self):
        """Attempts to find the latest version of a page """
        self.logger.debug("Finding latest web version")
        try:
            url = ""
            regex = self.versionRegex
            # Determine What URL to use
            # Try using most accurate URL first
            if self.versionURL != "":
                url = self.versionURL
            elif self.downloadURL != "":
                url = self.downloadURL
            elif self.url != "":
                url = self.url
            self.logger.debug("Scraping page: " + url + " with " + regex)
            versions = scrapePage(regex, url)
            self.logger.debug("Versions Found: " + str(versions))
            # Remove beta versions if we don't allow them
            # TODO: remove RC and ALPHA versions as well
            if self.betaOK == "":
                versionsTemp = []
                for version in versions:
                    if re.search("beta",version) == None:
                        versionsTemp.append(version)
                versions = versionsTemp
            # findHighestVesion sanitizes its own input
            # so we don't do that here
            ret = findHighestVersion(versions)
            self.latestVersion = ret
            return ret
        except:
            #raise PackageError('unknown error running findLatestVersion()')
            return None
        else:
            return ret

    def fileName(self):
        """Returns the name of the file as it is downladed (just the filename not the path)"""
        return self.__class__.__name__ + "-" + self.latestVersion
    
    def fileNameWithoutVersion(self):
        return self.__class__.__name__ + "-"
    
    def findFile(self, directory):
        """Returns true and updates self.downloadedPath if any version of a package is found in directory"""
        self.logger.debug("Checking for a downloaded file.")
        
        #Don't bother looking if we already know where one is.
        if self.downloadedPath != "" and self.downloadedPath.find(directory) != -1:
            return True
        
        #Enumerate files, see if ours is there.
        for packageFile in os.listdir(directory):
            filename = self.fileNameWithoutVersion()
            if packageFile.rfind(filename) != -1:
                self.downloadedPath = directory + '/' + packageFile
                return True
        return False

    def findLatestFile(self, directory):
        """Returns true and updates self.downloadedPath if a file belonging to us in the directory exists."""
        self.logger.debug("Checking for latest downloaded file.")

        if self.latestVersion == "":
            raise PackageError("Not enough information to determine latest downloaded file. Missing latest version.")
        
        #Enumerate files, see if ours is there.
        for packageFile in os.listdir(directory):
            filename = self.fileName()
            if packageFile.rfind(filename) != -1:
                self.downloadedPath = directory + '/' + packageFile
                return True
        return False

    def determineFileURL(self):
        """Helper function to determine the download url"""
        self.logger.debug("Determining download fileURL.")
        #Fill in #VERSION# if it is part of the downloadURL
        self.downloadURL = self.parseVersionSyntax(self.downloadURL)
        #If downloadRegex is specified use it
        #TODO: Remove this, its depricated
        if self.downloadRegex != "":
            self.downloadRegex = self.parseDownloadRegex()
            fileURL = scrapePage(self.downloadRegex, self.downloadURL)[0]
        #Search the page for the correct download Link
        elif self.linkRegex != '':
            self.linkRegex = self.parseVersionSyntax(self.linkRegex)
            self.downloadURL = self.parseVersionSyntax(self.downloadURL)
            self.logger.debug("Scraping: " + self.downloadURL + " with " + self.linkRegex + " for download link.")
            fileURL = parsePage(self.linkRegex, self.downloadURL)
        #Otherwise parsing the version syntax was all that was needed
        else:
            fileURL = self.downloadURL
        #TODO: Remove the following code (shouldn't be necessary but don't have time to test)
        if not re.match(".*:.*", fileURL):
            #TODO: Fix this - It doesn't cover the case where the link is /foo/bar
            #Which should become: http://website.com/foo/bar
            self.logger.debug("Adjusting unabsolute path")
            # If the path is not absolute we need to put the downloadURL on the front
            temp = self.downloadURL.split('/')[-1] # Find the last bit of downloadURL
            temp = self.downloadURL.rstrip(temp) # strip of everything up to /
            fileURL = temp + fileURL
        #TODO: End code removal
        return fileURL
    
    def download(self, directory):
        """Downloads the latest version of a program to directory"""
        
        if self.findLatestFile(directory):
            self.logger.debug("File found in cache.")
            return self.downloadedPath

        #Otherwise Download file
        try:
            fileURL = self.determineFileURL()
        except:
            raise PackageError("Unable to determine fileURL. This means the linkRegex was not found when searching the page")
        fileName = self.fileName()

        self.logger.debug("Attempting to download file from '" + fileURL + "' as: '" + fileName + "'")
        data = downloadFile(fileURL, directory, fileName) #download File and record data about download
        downloadedFilePath = data['downloadedPath'] # Keep track of where file was downloaded
        try:
            #If the page returned by the link is not file but instead another page
            #Then we need to delete our download and then try to find the file on
            #The page that was returned. For example a download page takes you to a specific page
            #for the file (that is html). msysgit is a good example of this. File links on the page
            #are not strait to the file but are instead to another page that actually has the file
            #Even though the link has the same text on the next page (just an extra click away)
            if data['info']['Content-Type'].rfind("text/html") != -1:
                self.downloadURL = data['actualURL']
                os.remove(downloadedFilePath)
                return self.download(directory)
        except:
            pass
        else:
            self.logger.debug("Finished downloading file to '" + downloadedFilePath + "'")
            return downloadedFilePath


    def install(self, hideGui=True, downloadPath=""):
        """Installs the downloaded version of a program from downloadPath"""
    
        #Check to see if the needed file is already downloaded. Error otherwise.
        if not self.findFile(downloadPath):
            raise PackageError("No downloaded package to install with.")
        
        #Attempt to auto figure out Install method using path
        if self.installMethod == "":
            self.installMethod = self.downloadedPath.split(".")[-1].lower()
            self.logger.debug("Discovered installation method: " + self.installMethod)
            
        #Call correct installation method
        if self.installMethod == "exe":
            self.installExe(hideGui, downloadPath)
        elif self.installMethod == "msi":
            self.installMsi(hideGui, downloadPath)
        elif self.installMethod == "zip":
            self.installZip(hideGui, downloadPath)
        else:
            raise PackageError("Installation Method Not supported")

       
    def uninstall(self):
        """Uninstalls a program"""
        self.logger.critical("uninstall not implemented")
        raise PackageError("Uninstall Not Implemented Yet")

    def name(self):
        return self.__class__.__name__[1:]
    
    def __str__(self):
        return self.programName

    def versionInformation(self):
        #This is bad, I can't find where it should go tho 
        #self.currentVersion=self.findLocalVersion()
        return {'current': self.currentVersion,
                'latest': self.latestVersion}

    def parseVersionSyntax(self, string):
        """Takes in a string an looks for VERSION# and #DOTLESSVERSION# and deals with it"""
        #TODO: Fix this, doesn't actually parse it just replaces currently
        # As such this function is a major hack!
        
        #Error Checking
        if self.latestVersion == "":
            raise PackageError("Not enough information to complete file replacement. Missing latest version.")
        
        if (string.find("#VERSION#") != -1):
            string = string.replace("#VERSION#", self.latestVersion)
        if (string.find("#VERSIONFIRST#") != -1):
            string = string.replace("#VERSIONFIRST#", self.latestVersion.split('.')[0])
        if (string.find("#DOTLESSVERSION#") != -1):
            string = string.replace('#DOTLESSVERSION#', self.latestVersion.replace('.',''))
        if (string.find("#LOWERCASEVERSION#") != -1):
            string = string.replace('#LOWERCASEVERSION#', self.latestVersion.lower())
        if (string.find("#UNDERSCOREVERSION#") != -1):
            string = string.replace('#UNDERSCOREVERSION#', self.latestVersion.replace('.','_'))
        if (string.find("#REGEXVERSION#") != -1):
            string = string.replace("#REGEXVERSION#", self.latestVersion.replace('.','.{0,1}'))
        return string
    
    def parseDownloadRegex(self):
        """Takes in the filename specified in a package config and gets rid of #VERSION#"""
        self.downloadRegex = self.parseVersionSyntax(self.downloadRegex)
        return self.downloadRegex
        
    
    def installExe(self, quiet=True, downloadPath=""):
        self.logger.debug("Attempting exe installation")
        
        if self.downloadedPath == "":
            raise PackageError("Error no installation file downloaded")
        
        #Replace \ in path to / so things work correctly (stupid backslashes)
        self.downloadedPath = self.downloadedPath.replace("/","\\");
        args=[self.downloadedPath]
        
        #Make installer quiet if needed
        if quiet and self.installSilentArgs != "":
            exec "self.installSilentArgs = " + self.installSilentArgs
            args += self.installSilentArgs
        
        #Launch the installer
        if call(args) != 0:
            raise PackageError("Package Installation Failed, Installer returned error")
        self.logger.debug("Finished exe installation")
    
    def installMsi(self, quiet=True, downloadPath=""):
        if self.downloadedPath == "":
            raise PackageError("Error no installation file downloaded")
        
        #Clean up path (stupid backslashes)
        self.downloadedPath = self.downloadedPath.replace("/","\\");
        
        #Make the install quiet if needed
        if quiet:
            args = ["msiexec", "/qb", "/i", self.downloadedPath]
        else:
            args = [self.downloadedPath]
        self.logger.debug("Attempting MSI installation")
        
        #Launch the installer
        if call(args) != 0:
            raise PackageError("Package Installation Failed, Installer returned error")
        self.logger.debug("Finished MSI installation")
    
    def installZip(self, quiet=False, downloadPath=""):
        #TODO: add logic to determine arch via files from zip file
        self.logger.debug("Attempting ZIP installation")
        if self.downloadedPath == "":
            self.logger.critical("ERROR NO INSTALLATION FILE DOWNLOADED")
            raise PackageError("Error no installation file downloaded")
        self.downloadedPath = self.downloadedPath.replace("/","\\");
        #Open Zip File that was downloaded
        with zipfile.ZipFile(self.downloadedPath, 'r') as installFile:
            #Check to see if extraction DIR exists if so delete it
            if os.path.exists(downloadPath + "/" + self.programName + "-" + self.latestVersion):
                self.logger.debug("Removing already extracted files from download directory")
                shutil.rmtree(downloadPath + "/" + self.programName + "-" + self.latestVersion)
            #Extract files to a temp DIR
            self.logger.debug("Extracting zip file for install")
            installFile.extractall(downloadPath + "/" + self.programName + "-" + self.latestVersion)
            #Find subdir in extracted path that actually contains the files we want
            #For example: if a zip file exracts to foo/bar.exe we don't want to have
            #Our program become c:/program File/Program/foo/bar.exe we want it to be
            #c:/program files/program/bar.exe
            iterdir = downloadPath + "/" + self.programName + "-" + self.latestVersion
            folder = len(os.listdir(iterdir))
            while folder == 1:
                iterdir = iterdir + "/" + os.listdir(iterdir)[0]
                folder = len(os.listdir(iterdir))
            if folder <= 0:
                self.logger.critical("Error Zip File was empty")
            self.logger.debug("Moving extracted files to: " + self.installDir + "\\" + self.programName)
            shutil.move(iterdir, self.installDir +"\\" + self.programName)
        #has trouble removing redundant directory. Turned off for now.
            #self.logger.debug("Removing extra filder generated by extraction")
            #shutil.rmtree(temp)

    def canHideGui(self):
        """True if the gui is hideable, false otherwise"""
        return not self.installSilentArgs == ""
    def determineArch(self):
        """Sets self.Arch by using the downloadURL or downloaded files contents"""
        #TODO: Fill in this function
        self.logger.debug("determineArch not implemented yet")
