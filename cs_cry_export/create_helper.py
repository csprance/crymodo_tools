import modo
import modo.constants as c

from cs_cry_export.utils import create_channel


def main():
    scene = modo.Scene()
    cry_helper = scene.addItem(c.LOCATOR_TYPE, name="CryHelper_NameHere")
    create_channel("cryhelper", cry_helper)


if __name__ == "__main__":
    main()
