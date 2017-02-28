#!/usr/bin/env python
#    chase 
#    Copyright (C) 2003 Bruce Woodward

#    chase is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.

#    chase is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    You should have received a copy of the GNU General Public License
#    along with chase; see the file COPYING. If not, write to the Free Software
#    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


import pickle

class BadType(Exception): pass

class State:
    def __init__(self):
        pass
    
    def save(self, outfile):
        pickle.dump(self, outfile)

    def saveStr(self):
        return pickle.dumps(self)

    def _load(reset, infile):
        inobj = pickle.load(infile)
        for i in reset.keys():
            setattr(inobj, i, reset[i])
        return inobj
    _load= staticmethod(_load)

if __name__ == '__main__':
    import unittest
    import pickle

    class dummy(State):
        def __init__(self):
            self.a = None
            State.__init__(self)
            self.b= 10
        def set_a(self,v):
            self.a= v
        def get_a(self):
            return self.a
        def set_b(self,v):
            self.b= v
        def get_b(self):
            return self.b
        def reload(infile):
            return State._load({'a':None}, infile)
        reload= staticmethod(reload)

    def openDummyObj():
        d = dummy()
        return d

    class OutFile:
        def __init__(self):
            self.fileD= None
            self.fileName= '/tmp/objstat'
        def openWrite(self):
            self.fileD= open(self.fileName, 'w+')
        def openRead(self):
            self.fileD= open(self.fileName, 'r')
        def close(self):
            self.fileD.close()
        def get_fd(self):
            return self.fileD
        
    class test(unittest.TestCase):

        def createDummyObj(a=123):
            ## nasty testing.
            ## create a pickle of an object, setting a to 123 and saving
            ## that state.
            outfile = OutFile()
            outfile.openWrite()
            d = openDummyObj()
            d.set_a(123)
            d.save(outfile.get_fd())
            outfile.close()
            
        def testSaveAndLoadState(self):
            self.createDummyObj()
            ## open the pickled object, having the State.load method reset
            ## the a instance varible to None as setup by the openDummyObj
            ## function.
            d = openDummyObj()
            infile = OutFile()
            infile.openRead()
            d = d.reload(infile.get_fd())
            infile.close()
            self.assertEquals(d.get_a(), None)
            self.assertEquals(d.get_b(), 10)

        def testSavedState(self):
            self.createDummyObj()
            f= OutFile()
            f.openRead()
            obj= pickle.load(f.get_fd())
            self.assertEquals(obj.get_a(), 123)
            self.assertEquals(obj.get_b(), 10)

        def testState_saveStr(self):
            d= openDummyObj()
            str= pickle.dumps(d)
            str1= d.saveStr()
            self.assertEquals(str, str1)

    unittest.main()
