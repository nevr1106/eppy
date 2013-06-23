# Copyright (c) 2012 Santosh Philip

# This file is part of eppy.

# Eppy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Eppy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with eppy.  If not, see <http://www.gnu.org/licenses/>.

"""py.test for modeleditor"""

import bunch
import idfreader
import modeleditor
import snippet

from iddcurrent import iddcurrent
iddsnippet = iddcurrent.iddtxt

idfsnippet = snippet.idfsnippet

from StringIO import StringIO
idffhandle = StringIO(idfsnippet)
iddfhandle = StringIO(iddsnippet)
bunchdt, data, commdct = idfreader.idfreader(idffhandle, iddfhandle)

# idd is read only once in this test
from modeleditor import IDF
from iddcurrent import iddcurrent
iddfhandle1 = StringIO(iddcurrent.iddtxt)
IDF.setiddname(iddfhandle1)

def test_poptrailing():
    """py.test for poptrailing"""
    data = (([1, 2, 3, '', 56, '', '', '', ''], 
        [1, 2, 3, '', 56]), # lst, poped
        ([1, 2, 3, '', 56], 
        [1, 2, 3, '', 56]), # lst, poped
        ([1, 2, 3, 56], 
        [1, 2, 3, 56]), # lst, poped
    )

def test_extendlist():
    """py.test for extendlist"""
    data = (([1,2,3], 2, 0, [1,2,3]), # lst, i, value, nlst
    ([1,2,3], 3, 0, [1,2,3,0]), # lst, i, value, nlst
    ([1,2,3], 5, 0, [1,2,3,0,0,0]), # lst, i, value, nlst
    ([1,2,3], 7, 0, [1,2,3,0,0,0,0,0]), # lst, i, value, nlst
    )
    for lst, i, value, nlst in data:
        modeleditor.extendlist(lst, i, value=value)
        assert lst == nlst

def test_newrawobject():
    """py.test for newrawobject"""
    thedata = (('zone'.upper(), 
        ['ZONE', '', '0', '0', '0', '0', '1', '1', 'autocalculate', 
            'autocalculate', 'autocalculate', '', '', 'Yes']), # key, obj
    )
    for key, obj in thedata:
        result = modeleditor.newrawobject(data, commdct, key)
        assert result == obj
        
def test_obj2bunch():
    """py.test for obj2bunch"""
    thedata = ((['ZONE', '', '0', '0', '0', '0', '1', '1', 'autocalculate', 
        'autocalculate', 'autocalculate', '', '', 'Yes']), # obj
    )
    for obj in thedata:
        key_i = data.dtls.index(obj[0].upper())
        abunch = idfreader.makeabunch(commdct, obj, key_i)
        result = modeleditor.obj2bunch(data, commdct, obj)
        assert result == abunch
    
def test_namebunch():
    """py.test for namebunch"""
    thedata = ((bunch.Bunch(dict(Name="", a=5)), 
        "yay", "yay"), # abunch, aname, thename
        (bunch.Bunch(dict(Name=None, a=5)), 
            "yay", None), # abunch, aname, thename
    )
    for abunch, aname, thename in thedata:
        result = modeleditor.namebunch(abunch, aname)
        assert result.Name == thename
        
def test_addobject():
    """py.test for addobject"""
    thedata = (('ZONE', 'karamba'), # key, aname
    )
    for key, aname in thedata:
        result = modeleditor.addobject(bunchdt, data, commdct, key, aname)
        assert data.dt[key][-1][1] == aname
        assert bunchdt[key][-1].Name == aname
        
def test_getnamedargs():
    """py.test for getnamedargs"""
    result = dict(a=1, b=2, c=3)
    assert result == modeleditor.getnamedargs(a=1, b=2, c=3)
    assert result == modeleditor.getnamedargs(dict(a=1, b=2, c=3))
    assert result == modeleditor.getnamedargs(dict(a=1, b=2), c=3)
    assert result == modeleditor.getnamedargs(dict(a=1), c=3, b=2)
    
def test_addobject1():
    """py.test for addobject"""
    thedata = (('ZONE', {'Name':'karamba'}), # key, kwargs
    )
    for key, kwargs in thedata:
        result = modeleditor.addobject1(bunchdt, data, commdct, key, kwargs)
        aname = kwargs['Name']
        assert data.dt[key][-1][1] == aname
        assert bunchdt[key][-1].Name == aname        
        
def test_getobject():
    """py.test for getobject"""
    thedata = (
        ('ZONE', 'PLENUM-1', 
            bunchdt['ZONE'][0]), # key, name, theobject
        ('ZONE', 'PLENUM-1'.lower(), 
            bunchdt['ZONE'][0]), # key, name, theobject
        ('ZONE', 'PLENUM-A', 
            None), # key, name, theobject
    )
    for key, name, theobject in thedata:
        result = modeleditor.getobject(bunchdt, key, name)
        assert result == theobject
        
def test_iddofobject():
    """pytest of iddofobject"""
    thedata = (('VERSION', 
                [{'format': ['singleLine'], 'unique-object': ['']},
                {'default': ['7.0'], 'field': ['Version Identifier'], 
                'required-field': ['']}]), # key, itsidd
    )
    for key, itsidd in thedata:
        result = modeleditor.iddofobject(data, commdct, key)
        result[0].pop('memo') # memo is new in version 8.0.0
        assert result == itsidd


def test_removeextensibles():
    """py.test for removeextensibles"""
    thedata = (("BuildingSurface:Detailed".upper(), "WALL-1PF",
    ["BuildingSurface:Detailed", "WALL-1PF", "WALL", "WALL-1", "PLENUM-1", 
    "Outdoors","", "SunExposed", "WindExposed", 0.50000, '4',] ), # key, objname, rawobject
    )
    for key, objname, rawobject in thedata:
        result = modeleditor.removeextensibles(bunchdt, data, commdct, key, 
                                                objname)
        assert result.obj == rawobject

def test_getrefnames():
    """py.test for getrefnames"""
    tdata = (
    ('ZONE', 
    ['ZoneNames', 'OutFaceEnvNames', 'ZoneAndZoneListNames', 
    'AirflowNetworkNodeAndZoneNames']), # objkey, therefs
    ('FluidProperties:Name'.upper(), 
    ['FluidNames', 'FluidAndGlycolNames']), # objkey, therefs
    ('Building'.upper(), 
    []), # objkey, therefs
    )
    for objkey, therefs in tdata:
        fhandle = StringIO("")
        idf = IDF(fhandle)
        result = modeleditor.getrefnames(idf, objkey)
        assert result == therefs

def test_getallobjlists():
    """py.test for getallobjlists"""
    tdata = (
    ('TransformerNames', 
    [('ElectricLoadCenter:Distribution'.upper(), 
    'TransformerNames',
    [10, ]
    ), ],
    ), # refname, objlists
    )
    for refname, objlists in tdata:
        fhandle = StringIO("")
        idf = IDF(fhandle)
        result = modeleditor.getallobjlists(idf, refname)
        assert result == objlists

def test_rename():
    """py.test for rename"""
    idftxt = """Material,
      G01a 19mm gypsum board,  !- Name
      MediumSmooth,            !- Roughness
      0.019,                   !- Thickness {m}
      0.16,                    !- Conductivity {W/m-K}
      800,                     !- Density {kg/m3}
      1090;                    !- Specific Heat {J/kg-K}

      Construction,
        Interior Wall,           !- Name
        G01a 19mm gypsum board,  !- Outside Layer
        F04 Wall air space resistance,  !- Layer 2
        G01a 19mm gypsum board;  !- Layer 3

    """
    ridftxt = """Material,
      peanut butter,  !- Name
      MediumSmooth,            !- Roughness
      0.019,                   !- Thickness {m}
      0.16,                    !- Conductivity {W/m-K}
      800,                     !- Density {kg/m3}
      1090;                    !- Specific Heat {J/kg-K}

      Construction,
        Interior Wall,           !- Name
        peanut butter,  !- Outside Layer
        F04 Wall air space resistance,  !- Layer 2
        peanut butter;  !- Layer 3

    """
    fhandle = StringIO(idftxt)
    idf = IDF(fhandle)
    result = modeleditor.rename(idf, 
            'Material'.upper(), 
            'G01a 19mm gypsum board', 'peanut butter')
    assert result.Name == 'peanut butter'
    assert idf.idfobjects['CONSTRUCTION'][0].Outside_Layer == 'peanut butter'                       
    assert idf.idfobjects['CONSTRUCTION'][0].Layer_3 == 'peanut butter'