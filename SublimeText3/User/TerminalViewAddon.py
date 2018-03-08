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
    def run(self, direction="down", always_split=False, do_exec=False,
            **kwargs):
        window = self.window

        direction = direction.strip().lower()
        if direction not in ('up', 'down', 'left', 'right'):
            raise ValueError("bad direction: {0}".format(direction))

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

            extreme_group_has_views = bool(window.views_in_group(extreme_group))

            # print("cells:", cells)
            # print("current_cell:", current_cell)
            # print("rows:", rows)
            # print("cols:", cols)
            # print("Lone in direction?", lone_in_direction)
            # print("Extreme Group", extreme_group)
            # print("extreme_group_has_views", extreme_group_has_views)
            # print("adjacent_cells", adjacent_cells)

            if always_split:
                do_split, start_from = True, extreme_group
            elif lone_in_direction and not extreme_group_has_views:
                do_split, start_from = True, extreme_group
            elif not extreme_group_has_views:
                do_split, start_from = False, extreme_group
            else:
                do_split, start_from = True, extreme_group

            window.focus_group(start_from)
            if do_split:
                window.run_command("create_pane", args={"direction": direction,
                                                        "give_focus": True})
                window.run_command("zoom_pane", args={"fraction": 0.35})

            if do_exec:
                window.run_command("terminal_view_exec", args=kwargs)
            else:
                window.run_command("terminal_view_open", args=kwargs)



def make_cmd(window, wrap_bash=True):
    v = window.extract_variables()
    filename = v['file']
    platform = v['platform'].strip().lower()

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
            sublime.error_message("Not sure how to run: {0}".format(filename))

    if platform in ('osx', 'linux'):
        if runwith:
            cmd = '"{0}" "{1}"'.format(runwith, filename)
        else:
            cmd = '"{0}"'.format(filename)

        if wrap_bash:
            cmd = "bash -lc '{0}'".format(cmd)
    else:
        sublime.error_message("TerminalViewAddon does not work on platform "
                              "'{0}'".format(platform))
        cmd = None

    return cmd


class RunInTerminalView(sublime_plugin.WindowCommand):
    def run(self, split_view=False, **kwargs):
        term_open_cmd = "split_open_terminal" if split_view else "terminal_view_open"
        if False:  # pylint: disable=using-constant-test
            cmd = make_cmd(self.window, wrap_bash=False)
            kwargs['do_exec'] = True
            kwargs['cmd'] = cmd
            self.window.run_command(term_open_cmd, args=kwargs)
        else:
            cmd = make_cmd(self.window, wrap_bash=False)
            self.window.run_command(term_open_cmd, args=kwargs)
            time.sleep(0.0)
            self.window.run_command("terminal_view_send_string",
                                    args={"string": cmd + '\n'})
