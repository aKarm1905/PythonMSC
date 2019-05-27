from hbobject import HBObject
from vectormath.euclid import Point3
from energyplus.geometryrules import GlobalGeometryRules

from collections import namedtuple
import os


class HBZone(HBObject):
    """Honeybee base class.

    Args:
        name: Unique name for this zone.
        origin: Zone origin point (default: 0, 0, 0)
        geometryRules: EnergyPlus geometryRules. (default: "LowerLeftCorner";
            "CounterClockWise"; "Absolute")
        buildingProgram: HBZone building program.
        zoneProgram: Specific program for this zone from the available building
            programs.
        isConditioned: A boolean that indicates if the zone is conditioned.
            (default: True)
    """

    def __init__(self, name, origin=(0, 0, 0), geometryRules=None,
                 buildingProgram=None, zoneProgram=None, isConditioned=True):
        """Init Honeybee Zone."""
        self.name = name
        """Zone name"""

        self.origin = origin
        """origin of the zone."""

        self.geometryRules = geometryRules

        self.buildingProgram = buildingProgram

        self.zoneProgram = zoneProgram

        self.__surfaces = []

    @classmethod
    def fromEPString(cls, EPString, geometryRules=None, buildingProgram=None,
                     zoneProgram=None, isConditioned=True):
        """Init Honeybee zone from an EPString.

        Args:
            EPString: The full EPString for an EnergyPlus Zone.
        """
        # clean input EPString - split based on comma
        _segments = EPString.replace("\t", "") \
            .replace(" ", "").replace(";", "").split(",")

        name = _segments[1]
        try:
            north, x, y, z = _segments[2:6]
        except:
            x, y, z = 0, 0, 0

        try:
            origin = map(float, (x, y, z))
        except ValueError:
            origin = 0, 0, 0

        return cls(name, origin, geometryRules, buildingProgram, zoneProgram,
                   isConditioned)

    @property
    def isHBZone(self):
        """Return True if a HBZone."""
        return True

    @property
    def origin(self):
        """Get set origin of the zone."""
        return self.__origin

    @origin.setter
    def origin(self, value):
        try:
            self.__origin = Point3(*value)
        except:
            raise Exception("Failed to set zone origin.")

    @property
    def geometryRules(self):
        """Get and set global geometry rules for this zone."""
        return self.__geometryRules

    @geometryRules.setter
    def geometryRules(self, geometryRules):
        if not geometryRules:
            geometryRules = GlobalGeometryRules()

        self.__geometryRules = geometryRules

    @property
    def isRelativeSystem(self):
        """Return True if coordinate system is relative.

        To find the absolute coordinate values in a relative system you should
        add surface coordinates to zone origin.
        """
        return self.geometryRules.system.lower() == "relative"

    @property
    def floors(self):
        """Get floor surfaces."""
        return tuple(srf for srf in self.surfaces if srf.isFloor)

    @property
    def walls(self):
        """Get wall surfaces."""
        return tuple(srf for srf in self.surfaces if srf.isWall)

    @property
    def ceilings(self):
        """Get ceilings surfaces."""
        return tuple(srf for srf in self.surfaces if srf.isCeiling)

    @property
    def surfaces(self):
        """Get list of HBSurfaces for this zone."""
        return self.__surfaces

    def addSurface(self, HBSurface):
        """Add a surface to Honeybee zone."""
        assert hasattr(HBSurface, "isHBSurface"), \
            "%s input is not a Honeybee surface." % str(HBSurface)

        self.__surfaces.append(HBSurface)
        # update surface parent
        HBSurface.parent = self

    @property
    def radianceMaterials(self):
        """Get list of Radiance materials for zone including fenestration."""
        return set(tuple(material for srf in self.surfaces
                   for material in srf.radianceMaterials))

    def toRadString(self, includeMaterials=False, includeChildrenSurfaces=True,
                    joinOutput=True):
        """Return geometries and materials as a tuple of multiline string.

        Returns:
            if includeMaterials = False:
                A namedTuple of multiline data. Keys are: materials geometries
            else:
                A multiline string for geometries

        Usage:

            s = self.toRadString()
            geoString = s.geometries
            matString = s.materials
            or
            s = self.toRadString()
            matString, geoString = s
        """
        _radDefinition = namedtuple("RadString", "materials geometries")
        _matStr = ""
        _geoStr = ""

        if len(self.surfaces) > 0:
            _materials = []
            _geos = []
            for hbsurface in self.surfaces:
                # Both surface and fenestration material
                _materials.extend(hbsurface.radianceMaterials)
                _geos.append(hbsurface.toRadString(
                    includeMaterials=False,
                    includeChildrenSurfaces=includeChildrenSurfaces
                )
                )

            # remove duplicated materials
            _materials = set([mat.toRadString() for mat in _materials])

            if joinOutput:
                _matStr = "\n".join(_materials) + "\n"
                # joing geometries
                _geoStr = "\n".join(_geos) + "\n"
            else:
                _matStr = _materials
                _geoStr = _geos
        else:
            print "Warning: Found no Honeybee objects."

        if includeMaterials:
            if joinOutput:
                return "\n".join(_radDefinition(_matStr, _geoStr))
            else:
                return _radDefinition(_matStr, _geoStr)
        else:
            if joinOutput:
                return "\n".join(_radDefinition("", _geoStr))
            else:
                return _radDefinition("", _geoStr)

    def radStringToFile(self, filePath, includeMaterials=False,
                        includeChildrenSurfaces=True):
        """Write HBZone Radiance definition to a file.

        Args:
            filePath: Full path for a valid file path (e.g. c:/ladybug/geo.rad)

        Returns:
            True in case of success. False in case of failure.
        """
        assert os.path.isdir(os.path.split(filePath)[0]), \
            "Cannot find %s." % os.path.split(filePath)[0]

        with open(filePath, "w") as outf:
            try:
                # The output of toRadString for a zone is a tuple
                outf.write("\n".join(self.toRadString(includeMaterials,
                                                      includeChildrenSurfaces)))
                return True
            except Exception as e:
                print "Failed to write %s to file:\n%s" % (self.name, e)
                return False

    def ToString(self):
        """Overwrite .NET ToString."""
        return self.__repr__()

    def __repr__(self):
        """Zone representation."""
        if self.zoneProgram and self.buildingProgram:
            return "HBZone %s %s:%s" % (self.name, self.zoneProgram,
                                        self.buildingProgram)
        else:
            return "HBZone: %s" % self.name
