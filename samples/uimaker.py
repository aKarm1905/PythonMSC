"""UI maker."""
import imp

from pyrevit import HOST_APP, EXEC_PARAMS, PyRevitException
from pyrevit.coreutils import find_loaded_asm
from pyrevit.coreutils.logger import get_logger

if not EXEC_PARAMS.doc_mode:
    from pyrevit.coreutils import ribbon

#pylint: disable=W0703,C0302,C0103,C0413
from pyrevit.extensions import components
from pyrevit.extensions import TAB_POSTFIX, PANEL_POSTFIX,\
    STACKTWO_BUTTON_POSTFIX, STACKTHREE_BUTTON_POSTFIX, \
    PULLDOWN_BUTTON_POSTFIX, SPLIT_BUTTON_POSTFIX, SPLITPUSH_BUTTON_POSTFIX, \
    PUSH_BUTTON_POSTFIX, TOGGLE_BUTTON_POSTFIX, SMART_BUTTON_POSTFIX,\
    LINK_BUTTON_POSTFIX, SEPARATOR_IDENTIFIER, SLIDEOUT_IDENTIFIER,\
    PANEL_PUSH_BUTTON_POSTFIX


mlogger = get_logger(__name__)


CONFIG_SCRIPT_TITLE_POSTFIX = u'\u25CF'


class UIMakerParams:
    def __init__(self, par_ui, par_cmp, cmp_item, asm_info, create_beta=False):
        self.parent_ui = par_ui
        self.parent_cmp = par_cmp
        self.component = cmp_item
        self.asm_info = asm_info
        self.create_beta_cmds = create_beta


def _make_button_tooltip(button):
    tooltip = button.doc_string + '\n\n' if button.doc_string else ''
    tooltip += 'Bundle Name:\n{} ({})'\
        .format(button.name, button.type_id.replace('.', ''))
    if button.author:
        tooltip += '\n\nAuthor(s):\n{}'.format(button.author)
    return tooltip


def _make_button_tooltip_ext(button, asm_name):

    tooltip_ext = ''

    if button.min_revit_ver and not button.max_revit_ver:
        tooltip_ext += 'Compatible with {} {} and above\n\n'\
            .format(HOST_APP.proc_name,
                    button.min_revit_ver)

    if button.max_revit_ver and not button.min_revit_ver:
        tooltip_ext += 'Compatible with {} {} and earlier\n\n'\
            .format(HOST_APP.proc_name,
                    button.max_revit_ver)

    if button.min_revit_ver and button.max_revit_ver:
        if int(button.min_revit_ver) != int(button.max_revit_ver):
            tooltip_ext += 'Compatible with {} {} to {}\n\n'\
                .format(HOST_APP.proc_name,
                        button.min_revit_ver, button.max_revit_ver)
        else:
            tooltip_ext += 'Compatible with {} {} only\n\n'\
                .format(HOST_APP.proc_name,
                        button.min_revit_ver)

    tooltip_ext += 'Class Name:\n{}\n\nAssembly Name:\n{}'\
        .format(button.unique_name, asm_name)

    return tooltip_ext


def _make_ui_title(button):
    if button.has_config_script():
        return button.ui_title + ' {}'.format(CONFIG_SCRIPT_TITLE_POSTFIX)
    else:
        return button.ui_title


def _make_full_class_name(asm_name, class_name):
    if asm_name is None or class_name is None:
        return None
    else:
        return '{}.{}'.format(asm_name, class_name)


def _get_effective_classname(button):
    """
    Verifies if button has class_name set. This means that typemaker has
    created a executor type for this command. If class_name is not set,
    this function returns button.unique_name. This allows for the UI button
    to be created and linked to the previously created assembly.
    If the type does not exist in the assembly, the UI button will not work,
    however this allows updating the command with the correct executor type,
    once command script has been fixed and pyrevit is reloaded.

    Args:
        button (pyrevit.extensions.genericcomps.GenericUICommand):

    Returns:
        str: class_name (or unique_name if class_name is None)

    """
    return button.class_name if button.class_name else button.unique_name


def _produce_ui_separator(ui_maker_params):
    """

    Args:
        ui_maker_params (UIMakerParams): Standard parameters for making ui item
    """
    parent_ui_item = ui_maker_params.parent_ui
    ext_asm_info = ui_maker_params.asm_info

    if not ext_asm_info.reloading:
        mlogger.debug('Adding separator to: %s', parent_ui_item)
        try:
            if hasattr(parent_ui_item, 'add_separator'):    # re issue #361
                parent_ui_item.add_separator()
        except PyRevitException as err:
            mlogger.error('UI error: %s', err.msg)

    return None


def _produce_ui_slideout(ui_maker_params):
    """

    Args:
        ui_maker_params (UIMakerParams): Standard parameters for making ui item
    """
    parent_ui_item = ui_maker_params.parent_ui
    ext_asm_info = ui_maker_params.asm_info

    if not ext_asm_info.reloading:
        mlogger.debug('Adding slide out to: %s', parent_ui_item)
        try:
            parent_ui_item.add_slideout()
        except PyRevitException as err:
            mlogger.error('UI error: %s', err.msg)

    return None


def _produce_ui_smartbutton(ui_maker_params):
    """

    Args:
        ui_maker_params (UIMakerParams): Standard parameters for making ui item
    """
    parent_ui_item = ui_maker_params.parent_ui
    parent = ui_maker_params.parent_cmp
    smartbutton = ui_maker_params.component
    ext_asm_info = ui_maker_params.asm_info

    if not smartbutton.is_supported:
        return None

    if smartbutton.beta_cmd and not ui_maker_params.create_beta_cmds:
        return None

    mlogger.debug('Producing smart button: %s', smartbutton)
    try:
        parent_ui_item.create_push_button(
            button_name=smartbutton.name,
            asm_location=ext_asm_info.location,
            class_name=_get_effective_classname(smartbutton),
            icon_path=smartbutton.icon_file or parent.icon_file,
            tooltip=_make_button_tooltip(smartbutton),
            tooltip_ext=_make_button_tooltip_ext(smartbutton,
                                                 ext_asm_info.name),
            tooltip_image=smartbutton.ttimage_file,
            tooltip_video=smartbutton.ttvideo_file,
            ctxhelpurl=smartbutton.get_help_url() or '',
            avail_class_name=smartbutton.avail_class_name,
            update_if_exists=True,
            ui_title=_make_ui_title(smartbutton))
    except PyRevitException as err:
        mlogger.error('UI error: %s', err.msg)
        return None

    new_uibutton = parent_ui_item.button(smartbutton.name)
    mlogger.debug('Importing smart button as module: %s', smartbutton)
    try:
        # replacing EXEC_PARAMS.command_name value with button name so the
        # init script can log under its own name
        prev_commandname = \
            __builtins__['__commandname__'] \
            if '__commandname__' in __builtins__ else None
        prev_commandpath = \
            __builtins__['__commandpath__'] \
            if '__commandpath__' in __builtins__ else None
        prev_shiftclick = \
            __builtins__['__shiftclick__'] \
            if '__shiftclick__' in __builtins__ else False
        prev_debugmode = \
            __builtins__['__forceddebugmode__'] \
            if '__forceddebugmode__' in __builtins__ else False

        __builtins__['__commandname__'] = smartbutton.name
        __builtins__['__commandpath__'] = smartbutton.get_full_script_address()
        __builtins__['__shiftclick__'] = False
        __builtins__['__forceddebugmode__'] = False
    except Exception as err:
        mlogger.error('Smart button import setup: %s | %s', smartbutton, err)
        return new_uibutton

    try:
        # importing smart button script as a module
        importedscript = imp.load_source(smartbutton.unique_name,
                                         smartbutton.script_file)
        # resetting EXEC_PARAMS.command_name to original
        __builtins__['__commandname__'] = prev_commandname
        __builtins__['__commandpath__'] = prev_commandpath
        __builtins__['__shiftclick__'] = prev_shiftclick
        __builtins__['__forceddebugmode__'] = prev_debugmode
        mlogger.debug('Import successful: %s', importedscript)
        mlogger.debug('Running self initializer: %s', smartbutton)

        res = False
        try:
            # running the smart button initializer function
            res = importedscript.__selfinit__(smartbutton,
                                              new_uibutton, HOST_APP.uiapp)
        except Exception as button_err:
            mlogger.error('Error initializing smart button: %s | %s',
                          smartbutton, button_err)

        # if the __selfinit__ function returns False
        # remove the button
        if res is False:
            mlogger.debug('SelfInit returned False on Smartbutton: %s',
                          new_uibutton)
            new_uibutton.deactivate()

        mlogger.debug('SelfInit successful on Smartbutton: %s', new_uibutton)
        return new_uibutton
    except Exception as err:
        mlogger.error('Smart button script import error: %s | %s',
                      smartbutton, err)
        return new_uibutton


def _produce_ui_linkbutton(ui_maker_params):
    """

    Args:
        ui_maker_params (UIMakerParams): Standard parameters for making ui item
    """
    parent_ui_item = ui_maker_params.parent_ui
    parent = ui_maker_params.parent_cmp
    linkbutton = ui_maker_params.component
    ext_asm_info = ui_maker_params.asm_info

    if not linkbutton.is_supported:
        return None

    if linkbutton.beta_cmd and not ui_maker_params.create_beta_cmds:
        return None

    if not linkbutton.command_class:
        return None

    mlogger.debug('Producing button: %s', linkbutton)
    try:
        linked_asm_list = find_loaded_asm(linkbutton.assembly)
        if not linked_asm_list:
            return None

        linked_asm = linked_asm_list[0]

        parent_ui_item.create_push_button(
            linkbutton.name,
            linked_asm.Location,
            _make_full_class_name(linked_asm.GetName().Name,
                                  linkbutton.command_class),
            linkbutton.icon_file or parent.icon_file,
            _make_button_tooltip(linkbutton),
            _make_button_tooltip_ext(linkbutton, ext_asm_info.name),
            None,
            None,
            None,
            update_if_exists=True,
            ui_title=_make_ui_title(linkbutton))
        return parent_ui_item.button(linkbutton.name)
    except PyRevitException as err:
        mlogger.error('UI error: %s', err.msg)
        return None


def _produce_ui_pushbutton(ui_maker_params):
    """

    Args:
        ui_maker_params (UIMakerParams): Standard parameters for making ui item
    """
    parent_ui_item = ui_maker_params.parent_ui
    parent = ui_maker_params.parent_cmp
    pushbutton = ui_maker_params.component
    ext_asm_info = ui_maker_params.asm_info

    if not pushbutton.is_supported:
        return None

    if pushbutton.beta_cmd and not ui_maker_params.create_beta_cmds:
        return None

    mlogger.debug('Producing button: %s', pushbutton)
    try:
        parent_ui_item.create_push_button(
            button_name=pushbutton.name,
            asm_location=ext_asm_info.location,
            class_name=_get_effective_classname(pushbutton),
            icon_path=pushbutton.icon_file or parent.icon_file,
            tooltip=_make_button_tooltip(pushbutton),
            tooltip_ext=_make_button_tooltip_ext(pushbutton,
                                                 ext_asm_info.name),
            tooltip_image=pushbutton.ttimage_file,
            tooltip_video=pushbutton.ttvideo_file,
            ctxhelpurl=pushbutton.get_help_url() or '',
            avail_class_name=pushbutton.avail_class_name,
            update_if_exists=True,
            ui_title=_make_ui_title(pushbutton))
        return parent_ui_item.button(pushbutton.name)
    except PyRevitException as err:
        mlogger.error('UI error: %s', err.msg)
        return None


def _produce_ui_pulldown(ui_maker_params):
    """

    Args:
        ui_maker_params (UIMakerParams): Standard parameters for making ui item
    """
    parent_ribbon_panel = ui_maker_params.parent_ui
    pulldown = ui_maker_params.component

    mlogger.debug('Producing pulldown button: %s', pulldown)
    try:
        parent_ribbon_panel.create_pulldown_button(pulldown.ui_title,
                                                   pulldown.icon_file,
                                                   update_if_exists=True)
        return parent_ribbon_panel.ribbon_item(pulldown.ui_title)
    except PyRevitException as err:
        mlogger.error('UI error: %s', err.msg)
        return None


def _produce_ui_split(ui_maker_params):
    """

    Args:
        ui_maker_params (UIMakerParams): Standard parameters for making ui item
    """
    parent_ribbon_panel = ui_maker_params.parent_ui
    split = ui_maker_params.component

    mlogger.debug('Producing split button: %s}', split)
    try:
        parent_ribbon_panel.create_split_button(split.ui_title,
                                                split.icon_file,
                                                update_if_exists=True)
        return parent_ribbon_panel.ribbon_item(split.ui_title)
    except PyRevitException as err:
        mlogger.error('UI error: %s', err.msg)
        return None


def _produce_ui_splitpush(ui_maker_params):
    """

    Args:
        ui_maker_params (UIMakerParams): Standard parameters for making ui item
    """
    parent_ribbon_panel = ui_maker_params.parent_ui
    splitpush = ui_maker_params.component

    mlogger.debug('Producing splitpush button: %s', splitpush)
    try:
        parent_ribbon_panel.create_splitpush_button(splitpush.ui_title,
                                                    splitpush.icon_file,
                                                    update_if_exists=True)
        return parent_ribbon_panel.ribbon_item(splitpush.ui_title)
    except PyRevitException as err:
        mlogger.error('UI error: %s', err.msg)
        return None


def _produce_ui_stacks(ui_maker_params):
    """

    Args:
        ui_maker_params (UIMakerParams): Standard parameters for making ui item
    """
    parent_ui_panel = ui_maker_params.parent_ui
    stack_parent = ui_maker_params.parent_cmp
    stack_cmp = ui_maker_params.component
    ext_asm_info = ui_maker_params.asm_info

    # if sub_cmp is a stack, ask parent_ui_item to open a stack
    # (parent_ui_item.open_stack).
    # All subsequent items will be placed under this stack. Close the stack
    # (parent_ui_item.close_stack) to finish adding items to the stack.
    try:
        parent_ui_panel.open_stack()
        mlogger.debug('Opened stack: %s', stack_cmp.name)

        if HOST_APP.is_older_than('2017'):
            _component_creation_dict[SPLIT_BUTTON_POSTFIX] = \
                _produce_ui_pulldown
            _component_creation_dict[SPLITPUSH_BUTTON_POSTFIX] = \
                _produce_ui_pulldown

        # capturing and logging any errors on stack item
        # (e.g when parent_ui_panel's stack is full and can not add any
        # more items it will raise an error)
        _recursively_produce_ui_items(
            UIMakerParams(parent_ui_panel,
                          stack_parent,
                          stack_cmp,
                          ext_asm_info,
                          ui_maker_params.create_beta_cmds))

        if HOST_APP.is_older_than('2017'):
            _component_creation_dict[SPLIT_BUTTON_POSTFIX] = \
                _produce_ui_split
            _component_creation_dict[SPLITPUSH_BUTTON_POSTFIX] = \
                _produce_ui_splitpush

        try:
            parent_ui_panel.close_stack()
            mlogger.debug('Closed stack: %s', stack_cmp.name)
            return stack_cmp
        except PyRevitException as err:
            mlogger.error('Error creating stack | %s', err)

    except Exception as err:
        mlogger.error('Can not create stack under this parent: %s | %s',
                      parent_ui_panel, err)


def _produce_ui_panelpushbutton(ui_maker_params):
    """

    Args:
        ui_maker_params (UIMakerParams): Standard parameters for making ui item
    """
    parent_ui_item = ui_maker_params.parent_ui
    # parent = ui_maker_params.parent_cmp
    paneldlgbutton = ui_maker_params.component
    ext_asm_info = ui_maker_params.asm_info

    if paneldlgbutton.beta_cmd and not ui_maker_params.create_beta_cmds:
        return None

    mlogger.debug('Producing panel button: %s', paneldlgbutton)
    try:
        parent_ui_item.create_panel_push_button(
            button_name=paneldlgbutton.name,
            asm_location=ext_asm_info.location,
            class_name=_get_effective_classname(paneldlgbutton),
            tooltip=_make_button_tooltip(paneldlgbutton),
            tooltip_ext=_make_button_tooltip_ext(paneldlgbutton,
                                                 ext_asm_info.name),
            tooltip_image=paneldlgbutton.ttimage_file,
            tooltip_video=paneldlgbutton.ttvideo_file,
            ctxhelpurl=paneldlgbutton.get_help_url() or '',
            avail_class_name=paneldlgbutton.avail_class_name,
            update_if_exists=True)

        return parent_ui_item.button(paneldlgbutton.name)
    except PyRevitException as err:
        mlogger.error('UI error: %s', err.msg)
        return None


def _produce_ui_panels(ui_maker_params):
    """

    Args:
        ui_maker_params (UIMakerParams): Standard parameters for making ui item
    """
    parent_ui_tab = ui_maker_params.parent_ui
    panel = ui_maker_params.component

    mlogger.debug('Producing ribbon panel: %s', panel)
    try:
        parent_ui_tab.create_ribbon_panel(panel.name, update_if_exists=True)
        return parent_ui_tab.ribbon_panel(panel.name)
    except PyRevitException as err:
        mlogger.error('UI error: %s', err.msg)
        return None


def _produce_ui_tab(ui_maker_params):
    """

    Args:
        ui_maker_params (UIMakerParams): Standard parameters for making ui item
    """
    parent_ui = ui_maker_params.parent_ui
    tab = ui_maker_params.component

    mlogger.debug('Verifying tab: %s', tab)
    if tab.has_commands():
        mlogger.debug('Tabs has command: %s', tab)
        mlogger.debug('Producing ribbon tab: %s', tab)
        try:
            parent_ui.create_ribbon_tab(tab.name, update_if_exists=True)
            return parent_ui.ribbon_tab(tab.name)
        except PyRevitException as err:
            mlogger.error('UI error: %s', err.msg)
            return None
    else:
        mlogger.debug('Tab does not have any commands. Skipping: %s', tab.name)
        return None


_component_creation_dict = {
    TAB_POSTFIX: _produce_ui_tab,
    PANEL_POSTFIX: _produce_ui_panels,
    STACKTWO_BUTTON_POSTFIX: _produce_ui_stacks,
    STACKTHREE_BUTTON_POSTFIX: _produce_ui_stacks,
    PULLDOWN_BUTTON_POSTFIX: _produce_ui_pulldown,
    SPLIT_BUTTON_POSTFIX: _produce_ui_split,
    SPLITPUSH_BUTTON_POSTFIX: _produce_ui_splitpush,
    PUSH_BUTTON_POSTFIX: _produce_ui_pushbutton,
    TOGGLE_BUTTON_POSTFIX: _produce_ui_smartbutton,
    SMART_BUTTON_POSTFIX: _produce_ui_smartbutton,
    LINK_BUTTON_POSTFIX: _produce_ui_linkbutton,
    SEPARATOR_IDENTIFIER: _produce_ui_separator,
    SLIDEOUT_IDENTIFIER: _produce_ui_slideout,
    PANEL_PUSH_BUTTON_POSTFIX: _produce_ui_panelpushbutton,
    }


def _recursively_produce_ui_items(ui_maker_params):
    cmp_count = 0
    for sub_cmp in ui_maker_params.component:
        ui_item = None
        try:
            mlogger.debug('Calling create func %s for: %s',
                          _component_creation_dict[sub_cmp.type_id],
                          sub_cmp)
            ui_item = _component_creation_dict[sub_cmp.type_id](
                UIMakerParams(ui_maker_params.parent_ui,
                              ui_maker_params.component,
                              sub_cmp,
                              ui_maker_params.asm_info,
                              ui_maker_params.create_beta_cmds))
            if ui_item:
                cmp_count += 1
        except KeyError:
            mlogger.debug('Can not find create function for: %s', sub_cmp)
        except Exception as create_err:
            mlogger.critical(create_err)

        mlogger.debug('UI item created by create func is: %s', ui_item)

        if ui_item \
                and not isinstance(ui_item, components.GenericStack) \
                and sub_cmp.is_container:
            subcmp_count = _recursively_produce_ui_items(
                UIMakerParams(ui_item,
                              ui_maker_params.component,
                              sub_cmp,
                              ui_maker_params.asm_info,
                              ui_maker_params.create_beta_cmds))

            # if component does not have any sub components hide it
            if subcmp_count == 0:
                ui_item.deactivate()

    return cmp_count


if not EXEC_PARAMS.doc_mode:
    current_ui = ribbon.get_current_ui()


def update_pyrevit_ui(ui_ext, ext_asm_info, create_beta=False):
    """
    Updates/Creates pyRevit ui for the given extension and
    provided assembly dll address.
    """
    mlogger.debug('Creating/Updating ui for extension: %s', ui_ext)
    cmp_count = _recursively_produce_ui_items(
        UIMakerParams(current_ui, None, ui_ext, ext_asm_info, create_beta))
    mlogger.debug('%s components were created for: %s', cmp_count, ui_ext)


def sort_pyrevit_ui(ui_ext):
    # only works on panels so far
    # re-ordering of ui components deeper than panels have not been implemented
    layout_directives = []
    for item in ui_ext:
        layout_directives.extend(item.get_layout_directives())

    for tab in current_ui.get_pyrevit_tabs():
        for ldir in layout_directives:
            if ldir.type == 'before':
                tab.reorder_before(ldir.item, ldir.target)
                layout_directives.remove(ldir)
            elif ldir.type == 'after':
                tab.reorder_after(ldir.item, ldir.target)
                layout_directives.remove(ldir)
            elif ldir.type == 'afterall':
                tab.reorder_afterall(ldir.item)
                layout_directives.remove(ldir)
            elif ldir.type == 'beforeall':
                tab.reorder_beforeall(ldir.item)
                layout_directives.remove(ldir)


def cleanup_pyrevit_ui():
    # hide all items that were not touched after a reload
    # meaning they have been removed in extension folder structure
    # and thus are not updated
    untouched_items = current_ui.get_unchanged_items()
    for item in untouched_items:
        if not item.is_native():
            try:
                mlogger.debug('Deactivating: %s', item)
                item.deactivate()
            except Exception as deact_err:
                mlogger.debug(deact_err)
