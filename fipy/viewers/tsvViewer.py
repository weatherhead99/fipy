#!/usr/bin/env python

## -*-Pyth-*-
 # ###################################################################
 #  FiPy - Python-based finite volume PDE solver
 # 
 #  FILE: "tsvViewer.py"
 #                                    created: 3/10/05 {2:54:11 PM} 
 #                                last update: 3/15/05 {10:57:54 AM} 
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
 #  See the file "license.terms" for information on usage and  redistribution
 #  of this file, and for a DISCLAIMER OF ALL WARRANTIES.
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

__docformat__ = 'restructuredtext'

import sys

import Numeric
 
from fipy.viewers.viewer import Viewer
from fipy.variables.vectorCellVariable import VectorCellVariable

class TSVViewer(Viewer):
    
    _axis = ["x", "y", "z"]
    
    def __init__(self, vars, limits = None, title = None):
        """
        "Views" one or more variables in tab-separated-value format.
        
        Output is a list of coordinates and variable values at each cell center.
        
        File contents will be, e.g.::
            
          title
          x	y	...	var0	var2	...
          0.0	0.0	...	3.14	1.41	...
          1.0	0.0	...	2.72	0.866	...
          :
          :
        
        Any cell centers that lie outside the `limits` provided will not be included.
        Any values that lie outside the `datamin` or `datamax` of  `limits` will be 
        replaced with `nan`.
        
        All variables must have the same mesh.
        
        It tries to do something reasonable with VectorCellVariable objects.
        
        :Parameters:
          - `vars`: a `Variable` or tuple of `Variable` objects to plot
          - `limits`: a dictionary with possible keys `xmin`, `xmax`, 
            `ymin`, `ymax`, `zmin`, `zmax`, `datamin`, `datamax`.
            A 1D Viewer will only use `xmin` and `xmax`, a 2D viewer 
            will also use `ymin` and `ymax`, and so on. 
            All viewers will use `datamin` and `datamax`. 
            Any limit set to a (default) value of `None` will autoscale.
          - `title`: displayed at the top of the Viewer output
        """
        Viewer.__init__(self, vars = vars, limits = limits, title = title)
        mesh = self.vars[0].getMesh()
        
        for var in self.vars:
            assert mesh is var.getMesh()


    def plot(self, file = None):
        """
        "plot" the coordinates and values of the variables to `file`. 
        If `file` is not provided, "plots" to stdout.
        
        >>> from fipy.meshes.grid1D import Grid1D
        >>> m = Grid1D(nx = 3, dx = 0.4)
        >>> from fipy.variables.cellVariable import CellVariable
        >>> v = CellVariable(mesh = m, name = "var", value = (0, 2, 5))
        >>> TSVViewer(vars = (v, v.getGrad())).plot()
        x	var	var_grad_x
        0.2	0	2.5
        0.6	2	6.25
        1	5	3.75
        
        >>> from fipy.meshes.grid2D import Grid2D
        >>> m = Grid2D(nx = 2, dx = .1, ny = 2, dy = 0.3)
        >>> v = CellVariable(mesh = m, name = "var", value = (0, 2, -2, 5))
        >>> TSVViewer(vars = (v, v.getGrad())).plot()
        x	y	var	var_grad_x	var_grad_y
        0.05	0.15	0	10	-3.33333333333333
        0.15	0.15	2	10	5
        0.05	0.45	-2	35	-3.33333333333333
        0.15	0.45	5	35	5
        """
        if file is not None:
            f = open(file, "w")
        else:
            f = sys.stdout
        
        if self.title:
            f.write(self.title)
            f.write("\n")
            
        mesh = self.vars[0].getMesh()
        dim = mesh.getDim()
        
        headings = []
        for index in range(dim):
            headings.extend(self._axis[index])
            
        for var in self.vars:
            name = var.getName()
            if isinstance(var, VectorCellVariable):
                for index in range(dim):
                    headings.extend(["%s_%s" % (name, self._axis[index])])
            else:
                headings.extend([name])
            
        f.write("\t".join(headings))
        f.write("\n")
        
        values = mesh.getCellCenters()
        for var in self.vars:
            if isinstance(var, VectorCellVariable):
                values = Numeric.concatenate((values, Numeric.array(var)), 1)
            else:
                values = Numeric.concatenate((values, Numeric.transpose(Numeric.array((var,)))), 1)
        
        for index in range(values.shape[0]):
            lineValues = values[index]
            
            # omit any elements whose cell centers lie outside of the specified limits
            skip = False
            for axis in range(dim):
                mini = self.getLimit("%smin" % self._axis[axis])
                maxi = self.getLimit("%smax" % self._axis[axis])
                
                if (mini and lineValues[axis] < mini) or (maxi and lineValues[axis] > maxi):
                    skip = True
                    break
                    
            if skip:
                continue

            # replace any values that lie outside of the specified datalimits with 'nan'
            for valIndex in range(dim, len(lineValues)):
                mini = self.getLimit("datamin")
                maxi = self.getLimit("datamax")
                
                if (mini and lineValues[valIndex] < mini) or (maxi and lineValues[valIndex] > maxi):
                    lineValues[valIndex] = float("NaN")
                    break
            
            line = ["%.15g" % value for value in lineValues]
            f.write("\t".join(line))
            f.write("\n")

        if f is not sys.stdout:
            f.close()

def _test(): 
    import doctest
    return doctest.testmod()
    
if __name__ == "__main__": 
    _test() 
