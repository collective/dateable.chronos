# -*- coding: ISO-8859-15 -*-
# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Author: Lennart Regebro <mailto:regebro@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id: displaytable.py 24473 2005-06-27 12:20:19Z lregebro $

"""
  This is a library of support objects for making HTML tables
"""

import copy
from UserList import UserList
#from ExtensionClass import Base

def area_cmp(a, b):
    """Compares two areas on area. Smaller comes first."""
    area_a = a.getRowSpan() * a.getColSpan()
    area_b = b.getRowSpan() * b.getColSpan()
    if area_a < area_b: return -1
    if area_a > area_b: return 1
    return 0

class TwoDimensionalArea:
    """This is a baseclass for almost everything."""
    __allow_access_to_unprotected_subobjects__ = 1
    
    def getFirstRow(self):
        return self.firstrow

    def setFirstRow(self, value):
        if self.getLastRow() <= value:
            raise ValueError('Cells can not have zero or negative size')
        self.firstrow = value

    def getLastRow(self):
        return self.lastrow

    def setLastRow(self, value):
        if self.getFirstRow() >= value:
            raise ValueError('Cells can not have zero or negative size')
        self.lastrow = value

    def getFirstCol(self):
        return self.firstcol

    def setFirstCol(self, value):
        if self.getLastCol() <= value:
            raise ValueError('Cells can not have zero or negative size')
        self.firstcol = value

    def getLastCol(self):
        return self.lastcol

    def setLastCol(self, value):
        if self.getFirstCol() >= value:
            raise ValueError('Cells can not have zero or negative size')
        self.lastcol = value

    def getRowSpan(self):
        return self.getLastRow() - self.getFirstRow()

    def getColSpan(self):
        return self.getLastCol() - self.getFirstCol()

    def __cmp__(self, other):
        if not isinstance(other, TwoDimensionalArea):
            return -1
        
        if other.getFirstRow() > self.getFirstRow():
            return -1
        if other.getFirstRow() < self.getFirstRow():
            return 1
        if other.getFirstCol() > self.getFirstCol():
            return -1
        if other.getFirstCol() < self.getFirstCol():
            return 1
        if other.getLastRow() > self.getLastRow():
            return -1
        if other.getLastRow() < self.getLastRow():
            return 1
        if other.getLastCol() > self.getLastCol():
            return -1
        if other.getLastCol() < self.getLastCol():
            return 1
        return 0

    def __str__(self):
        return '<%s %s, %s, %s, %s >' % (str(self.__class__),
            self.getFirstRow(),  self.getFirstCol(),
            self.getLastRow(), self.getLastCol())
            
            
class Cell(TwoDimensionalArea):
    """A singularity in areas. Has no subareas."""
    def __init__(self, firstrow, firstcol, lastrow, lastcol):
        if lastrow <= firstrow or lastcol <= firstcol:
            raise ValueError('Cells can not have zero or negative size')
        self.firstrow = firstrow
        self.firstcol = firstcol
        self.lastrow = lastrow
        self.lastcol = lastcol

    def willYield(self, cell):
        """Checks if this cell will give up space to the other"""
        # By default, never yield
        return 0

    def mask(self, cell):
        pass
    
class BackgroundCell(Cell):
    """A cell that do not conflict with overlapping cells."""

    def willYield(self, cell):
        """Checks if this cell will give up space to the other"""
        # Don't  yield to other background cells.
        if isinstance(cell, BackgroundCell):
            return 0
        return 1


class Grid(UserList, TwoDimensionalArea):
    """An area containing several smaller non-overlapping areas"""

    def __str__(self):
        res = '<%s %s, %s, %s, %s containing' % (str(self.__class__),
            self.getFirstRow(),  self.getFirstCol(),
            self.getLastRow(), self.getLastCol())
        for each in self.data:
            res += ' ' + str(each)
        return res
                
    def getFirstRow(self):
        if len(self) == 0:
            return 0
        val = self.data[0].getFirstRow()
        for each in self.data[1:]:
            if each.getFirstRow() < val:
                val = each.getFirstRow()
        return val

    def getLastRow(self):
        if len(self) == 0:
            return 0
        val = self.data[0].getLastRow()
        for each in self.data[1:]:
            if each.getLastRow() > val:
                val = each.getLastRow()
        return val

    def getFirstCol(self):
        if len(self) == 0:
            return 0
        val = self.data[0].getFirstCol()
        for each in self.data[1:]:
            if each.getFirstCol() < val:
                val = each.getFirstCol()
        return val

    def getLastCol(self):
        if len(self) == 0:
            return 0
        val = self.data[0].getLastCol()
        for each in self.data[1:]:
            if each.getLastCol() > val:
                val = each.getLastCol()
        return val

    # Cell crunching
    def splitCells(self, cell, newcell):
        if cell.getFirstCol() < newcell.getFirstCol():
            mincol = cell.getFirstCol()
        else:
            mincol = newcell.getFirstCol()
        if cell.getLastCol() > newcell.getLastCol():
            maxcol = cell.getLastCol()
        else:
            maxcol = newcell.getLastCol()
        medium = (maxcol + mincol)/2
        if maxcol - mincol < 2:
            # We need to split this column in two.
            self.splitColumn(medium)
            medium += 1
        if cell.getLastCol() <= medium:
            newcell.setFirstCol(cell.getLastCol())
        elif newcell.getLastCol() <= medium:
            cell.setFirstCol(newcell.getLastCol())
        else:
            cell.setLastCol(medium)
            newcell.setFirstCol(medium)

    def maskCell(self, backgroundcell, maskingcell):
        """Splits a yeilding cell into several new cells"""
        
        # There is a maximum of 9 cells, the middle one  1 2 3
        # is the mask cell which we call 0, and the      4 0 5
        # remaining eight are positioned as shown here:  6 7 8
        
        # The celldimensions:
        backRfrom = backgroundcell.getFirstRow()
        backCfrom = backgroundcell.getFirstCol()
        backRto = backgroundcell.getLastRow()
        backCto = backgroundcell.getLastCol()
        maskRfrom = maskingcell.getFirstRow()
        maskCfrom = maskingcell.getFirstCol()
        maskRto = maskingcell.getLastRow()
        maskCto = maskingcell.getLastCol()
        
        if maskRfrom < backRfrom:
            midRfrom = backRfrom
        else:
            midRfrom = maskRfrom
        
        if maskCfrom < backCfrom:
            midCfrom = backCfrom
        else:
            midCfrom = maskCfrom
        
        if maskRto > backRto:
            midRto = backRto
        else:
            midRto = maskRto
        
        if maskCto > backCto:
            midCto = backCto
        else:
            midCto = maskCto
            
        # The dimensions of the 8 resulting cells:
        cell1 = (backRfrom, backCfrom, midRfrom, midCfrom)
        cell2 = (backRfrom, midCfrom, midRfrom, midCto)
        cell3 = (backRfrom, midCto, midRfrom, backCto)
        cell4 = (midRfrom, backCfrom, midRto, midCfrom)
        cell5 = (midRfrom, midCto, midRto, backCto)
        cell6 = (midRto, backCfrom, backRto, midCfrom)
        cell7 = (midRto, midCfrom, backRto, midCto)
        cell8 = (midRto, midCto, backRto, backCto)
        
        res = []
        for cell in (cell1, cell2, cell3, cell4, cell5, cell6, cell7, cell8):
            if (cell[2] > cell[0] and cell[3] > cell[1]):
                # This cell has dimensions.
                newcell = copy.deepcopy(backgroundcell)
                newcell.setLastCol(cell[3])
                newcell.setLastRow(cell[2])
                newcell.setFirstCol(cell[1])
                newcell.setFirstRow(cell[0])
                res.append(newcell)
        # Done!
        return res
                        
    def append(self, newcell):
        # XXX: If the new cell conflict with several existing cells
        # results are unpredictable at best... 
        # Check for conflict
        newcells = [newcell]
        for cell in self:
            if self.checkForConflict(cell, newcell):
                # First check if any of the cells will yield.
                if cell.willYield(newcell):
                    # Masking can result in one cell becoming several cells.
                    # So we need to remove the cell and then add the result.
                    self.remove(cell)
                    newcells.extend(self.maskCell(cell, newcell))
                elif newcell.willYield(cell):
                    newcells = self.maskCell(newcell, cell)
                else:
                    # Currently resolve by putting conflicting cells besides
                    # each other. This may become a setting in the future.
                    self.splitCells(cell,newcell)
        self.data.extend(newcells)

    def sortOnArea(self, other=None):
        """Sort list of cells on area, with smallest first."""
        
        if other is None:
            other = self
        
        return other.sort(area_cmp)
    
    def checkForConflict(self, first, second):
        # First check for height
        if first.getFirstRow() >= second.getLastRow() or \
           first.getLastRow() <= second.getFirstRow():
            # No conflict
            return 0

        if first.getFirstCol() >= second.getLastCol() or \
           first.getLastCol() <= second.getFirstCol():
            # No conflict
            return 0
        # Yes, there is a conflict
        return 1

    def splitColumn(self, column, count=1):
        """Inserts new columns, shifting everything right"""
        for cell in self:
            first = cell.getFirstCol()
            last = cell.getLastCol()
            if last > column:
                cell.setLastCol(last+count)
            if first > column:
                cell.setFirstCol(first+count)

    def splitRow(self, row, count=1):
        """Inserts new rows, shifting everything down"""
        for cell in self:
            first = cell.getFirstRow()
            last = cell.getLastRow()
            if last > row:
                cell.setLastRow(last+count)
            if first > row:
                cell.setFirstRow(first+count)

    def insertGridByRow(self, newgrid, row):
        """Merges in another grid into a space inserted into this grid"""
        # I'm not sure what this is for, actually.... /LRE
        gridheight = newgrid.getLastRow()
        # Insert the new space:
        self.splitRow(row, gridheight)
        # Shift all cells in the newgrid down to their
        # positions in the merged grid
        for cell in newgrid:
            cell.setLastRow(cell.getLastRow()+row)
            cell.setFirstRow(cell.getFirstRow()+row)
        # And merge the grids
        self.extend(newgrid)

    def flatten(self):
        """Flattens grid
        
        This function converts all GridCells to pure Cells. This is done
        before rendering if you don't want tables in tables.
        """
        for cell in self.data[:]:
            if isinstance(cell, Grid):
                # First replace with a background cell
                # Don't worry. We still have a reference to the cell
                # in the cell variable. The cell will not get garbage 
                # collected until all references are dropped. I hope. :)
                self.data.remove(cell)
                self.append(BackgroundCell(cell.getFirstRow(),
                    cell.getFirstCol(), cell.getLastRow(), cell.getLastCol()))
                cell.flatten()
                # Check if a split is needed. 
                grid_size = cell.getRowSpan()
                cell_size = cell.getLastCellRow()
                if cell_size > grid_size:
                    self.splitRow(cell.getFirstRow(), cell_size-grid_size)
        
                grid_size = cell.getColSpan()
                cell_size = cell.getLastCellCol()
                if cell_size > grid_size:
                    self.splitColumn(cell.getFirstCol(), cell_size-grid_size)
                    
                insertrow = cell.getFirstRow()
                insertcol = cell.getFirstCol()
                for subcell in cell.data:
                    subcell.setLastRow(subcell.getLastRow() + insertrow)
                    subcell.setFirstRow(subcell.getFirstRow() + insertrow)
                    subcell.setLastCol(subcell.getLastCol() + insertcol)
                    subcell.setFirstCol(subcell.getFirstCol() + insertcol)
                    self.append(subcell)
        self.sort()
    
    def isConflicting(self, cell):
        for each in self.data:
            if self.checkForConflict(each, cell):
                return 1
        return 0
            
    def extend(self, other):
        other.sort(area_cmp)
        defer_list = []
        for each in other:
            # Start with adding everything that does not conflict.
            # (Yes, this means that if you start with something that causes
            # major conflict, this is not much of an improvement, which is
            # why we sorted for area first, in the hope that small areas will
            # conflict with less stuff.
            if self.isConflicting(each):
                defer_list.append(each)
            else:
                self.append(each)
        
        for each in defer_list:
            self.append(each)


class SizedGrid(Grid):
    """A grid with "physical" size.

    This grid has size and position as well as columns and rows.
    The size and position (top, left, height, width attributes)
    are used to calculate the final sizes of the cells.
    While actually creating the cells, sizes should only be relative 
    to each other.
    """

    def __init__(self, top=0, left=0, height=0, width=0):
        Grid.__init__(self)
        self.top = top
        self.left = left
        self.height = height
        self.width = width

    def flatten(self):
        Grid.flatten(self)
        row_scale = float(self.height) / float(self.getLastRow())
        col_scale = float(self.width) / float(self.getLastCol())
        for each in self.data:
            each.setLastRow(int(each.getLastRow() * row_scale) + self.top)
            each.setLastCol(int(each.getLastCol() * col_scale) + self.left)
            each.setFirstRow(int(each.getFirstRow() * row_scale) + self.top)
            each.setFirstCol(int(each.getFirstCol() * col_scale) + self.left)

# Not used, but could maybe be useful?
class GridCell(Cell, Grid):
    """A Cell that contains other Cells"""
    # The dimensions of the cell as it appears outwardly are fixed, even when
    # internal size is larger that outward size. When merging, the maximum of
    # the cells getLastX and the Grids getLastX are used.
    def __init__(self, firstrow, firstcol, lastrow, lastcol):
        Cell.__init__(self, firstrow, firstcol, lastrow, lastcol)
        Grid.__init__(self)

    def getLastCellRow(self):
        last = 0
        for cell in self.data:
            if cell.getLastRow() > last:
                last = cell.getLastRow()
        return last
                        
    def getLastCellCol(self):
        last = 0
        for cell in self.data:
            if cell.getLastCol() > last:
                last = cell.getLastCol()
        return last

#####################################
## Special calendar support stuff
## Move to the view classes?
#####################################
class DayGrid(SizedGrid):
    """A Sized grid that does not recalculate height."""
    def flatten(self):
        if len(self) == 0:
            return
        Grid.flatten(self)
        col_scale = float(self.width) / float(self.getLastCol())
        for each in self.data:
            each.setLastCol(int(each.getLastCol() * col_scale) + self.left)
            each.setFirstCol(int(each.getFirstCol() * col_scale) + self.left)

