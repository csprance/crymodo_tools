from subprocess import Popen, PIPE, STDOUT

import lx
import modo


def set_rc_path():
    try:
        lx.eval("dialog.main fileOpen")
        lx.eval('dialog.title "Select RC.exe Path"')
        lx.eval("dialog.open")
        result = lx.eval("dialog.result ?")
        lx.eval('user.value cs_cry_export_preference_rc "%s"' % result)
        return result
    except RuntimeError:
        return None


def run(**kwargs):
    rc_path = lx.eval("user.value cs_cry_export_preference_rc ?")
    output = Popen(
        [
            rc_path,
            "/verbose",
            "/refresh",
            '/threads=processors'
            "/vertexindexformat=u16",
            kwargs["path"],
        ],
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=STDOUT,
    ).communicate()[0]
    # modo.dialogs.alert("RC Output", output)
