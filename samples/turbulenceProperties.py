# coding=utf-8
"""turbulenceProperties class.

Use turbulenceProperties for versions prior to 3.0+
"""
from foamfile import FoamFile, foamFileFromFile
from collections import OrderedDict


class TurbulenceProperties(FoamFile):
    """Turbulence Properties class."""

    # set default valus for this class
    __defaultValues = OrderedDict()
    __defaultValues['simulationType'] = 'laminar'
    __RASModels = ('LRR', 'LamBremhorstKE', 'LaunderSharmaKE', 'LienCubicKE',
                   'LienLeschziner', 'RNGkEpsilon', 'SSG', 'ShihQuadraticKE',
                   'SpalartAllmaras', 'kEpsilon', 'kOmega', 'kOmegaSSTSAS',
                   'kkLOmega', 'qZeta', 'realizableKE', 'v2f', 'buoyantKEpsilon')
    __LESModels = ('DeardorffDiffStress', 'Smagorinsky', 'SpalartAllmarasDDES',
                   'SpalartAllmarasDES', 'SpalartAllmarasIDDES', 'WALE',
                   'dynamicKEqn', 'dynamicLagrangian', 'kEqn', 'kOmegaSSTDES')

    def __init__(self, values=None):
        """Init class."""
        FoamFile.__init__(self, name='turbulenceProperties', cls='dictionary',
                          location='constant', defaultValues=self.__defaultValues,
                          values=values)

    @classmethod
    def fromFile(cls, filepath):
        """Create a FoamFile from a file.

        Args:
            filepath: Full file path to dictionary.
        """
        return cls(values=foamFileFromFile(filepath, cls.__name__))

    @classmethod
    def laminar(cls):
        """Laminar model."""
        return cls()

    @classmethod
    def RAS(cls, RASModel='RNGkEpsilon', turbulence=True, printCoeffs=True,
            RASModelCoeffs=None):
        """Reynolds-averaged simulation (RAS) turbulence model.

        Read more: http://cfd.direct/openfoam/user-guide/turbulence/
        Watch this: https://www.youtube.com/watch?v=Eu_4ppppQmw

        Args:
            RASModel: Name of RAS turbulence model (default: RNGkEpsilon).
                Incompressible RAS turbulence models:
                    LRR, LamBremhorstKE, LaunderSharmaKE, LienCubicKE,
                    LienLeschziner, RNGkEpsilon, SSG, ShihQuadraticKE,
                    SpalartAllmaras, kEpsilon, kOmega, kOmegaSSTSAS, kkLOmega,
                    qZeta, realizableKE, v2f
                Compressible RAS turbulence models:
                    LRR, LaunderSharmaKE, RNGkEpsilon, SSG, SpalartAllmaras,
                    buoyantKEpsilon, kEpsilon, kOmega, kOmegaSSTSAS,
                    realizableKE, v2f
            turbulence: Boolean switch to turn the solving of turbulence
                modelling on/off (default: True).
            printCoeffs: Boolean switch to print model coeffs to terminal at
                simulation start up (default: True).
            RASModelCoeffs: Optional dictionary of coefficients for the respective
                RASModel, to override the default coefficients.
        """
        # check RASModel input
        assert RASModel in cls.__RASModels, \
            '{} is not a valid input for RASModel.' \
            ' Try one of the models below:\n{}'.format(RASModel, cls.__RASModels)

        values = {'simulationType': 'RAS', 'RAS': {
            'RASModel': RASModel,
            'turbulence': FoamFile.convertBoolValue(turbulence),
            'printCoeffs': FoamFile.convertBoolValue(printCoeffs)}
        }

        if RASModelCoeffs:
            values['RAS'].update({'%sCoeffs' % RASModel: RASModelCoeffs})

        return cls(values=values)

    @classmethod
    def LES(cls, LESModel='kEqn', delta='cubeRootVol', turbulence=True,
            printCoeffs=True, LESModelCoeffs=None, deltaCoeffs=None):
        """Large eddy simulation (LES) modelling.

        Args:
            LESModel: Name of LES turbulence model.
                Incompressible LES turbulence models.
                    DeardorffDiffStress, Smagorinsky, SpalartAllmarasDDES,
                    SpalartAllmarasDES, SpalartAllmarasIDDES, WALE, dynamicKEqn,
                    dynamicLagrangian, kEqn, kOmegaSSTDES
                Compressible LES turbulence models.
                    DeardorffDiffStress, Smagorinsky, SpalartAllmarasDDES,
                    SpalartAllmarasDES, SpalartAllmarasIDDES, WALE, dynamicKEqn,
                    dynamicLagrangian, kEqn, kOmegaSSTDES
            delta: Name of delta model.
            turbulence: Boolean switch to turn the solving of turbulence
                modelling on/off (default: True).
            printCoeffs: Boolean switch to print model coeffs to terminal at
                simulation start up (default: True).
            LESModelCoeffs: Dictionary of coefficients for the respective LESModel,
                to override the default coefficients.
            deltaCoeffs: Dictionary of coefficients for the delta model.
        """
        assert LESModel in cls.__LESModels, \
            '{} is not a valid input for LESModels.' \
            ' Try one of the models below:\n{}'.format(LESModel, cls.__LESModels)

        values = {'simulationType': 'LES', 'LES': {
            'LESModel': LESModel,
            'delta': delta,
            'turbulence': FoamFile.convertBoolValue(turbulence),
            'printCoeffs': FoamFile.convertBoolValue(printCoeffs)}
        }

        if LESModelCoeffs:
            values['LES'].update({'%sCoeffs' % LESModel: LESModelCoeffs})

        if deltaCoeffs:
            values['LES'].update({'%sCoeffs' % deltaCoeffs: deltaCoeffs})

        return cls(values=values)

    @property
    def isTurbulenceProperties(self):
        """Return True."""
        return True
