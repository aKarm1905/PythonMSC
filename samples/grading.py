# coding=utf-8
"""Butterfly grading class for blockMeshDict."""
from copy import deepcopy


class SimpleGrading(object):
    """Block simpleGrading in blockMeshDict.

    Attributes:
        xGrading: Grading for X. The input can be a Grading or a MultiGrading
            (default: 1).
        yGrading: Grading for Y. The input can be a Grading or a MultiGrading
            (default: 1).
        zGrading: Grading for Z. The input can be a Grading or a MultiGrading
            (default: 1).

    Usage:
        xGrading = Grading.fromExpansionRatio(1)
        yGrading = Grading.fromExpansionRatio(1)
        zGrading = MultiGrading(
            (Grading(0.2, 0.3, 4),
            Grading(0.6, 0.4, 1),
            Grading(0.2, 0.3, 0.25))
        )

        print simpleGrading(xGrading, yGrading, zGrading)

        >> simpleGrading (
            1.0
            1.0
            (
                (0.2 0.3 4.0)
                (0.6 0.4 1.0)
                (0.2 0.3 0.25)
            )
            )
    """

    def __init__(self, xGrading=1, yGrading=1, zGrading=1):
        """Init simpleGrading class."""
        self.xGrading = self._tryReadGrading(xGrading)
        self.yGrading = self._tryReadGrading(yGrading)
        self.zGrading = self._tryReadGrading(zGrading)

    @property
    def isSimpleGrading(self):
        """Return True."""
        return True

    def _tryReadGrading(self, g):
        """Try to convert input value to grading."""
        if hasattr(g, 'isGrading'):
            assert g.isValid, \
                'You cannot use grading {} as a single grading.' \
                'Use this grading to create a MultiGrading and then use' \
                'MultiGrading to create simpleGrading.'.format(g)
            return g
        elif str(g).isdigit():
            # create grading from a single value as expansion ratio
            return Grading.fromExpansionRatio(g)
        else:
            try:
                return Grading(*tuple(g))
            except Exception as e:
                raise ValueError('Invalid input ({}). Grading should be a number '
                                 'or a tuple of numeric values.\n{}'.format(g, e))

    def toOpenFOAM(self):
        """Get blockMeshDict string.

        Args:
            vertices: list of vertices for all the geometries in the case.
            tolerance: Distance tolerance between input vertices and blockMesh
                vertices.
        """
        _body = "\nsimpleGrading (\n\t{}\n\t{}\n\t{}\n\t)"

        return _body.format(self.xGrading, self.yGrading, self.zGrading)

    def duplicate(self):
        """Return a copy of this object."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """OpenFOAM blockMeshDict boundary."""
        return self.toOpenFOAM()


class MultiGrading(object):
    """MultiGrading.

    Use this object to create MultiGrading like the example below.
        (0.2 0.3 4)    // 20% y-dir, 30% cells, expansion = 4
        (0.6 0.4 1)    // 60% y-dir, 40% cells, expansion = 1
        (0.2 0.3 0.25) // 20% y-dir, 30% cells, expansion = 0.25 (1/4)
    Read more at section 5.3.1.3: http://cfd.direct/openfoam/user-guide/blockmesh/

    Attributes:
        gradings: A list of minimum two OpenFOAM Gradings. All the gradings
            should have percentageLength and percentageCells values.
    """

    def __init__(self, gradings):
        """Init MultiGrading."""
        assert len(gradings) > 1, 'Length of gradings should be at least 2.'

        for g in gradings:
            assert hasattr(g, 'isGrading') and g.percentageCells \
                and g.percentageLength, 'Invalid input: {}'.format(g)

        self.__gradings = gradings

    @property
    def gradings(self):
        """Get gradings in this MultiGrading."""
        return self.__gradings

    @property
    def isGrading(self):
        """Return True."""
        return True

    @property
    def isValid(self):
        """Return True."""
        return True

    def duplicate(self):
        """Return a copy of this object."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """MultiGrading."""
        return '(\n\t\t{}\n\t)'.format('\n\t\t'.join(map(str, self.gradings)))


class Grading(object):
    """OpenFOAM grading.

    Use this class to create OpenFOAM grading with either a single expansion
    ration or (percentageLength, percentageCells, expansionRatio).

    Attributes:
        percentageLength: Percentage of length of the block.
        percentageCells: Percentage of cells to be included in this segment.
        expansionRatio: Expansion ration in this segment (default: 1).
    """

    def __init__(self, percentageLength=None, percentageCells=None,
                 expansionRatio=1):
        """Init a grading."""
        self.percentageLength = self._checkValues(percentageLength)
        self.percentageCells = self._checkValues(percentageCells)
        self.expansionRatio = self._checkValues(expansionRatio)

    @classmethod
    def fromExpansionRatio(cls, expansionRatio=1):
        """Create a grading with only expansionRatio."""
        return cls(expansionRatio=expansionRatio)

    @staticmethod
    def _checkValues(v):
        if not v:
            return
        try:
            return float(v)
        except TypeError:
            return int(v)

    @property
    def isGrading(self):
        """Return True."""
        return True

    @property
    def isValid(self):
        """Return True if grading is just an expansionRatio."""
        return not self.percentageCells or not self.percentageLength

    def duplicate(self):
        """Return a copy of this object."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Grading."""
        if not self.percentageCells or not self.percentageLength:
            return str(self.expansionRatio)
        else:
            return '({} {} {})'.format(self.percentageLength,
                                       self.percentageCells,
                                       self.expansionRatio)
