# python
from datetime import datetime

from lxml import etree
from lxml.builder import ElementMaker

E = ElementMaker()


def create_helper_node(
    _id="default",
    trans="0 0 0",
    rot_z="0 0 1 0",
    rot_y="0 1 0 0",
    rot_x="1 0 0 0",
    scale="1 1 1",
):
    node = E.node(
        {"id": _id},
        E.translate({"sid": "translation"}, trans),
        E.rotate({"sid": "rotation_z"}, rot_z),
        E.rotate({"sid": "rotation_y"}, rot_y),
        E.rotate({"sid": "rotation_x"}, rot_x),
        E.scale({"sid": "scale"}, scale),
        E.extra(
            E.technique(
                {"profile": "CryEngine"},
                E.helper(
                    {"type": "dummy"},
                    E.bound_box_min("-5 -5 -5"),
                    E.bound_box_max("5 5 5"),
                ),
            )
        ),
    )
    return node


# noinspection PyDefaultArgument
def create_effect(
    id="effect-mat-name",
    emission="0.0 0.0 0.0 1.0",
    ambient="0.0 0.0 0.0 1.0",
    diffuse="0.0 0.0 0.0 1.0",
    specular="0.0 0.0 0.0 1.0",
    shininess="1.0",
    reflective="0.0 0.0 0.0 1.0",
    reflectivity="1.0",
    transparent="0.0 0.0 0.0 1.0",
    transparency="1.0",
    index_of_refraction="1.0",
):
    return E.effect(
        {"id": id},
        E.profile_COMMON(
            E.technique(
                {"sid": "default"},
                E.phong(
                    E.emission(E.color({"sid": "emission"}, emission)),
                    E.ambient(E.color({"sid": "ambient"}, ambient)),
                    E.diffuse(E.color({"sid": "diffuse"}, diffuse)),
                    E.specular(E.color({"sid": "specular"}, specular)),
                    E.shininess(E.float({"sid": "shininess"}, shininess)),
                    E.reflective(E.color({"sid": "reflective"}, reflective)),
                    E.reflectivity(E.float({"sid": "reflectivity"}, reflectivity)),
                    E.transparent(
                        {"opaque": "RGB_ZERO"},
                        E.color({"sid": "transparent"}, transparent),
                    ),
                    E.transparency(E.float({"sid": "transparency"}, transparency)),
                    E.index_of_refraction(
                        E.float({"sid": "index_of_refraction"}, index_of_refraction)
                    ),
                ),
            )
        ),
    )


def create_collada_file():
    xml = E.COLLADA(
        {"xmlns": "http://www.collada.org/2005/11/COLLADASchema", "version": "1.4.1"},
        E.asset(
            E.contributor(
                E.author("Chris Sprance"),
                E.authoring_tool("Modo CRYEXPORT Tool 1.0.0"),
                E.source_data("filepath"),
            ),
            E.created(str(datetime.now())),
            E.modified(str(datetime.now())),
            E.revision("1.4.1"),
            E.unit({"name": "meter", "meter": "1.0000000000e+000"}),
            E.up_axis("Z_UP"),
        ),
        E.library_animation_clips(),
        E.library_animations(),
        E.library_effects(
            create_effect(id="test5"),
            create_effect(id="test1"),
            create_effect(id="test2"),
        ),
        E.library_materials(
            E.material({"id": "mat-id"}, E.instance_effect({"url": "#mat-id"})),
            E.material({"id": "mat-id1"}, E.instance_effect({"url": "#mat-id1"})),
        ),
        E.library_geometries(),
        E.library_controllers(),
        E.library_visual_scenes(create_helper_node()),
        E.library_images(),
        E.scene(),
    )
    return xml


def main():
    xml = create_collada_file()
    print('<?xml version="1.0" encoding="utf-8"?>')
    print(etree.tostring(xml, pretty_print=True))
    with open("output.dae", "w") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n')
        f.write(etree.tostring(xml, pretty_print=True))


if __name__ == "__main__":
    main()
