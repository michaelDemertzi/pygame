"""Config on Darwin w/ frameworks"""

import os, sys, shutil, string
from glob import glob

configcommand = os.environ.get('SDL_CONFIG', 'sdl-config')
configcommand = configcommand + ' --version --cflags --libs'

class Dependency:
    libext = '.dylib'
    def __init__(self, name, checkhead, checklib, lib):
        self.name = name
        self.inc_dir = None
        self.lib_dir = None
        self.lib = lib
        self.found = 0
        self.checklib = checklib+self.libext
        self.checkhead = checkhead
        self.cflags = ''
    
    def configure(self, incdirs, libdirs):
        incname = self.checkhead
        libnames = self.checklib, string.lower(self.name)
        for dir in incdirs:
            path = os.path.join(dir, incname)
            if os.path.isfile(path):
                self.inc_dir = dir
                break
        for dir in libdirs:
            for name in libnames:
                path = os.path.join(dir, name)
                if os.path.isfile(path):
                    self.lib_dir = dir
                    break 
        if self.lib_dir and self.inc_dir:
            print self.name + '        '[len(self.name):] + ': found'
            self.found = 1
        else:
            print self.name + '        '[len(self.name):] + ': not found'

class FrameworkDependency(Dependency):
    def configure(self, incdirs, libdirs):
      for n in '/Library/Frameworks/','~/Library/Frameworks/','/System/Library/Frameworks/':
        if os.path.isfile(n+self.lib+'.framework/Versions/Current/'+self.lib):
          print 'Framework '+self.lib+' found'
          self.found = 1
          self.inc_dir = n+self.lib+'.framework/Versions/Current/Headers'
          self.cflags = '-Ddarwin -Xlinker "-F'+n+self.lib+'.framework" -Xlinker "-framework" -Xlinker "'+self.lib+'"'
          self.origlib = self.lib
          self.lib = ''
          return
      print 'Framework '+self.lib+' not found'

sdl_lib_name = 'SDL'
if sys.platform.find('bsd') != -1:
    sdl_lib_name = 'SDL-1.2'

DEPS = [
    FrameworkDependency('SDL', 'SDL.h', 'lib'+sdl_lib_name, 'SDL'),
    FrameworkDependency('FONT', 'SDL_ttf.h', 'libSDL_ttf', 'SDL_ttf'),
    FrameworkDependency('IMAGE', 'SDL_image.h', 'libSDL_image', 'SDL_image'),
    FrameworkDependency('MIXER', 'SDL_mixer.h', 'libSDL_mixer', 'SDL_mixer'),
    Dependency('SMPEG', 'smpeg.h', 'libsmpeg', 'smpeg'),
]


from distutils.util import split_quoted
def main():
    global DEPS
    
    print 'calling "sdl-config"'
    configinfo = "-I/usr/local/include/SDL -L/usr/local/lib -D_REENTRANT -lSDL"
    try:
        configinfo = os.popen(configcommand).readlines()
        print 'Found SDL version:', configinfo[0]
        configinfo = ' '.join(configinfo[1:])
        configinfo = configinfo.split()
        for w in configinfo[:]:
            if ',' in w: configinfo.remove(w)
        configinfo = ' '.join(configinfo)
        #print 'Flags:', configinfo
    except:
        raise SystemExit, """Cannot locate command, "sdl-config". Default SDL compile
flags have been used, which will likely require a little editing."""

    print 'Hunting dependencies...'
    incdirs = ['/usr/local/include/smpeg']
    libdirs = []
    extralib = []
    newconfig = []
    eat_next = None
    for arg in split_quoted(configinfo):
      if eat_next:
        eat_next.append(arg)  
        eat_next=None
        continue
      if arg[:2] == '-I':
        incdirs.append(arg[2:])
        newconfig.append(arg)
      elif arg[:2] == '-L':
        libdirs.append(arg[2:])
        newconfig.append(arg)
      elif arg[:2] == '-F':
        extralib.append(arg)
      elif arg == '-framework':
        extralib.append(arg)
        eat_next = extralib
    for d in DEPS:
      d.configure(incdirs, libdirs)

    newconfig.extend(map(lambda x:'-Xlinker "%s"'%x,extralib))
    if sys.platform.find('darwin') != -1:
      newconfig.append('-Ddarwin')
    configinfo = ' '.join(newconfig)
    DEPS[0].inc_dirs = []
    DEPS[0].lib_dirs = []
    DEPS[0].cflags = configinfo
    return DEPS

    
if __name__ == '__main__':
    print """This is the configuration subscript for Unix.
             Please run "config.py" for full configuration."""