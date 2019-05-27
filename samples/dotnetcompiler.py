"""Base module for compiling dotnet sources to bytecode."""
from pyrevit import PyRevitException
from pyrevit.compat import safe_strtype
from pyrevit.framework import Array, Dictionary
from pyrevit.framework import Compiler, CSharpCodeProvider
from pyrevit.coreutils.logger import get_logger


mlogger = get_logger(__name__)   #pylint: disable=C0103


def _compile_dotnet(code_provider,
                    sourcefiles_list,
                    full_output_file_addr=None,
                    reference_list=None,
                    resource_list=None,
                   ):
    mlogger.debug('Compiling source files to: %s', full_output_file_addr)
    mlogger.debug('References assemblies are: %s', reference_list)

    compiler_params = Compiler.CompilerParameters()

    if full_output_file_addr is None:
        compiler_params.GenerateInMemory = True
    else:
        compiler_params.GenerateInMemory = False
        compiler_params.OutputAssembly = full_output_file_addr

    compiler_params.TreatWarningsAsErrors = False
    compiler_params.GenerateExecutable = False
    compiler_params.CompilerOptions = "/optimize"

    for reference in reference_list or []:
        mlogger.debug('Adding reference to compiler: %s', reference)
        compiler_params.ReferencedAssemblies.Add(reference)

    for resource in resource_list or []:
        mlogger.debug('Adding resource to compiler: %s', resource)
        compiler_params.EmbeddedResources.Add(resource)

    mlogger.debug('Compiling source files.')
    compiler = \
        code_provider.CompileAssemblyFromFile(compiler_params,
                                              Array[str](sourcefiles_list))

    if compiler.Errors.HasErrors:
        err_list = \
            [safe_strtype(err) for err in compiler.Errors.GetEnumerator()]
        err_str = '\n'.join(err_list)
        raise PyRevitException("Compile error: {}".format(err_str))

    if full_output_file_addr is None:
        mlogger.debug('Compile to memory successful: %s',
                      compiler.CompiledAssembly)
        return compiler.CompiledAssembly
    else:
        mlogger.debug('Compile successful: %s', compiler.PathToAssembly)
        return compiler.PathToAssembly


def compile_csharp(sourcefiles_list,
                   full_output_file_addr=None,
                   reference_list=None, resource_list=None):
    """Compile list of c-sharp source files to assembly.

    if full_output_file_addr is provided, the generated dll will be written
    to that file, otherwise the assembly will be generated in memory.

    Args:
        sourcefiles_list (list[str]): list of source c-sharp files
        full_output_file_addr (str): full path of output dll
        reference_list (list[str]): list of reference assemblies
        resource_list (list[str]): list of resources to be included

    Returns:
        str or System.Reflection.Assembly:
            path to assembly if dll path provided, otherwise generated assembly
    """
    mlogger.debug('Getting csharp provider.')

    cleanedup_source_list = \
        [src.replace('\\', '\\\\') for src in sourcefiles_list]

    provider = \
        CSharpCodeProvider(Dictionary[str, str]({'CompilerVersion': 'v4.0'}))

    if not provider:
        raise PyRevitException("Compile error: Can not get C# Code Provider.")

    return _compile_dotnet(provider,
                           cleanedup_source_list,
                           full_output_file_addr,
                           reference_list, resource_list)
