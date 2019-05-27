"""Collection of methods for geometrical operations."""
from vectormath.euclid import math, Vector3

def stripPointList(pts):
    if not hasattr(pts[0], '__iter__') or hasattr(pts[0], 'X'):
        return pts
    elif hasattr(pts[0][0], '__iter__') and \
        not hasattr(pts[0][0][0], '__iter__'):
        # base face has multiple faces and this is one of them
        return pts[0]
    else:
        # pts are nested than what it should be, just strip them onece more
        return stripPointList(pts[0])

def calculateNormalFromPoints(pts):
    """Calculate normal vector for a list of points.

    This method uses the pts[-1], pts[0] and pts[1] to calculate the normal
    assuming the points are representing a planar surface
    """
    # pts = stripPointList(pts)

    try:
        # vector between first point and the second point on the list
        v1 = Vector3(pts[1].X - pts[0].X,
                     pts[1].Y - pts[0].Y,
                     pts[1].Z - pts[0].Z)

        # vector between first point and the last point in the list
        v2 = Vector3(pts[-1].X - pts[0].X,
                     pts[-1].Y - pts[0].Y,
                     pts[-1].Z - pts[0].Z)
    except AttributeError:
        # vector between first point and the second point on the list
        v1 = Vector3(pts[1][0] - pts[0][0],
                     pts[1][1] - pts[0][1],
                     pts[1][2] - pts[0][2])

        # vector between first point and the last point in the list
        v2 = Vector3(pts[-1][0] - pts[0][0],
                     pts[-1][1] - pts[0][1],
                     pts[-1][2] - pts[0][2])
        return tuple(v1.cross(v2).normalize())
    except IndexError:
        raise ValueError('Length of input points should be 3!')

    else:
        return tuple(v1.cross(v2).normalize())

def calculateCenterPointFromPoints(pts):
    """Calculate center point.

    This method finds the center point by averging x, y and z values.
    """
    x, y, z = 0, 0, 0

    try:
        ptCount = float(len(pts))
        for pt in pts:
            x += pt[0]
            y += pt[1]
            z += pt[2]
    except IndexError:
        raise IndexError("Each point should be a list or a tuple with 3 values.")
    except TypeError:
        raise TypeError("Pts should be a list or a tuple of points.")

    return x / ptCount, y / ptCount, z / ptCount


def calculateVectorAngleToZAxis(vector):
    """Calculate angle between vectoe and (0, 0, 1) in degrees."""
    zAxis = Vector3(0, 0, 1)
    try:
        return math.degrees(zAxis.angle(Vector3(*vector)))
    except TypeError:
        # Vectors from Dynamo are not iterable!
        return math.degrees(zAxis.angle(Vector3(vector.X, vector.Y, vector.Z)))

if __name__ == "__main__":
    pts = ((0, 0, 0), (10, 10, 0), (10, 0, 0))
    srfVector = calculateNormalFromPoints(pts)

    print calculateVectorAngleToZAxis(srfVector)
    print calculateCenterPointFromPoints(pts)
