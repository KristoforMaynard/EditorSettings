# in your User settings, it's useful to specify:
# > "origami_auto_close_empty_panes": true,
#
# There are some associated entries in
# > Default (OSX).sublime-keymap
# > Default (Linux).sublime-keymap
# > Default.sublime-commands
#
# cmd+alt+w, next pane?
# cmd+alt+shift+w, prev pane?

import os
import time

import sublime
import sublime_plugin


def import_companions():
    try:
        import TerminalView
    except ImportError:
        TerminalView = None

    try:
        from Origami import origami
    except ImportError:
        origami = None

    return TerminalView, origami

def _emit_no_origami_msg():
    sublime.error_message("The Origami plugin must be installed to "
                          "split-open a terminal window")

def argmax(seq):
    return max(enumerate(seq), key=lambda x: x[1])[0]

def argmin(seq):
    return min(enumerate(seq), key=lambda x: x[1])[0]


class SplitOpenTerminalView(sublime_plugin.WindowCommand):
    def run(self, direction="down", always_split=False, split_fraction=0.35,
            do_exec=False, **kwargs):
        window = self.window

        direction = direction.strip().lower()
        if direction not in ('up', 'down', 'left', 'right'):
            raise ValueError("bad direction: {0}".format(direction))

        if 'working_dir' in kwargs:
            kwargs['cwd'] = kwargs.pop('working_dir')

        TerminalView, origami = import_companions()

        if TerminalView is None:
            sublime.error_message("split-open terminal requires the "
                                  "TerminalView plugin")
            return

        if origami is None:
            window.run_command("terminal_view_open", args=kwargs)
            _emit_no_origami_msg()
        else:
            cells = window.get_layout()['cells']
            rows = window.get_layout()['rows']
            cols = window.get_layout()['cols']
            current_cell = cells[window.active_group()]

            # iaxis = {'left': 0, 'right': 0, 'up': 1, 'down': 1}[direction]
            # idir = {'left': 0, 'up': 1, 'right': 2, 'down': 3}[direction]

            adjacent_cells = origami.cells_adjacent_to_cell_in_direction(cells,
                                                                         current_cell,
                                                                         direction)
            lone_in_direction = not bool(adjacent_cells)

            if direction == 'down':
                extreme_group = [tup[3] for tup in cells].index(argmax(rows))
            elif direction == 'up':
                extreme_group = [tup[1] for tup in cells].index(argmin(rows))
            elif direction == 'left':
                extreme_group = [tup[0] for tup in cells].index(argmin(cols))
            elif direction == 'right':
                extreme_group = [tup[2] for tup in cells].index(argmax(cols))

            extreme_group_views = window.views_in_group(extreme_group)
            extreme_group_has_views = bool(extreme_group_views)
            extreme_group_has_terminal = any(view.settings().has('terminal_view_activate_args')
                                             for view in extreme_group_views)
            # print("cells:", cells)
            # print("current_cell:", current_cell)
            # print("rows:", rows)
            # print("cols:", cols)
            # print("Lone in direction?", lone_in_direction)
            # print("Extreme Group", extreme_group)
            # print("extreme_group_has_views", extreme_group_has_views)
            # print("adjacent_cells", adjacent_cells)

            # this logic is becoming silly...
            if always_split:
                do_split, start_from = True, extreme_group
            elif lone_in_direction and not extreme_group_has_views:
                do_split, start_from = True, extreme_group
            elif extreme_group_has_terminal:
                do_split, start_from = False, extreme_group
            elif not extreme_group_has_views:
                do_split, start_from = False, extreme_group
            else:
                do_split, start_from = True, extreme_group

            window.focus_group(start_from)
            if do_split:
                window.run_command("create_pane", args={"direction": direction,
                                                        "give_focus": True})
                window.run_command("zoom_pane", args={"fraction": split_fraction})

            # print("????", kwargs)
            if do_exec:
                kwargs['working_dir'] = kwargs.pop('cwd', None)
                sublime.error_message("TerminalViewAddon: don't use do_exec")
                # window.run_command("terminal_view_exec", args=kwargs)
            else:
                window.run_command("terminal_view_open", args=kwargs)



def make_cmd(window, wrap_bash=True, filename=None, close_on_finished=False):
    v = window.extract_variables()
    platform = v['platform'].strip().lower()
    if filename is None:
        filename = v['file']

    if close_on_finished:
        wrap_bash = True
        next_cmd = '; logout'
    else:
        next_cmd = ''

    root, ext = os.path.splitext(os.path.basename(filename))
    ext = ext.strip().lower()
    if os.access(filename, os.X_OK):
        runwith = ''
    else:
        ext_lookup = {'.py': 'python', '.pl': 'perl', '.sh': 'bash'}
        if ext in ext_lookup:
            runwith = ext_lookup[ext]
        elif (root.strip().lower(), ext) == ('makefile', ''):
            runwith = 'make'
        else:
            # sublime.error_message("Not sure how to run: {0}".format(filename))
            runwith = ''

    if platform in ('osx', 'linux'):
        if runwith:
            cmd = '"{0}" "{1}"'.format(runwith, filename)
        else:
            cmd = '"{0}"'.format(filename)

        if wrap_bash:
            cmd = "bash -lc '{0}'{1}".format(cmd, next_cmd)
    else:
        sublime.error_message("TerminalViewAddon does not work on platform "
                              "'{0}'".format(platform))
        cmd = None

    return cmd


class RunInTerminalView(sublime_plugin.WindowCommand):
    def run(self, target_file=None, split_view=False, close_on_finished=False,
            do_exec=False, **kwargs):
        # kwargs.pop("name", None)

        if split_view:
            term_open_cmd = "split_open_terminal_view"
        else:
            term_open_cmd = "terminal_view_open"

        if do_exec:
            cmd = make_cmd(self.window, wrap_bash=False, filename=target_file,
                           close_on_finished=close_on_finished)
            kwargs['do_exec'] = True
            kwargs['shell_cmd'] = cmd
            self.window.run_command(term_open_cmd, args=kwargs)
        else:
            cmd = make_cmd(self.window, wrap_bash=False, filename=target_file,
                           close_on_finished=close_on_finished)
            self.window.run_command(term_open_cmd, args=kwargs)
            time.sleep(0.0)
            self.window.run_command("terminal_view_send_string",
                                    args={"string": cmd + '\n'})
