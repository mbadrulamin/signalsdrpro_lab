# Shared by every demo script. Not run on its own.
#
# The labs expect their files in /tmp, but /tmp is emptied at every boot.
# The real copies live in ~/sdr_demo. restore() puts a copy back before a demo.

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LABS="$REPO/02_flowgraphs"
SCRIPTS="$REPO/03_scripts"
STORE="$HOME/sdr_demo"

# VS Code installed as a snap points GTK and GIO at its own libraries, and its
# terminal passes that on. The first Qt window then crashes with
# "symbol lookup error ... /snap/core20/...". Undo it so the demos run the same
# from VS Code as from an ordinary terminal.
if [ "${SNAP_NAME:-}" = "code" ]; then
    [ -n "${XDG_DATA_DIRS_VSCODE_SNAP_ORIG:-}" ]   && export XDG_DATA_DIRS="$XDG_DATA_DIRS_VSCODE_SNAP_ORIG"
    [ -n "${XDG_CONFIG_DIRS_VSCODE_SNAP_ORIG:-}" ] && export XDG_CONFIG_DIRS="$XDG_CONFIG_DIRS_VSCODE_SNAP_ORIG"
    unset GTK_PATH GTK_EXE_PREFIX GTK_IM_MODULE_FILE GIO_MODULE_DIR \
          GDK_PIXBUF_MODULE_FILE GDK_PIXBUF_MODULEDIR GSETTINGS_SCHEMA_DIR \
          LOCPATH XDG_DATA_HOME
fi

say()  { printf '\n\033[1m%s\033[0m\n' "$*"; }
ok()   { printf '  \033[32mOK\033[0m    %s\n' "$*"; }
warn() { printf '  \033[33mWARN\033[0m  %s\n' "$*"; }
bad()  { printf '  \033[31mFAIL\033[0m  %s\n' "$*"; }

# restore NAME: copy ~/sdr_demo/NAME to /tmp/NAME, unless it is already there.
restore() {
    local name="$1"
    if [ -s "/tmp/$name" ] && [ "$(stat -c %s "/tmp/$name")" = "$(stat -c %s "$STORE/$name" 2>/dev/null)" ]; then
        return 0
    fi
    if [ ! -s "$STORE/$name" ]; then
        bad "$STORE/$name is missing. See SETUP_CHECKLIST.md."
        return 1
    fi
    echo "  copying $name to /tmp (a few seconds)..."
    cp "$STORE/$name" "/tmp/$name"
}

# radio_users: print any program that may be holding the radio.
radio_users() {
    ps -eo pid,args | grep -E "[l]ab0[1-9]_|[l]ab1[0-2]_|[u]hd_fft|[s]can_tv_band|[g]qrx|[t]v_playout" \
        | grep -v -E "grep|preflight|stop_all"
}

# need_free_radio: stop the demo if something else has the radio.
need_free_radio() {
    local users
    users="$(radio_users)"
    if [ -n "$users" ]; then
        bad "Something else is using the radio. Close it first, or run ./stop_all.sh"
        echo "$users" | sed 's/^/        /'
        exit 1
    fi
}
