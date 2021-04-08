import bpy


def collapsable_panel(
    layout: bpy.types.UILayout, data: bpy.types.AnyType, property: str, alert: bool = False, **kwargs
):
    row = layout.row()
    row.prop(
        data, property, icon="TRIA_DOWN" if getattr(data, property) else "TRIA_RIGHT", icon_only=True, emboss=False,
    )
    if alert:
        row.alert = True
    row.label(**kwargs)
    return getattr(data, property)
