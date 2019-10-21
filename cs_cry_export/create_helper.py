import modo
import modo.constants as c

import cs_cry_export.utils as utils
import cs_cry_export.constants as _c


def main():
    scene = modo.Scene()
    result = utils.get_user_input("Helper Name.")
    locator = scene.addItem(c.LOCATOR_TYPE, name="%s%s" % (_c.CRYHELPER_PREFIX, result))
    locator.channel("drawShape").set("Custom")
    locator.channel("isSolid").set(False)
    locator.channel("isSize").set((.25, .25, .25))
    locator.setTag("COLR", "lightpurple")
    locator.PackageAdd("glDraw")
    locator.channel("wireOptions").set("user")
    locator.channel("wireColor").set((1, .75, 1))
    utils.create_channel(_c.CHANNEL_CRYHELPER_NAME, locator)


if __name__ == "__main__":
    main()
