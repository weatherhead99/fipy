#!/usr/bin/env python

## -*-Pyth-*-
 # ###################################################################
 #  FiPy - Python-based finite volume PDE solver
 # 
 #  FILE: "uniformGrid1D.py"
 #                                    created: 2/22/06 {11:32:04 AM}
 #                                last update: 2/23/06 {3:25:02 PM} 
 #  Author: Jonathan Guyer <guyer@nist.gov>
 #  Author: Daniel Wheeler <daniel.wheeler@nist.gov>
 #  Author: James Warren   <jwarren@nist.gov>
 #    mail: NIST
 #     www: http://www.ctcms.nist.gov/fipy/
 #  
 # ========================================================================
 # This software was developed at the National Institute of Standards
 # and Technology by employees of the Federal Government in the course
 # of their official duties.  Pursuant to title 17 Section 105 of the
 # United States Code this software is not subject to copyright
 # protection and is in the public domain.  FiPy is an experimental
 # system.  NIST assumes no responsibility whatsoever for its use by
 # other parties, and makes no guarantees, expressed or implied, about
 # its quality, reliability, or any other characteristic.  We would
 # appreciate acknowledgement if the software is used.
 # 
 # This software can be redistributed and/or modified freely
 # provided that any derivative works bear some notice that they are
 # derived from it, and any modified versions bear some notice that
 # they have been modified.
 # ========================================================================
 #  
 #  Description: 
 # 
 #  History
 # 
 #  modified   by  rev reason
 #  ---------- --- --- -----------
 #  2003-11-10 JEG 1.0 original
 # ###################################################################
 ##

"""
1D Mesh
"""
__docformat__ = 'restructuredtext'

import MA

from fipy.meshes.numMesh.grid1D import Grid1D
from fipy.tools.dimensions.physicalField import PhysicalField
from fipy.tools import numerix

class UniformGrid1D(Grid1D):
    """
    Creates a 1D grid mesh.
    
        >>> mesh = UniformGrid1D(nx = 3)
        >>> print mesh.getCellCenters()
        [[ 0.5,]
         [ 1.5,]
         [ 2.5,]] 1
    """
    def __init__(self, dx = 1., nx = None, origin = (0,)):
        self.dx = PhysicalField(value = dx)
        scale = PhysicalField(value = 1, unit = self.dx.getUnit())
        self.dx /= scale
        
        self.origin = PhysicalField(value = origin)
        self.origin /= scale
        
        self.nx = self._calcNumPts(d = self.dx, n = nx)
        
        self.numberOfVertices = self.nx + 1
        self.numberOfFaces = self.nx + 1
        self.numberOfCells = self.nx
        
        self.scale = {
            'length': 1.,
            'area': 1.,
            'volume': 1.
        }
        
        self.setScale(value = scale)
        
    def __repr__(self):
        return "%s(dx = %s, nx = %d)" % (self.__class__.__name__, `self.dx`, self.nx)

    def _translate(self, vector):
        return UniformGrid1D(dx = self.dx, nx = self.nx, origin = self.origin + vector)

    def __mul__(self, factor):
        return UniformGrid1D(dx = self.dx * factor, nx = self.nx, origin = self.origin * factor)

    def _concatenate(self, other, smallNumber):
        return Mesh1D(vertexCoords = self.getVertexCoords(), 
                      faceVertexIDs = self._createFaces(), 
                      cellFaceIDs = self.createCells())._concatenate(other = other, smallNumber = smallNumber)
        
##     get topology methods

##         from common/mesh
        
    def _getCellFaceIDs(self):
        return MA.array(self._createCells())
        
    def getExteriorFaceIDs(self):
        return numerix.array([0, self.numberOfFaces-1])
        
    def getInteriorFaceIDs(self):
        return numerix.arange(self.numberOfFaces-2) + 1
            
    def _getCellFaceOrientations(self):
        orientations = numerix.ones((self.numberOfCells, 2))
        orientations[...,0] *= -1
        orientations[0,0] = 1
        return orientations

    def _getAdjacentCellIDs(self):
        c1 = numerix.arange(self.numberOfFaces)
        ids = numerix.transpose(numerix.array((c1 - 1, c1)))
        ids[0,0] = ids[0,1]
        ids[-1,1] = ids[-1,0]
        return ids[...,0], ids[...,1]

    def _getCellToCellIDs(self):
        c1 = numerix.arange(self.numberOfCells)
        ids = MA.transpose(MA.array((c1 - 1, c1 + 1)))
##         ids[0,1] = ids[0,0]
        ids[0,0] = MA.masked
##         ids[0,0] = ids[0,1]
##         ids[0,1] = MA.masked
        ids[-1,1] = MA.masked
        return ids
        
    def _getCellToCellIDsFilled(self):
        ids = self._getCellToCellIDs().filled()
        ids[0,0] = 0
        ids[-1,1] = self.numberOfCells - 1
        return ids
        
    def _getMaxFacesPerCell(self):
        return 2
        
##         from numMesh/mesh

    def getVertexCoords(self):
        return self.getFaceCenters()

    def getFaceCellIDs(self):
        c1 = numerix.arange(self.numberOfFaces)
        ids = MA.transpose(MA.array((c1 - 1, c1)))
        ids[0,0] = ids[0,1]
        ids[0,1] = MA.masked
        ids[-1,1] = MA.masked
        return ids

##     get geometry methods
        
##         from common/mesh
        
    def _getFaceAreas(self):
        return numerix.ones(self.numberOfFaces,'d')

    def _getFaceNormals(self):
        faceNormals = numerix.ones((self.numberOfFaces, 1), 'd')
        # The left-most face has neighboring cells None and the left-most cell.
        # We must reverse the normal to make fluxes work correctly.
        faceNormals[0] *= -1
        return faceNormals
        
    def getCellVolumes(self):
        return numerix.ones(self.numberOfCells, 'd') * self.dx

    def getCellCenters(self):
        return (numerix.arange(self.numberOfCells)[...,numerix.NewAxis] + 0.5) * self.dx + self.origin

    def _getCellDistances(self):
        distances = numerix.zeros(self.numberOfFaces, 'd')
        distances[1:-1] = self.dx
        distances[0] = self.dx / 2.
        distances[-1] = self.dx / 2.
        return distances

    def _getFaceToCellDistanceRatio(self):
        distances = numerix.ones(self.numberOfFaces, 'd')
        distances *= 0.5
        distances[0] = 1
        distances[-1] = 1
        return distances
        
    def _getOrientedAreaProjections(self):
        return self._getAreaProjections()

    def _getAreaProjections(self):
        return self._getFaceNormals()

    def _getOrientedFaceNormals(self):
        return self._getFaceNormals()

    def _getFaceTangents1(self):
        return numerix.zeros(self.numberOfFaces, 'd')[..., numerix.NewAxis]

    def _getFaceTangents2(self):
        return numerix.zeros(self.numberOfFaces, 'd')[..., numerix.NewAxis]
        
    def _getFaceAspectRatios(self):
        return 1. / _getCellDistances()
    
    def _getCellToCellDistances(self):
        distances = MA.zeros((self.numberOfCells,2), 'd')
        distances[:] = self.dx
        distances[0,0] = self.dx / 2.
        distances[-1,1] = self.dx / 2.
        return distances

    def _getCellNormals(self):
        normals = numerix.ones((self.numberOfCells,2,1), 'd')
        normals[...,0,:] = -1
        return normals
        
    def _getCellAreas(self):
        return numerix.ones((self.numberOfCells,2), 'd')

    def _getCellAreaProjections(self):
        return MA.array(self._getCellNormals())

##         from numMesh/mesh

    def getFaceCenters(self):
        return numerix.arange(self.numberOfFaces)[...,numerix.NewAxis] * self.dx + self.origin

    def _getCellVertexIDs(self):
        c1 = numerix.arange(self.numberOfCells)
        return numerix.transpose(numerix.array((c1 + 1, c1)))


##     scaling
    
    def _calcScaledGeometry(self):
        pass

def _test():
    import doctest
    return doctest.testmod()

if __name__ == "__main__":
    _test()
