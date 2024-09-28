bl_info = {
    "name": "Easy Sculpt Menu",
    "author": "Kaan Soyler (404axolotl)",
    "version": (2, 1),
    "blender": (2, 80, 0),
    "location": "Sculpt Mode",
    "description": "Switchable menu for customizing brush options, optimized for pen input",
    "category": "Sculpt",
}

import bpy
from bpy.types import (
    Operator,
    AddonPreferences,
    Menu,
)
from bpy.props import (
    BoolProperty,
    StringProperty,
    EnumProperty,
)

addon_keymaps = []

class EasySculptMenuPreferences(AddonPreferences):
    bl_idname = __name__

    menu_type: EnumProperty(
        name="Menu Type",
        description="Choose between Pie Menu and Regular Menu",
        items=[
            ('PIE', "Pie Menu", "Use Pie Menu"),
            ('REGULAR', "Regular Menu", "Use Regular Menu"),
        ],
        default='PIE',
    )

    shortcut_key: StringProperty(
        name="Shortcut Key",
        description="Key to open the Easy Sculpt Menu",
        default='W',
    )

    # Define available brushes
    available_brushes = [
        ('DRAW', "Draw", "Draw brush"),
        ('SMOOTH', "Smooth", "Smooth brush"),
        ('CREASE', "Crease", "Crease brush"),
        ('GRAB', "Grab", "Grab brush"),
        ('ELASTIC_DEFORM', "Elastic Deform", "Elastic Deform brush"),
        ('INFLATE', "Inflate", "Inflate brush"),
        ('CLAY', "Clay", "Clay brush"),
        ('PINCH', "Pinch", "Pinch brush"),
        ('SCRAPE', "Scrape", "Scrape brush"),
        ('FLATTEN', "Flatten", "Flatten brush"),
    ]

    # Brush visibility properties
    for brush in available_brushes:
        exec(f"show_brush_{brush[0]}: BoolProperty(name='{brush[1]}', description='{brush[2]}', default=True)")

    def draw(self, context):
        layout = self.layout

        layout.label(text="Menu Settings:")
        layout.prop(self, "menu_type")
        layout.prop(self, "shortcut_key")

        layout.separator()
        layout.label(text="Brushes to Display:")
        for brush in self.available_brushes:
            prop_name = f"show_brush_{brush[0]}"
            layout.prop(self, prop_name)

# Operator to call the menu
class SCULPT_OT_easy_menu_call(Operator):
    """Call Easy Sculpt Menu"""
    bl_idname = "wm.easy_sculpt_menu_call"
    bl_label = "Easy Sculpt Menu Call"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        if prefs.menu_type == 'PIE':
            bpy.ops.wm.call_menu_pie(name=SCULPT_MT_easy_pie_menu.bl_idname)
        else:
            bpy.ops.sculpt.easy_regular_menu('INVOKE_DEFAULT')
        return {'FINISHED'}

# Regular Pop-up Menu
class SCULPT_OT_easy_regular_menu(Operator):
    """Easy Sculpt Regular Menu"""
    bl_idname = "sculpt.easy_regular_menu"
    bl_label = "Easy Sculpt Menu"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        settings = context.tool_settings
        sculpt = settings.sculpt
        brush = sculpt.brush
        unified = settings.unified_paint_settings
        prefs = context.preferences.addons[__name__].preferences

        if brush:
            # Brush Settings
            box = layout.box()
            box.label(text="Brush Settings", icon='BRUSH_DATA')
            row = box.row(align=True)
            row.prop(unified, "use_unified_size", text="Unified Size")
            row.prop(unified, "use_unified_strength", text="Unified Strength")

            if unified.use_unified_size:
                box.prop(unified, "size", text="Size")
            else:
                box.prop(brush, "size", text="Size")

            if unified.use_unified_strength:
                box.prop(unified, "strength", text="Strength")
            else:
                box.prop(brush, "strength", text="Strength")

            # Advanced Settings
            box = layout.box()
            box.label(text="Advanced Settings", icon='PREFERENCES')
            box.prop(brush, "auto_smooth_factor", slider=True)
            box.prop(brush, "normal_radius_factor", slider=True)
            box.prop(brush, "hardness", slider=True)
            box.prop(brush, "use_frontface", text="Front Faces Only")
            box.prop(brush, "use_accumulate")
            box.operator("brush.reset", text="Reset Brush Settings")

            # Brush Selection
            box = layout.box()
            box.label(text="Brush Selection", icon='SCULPTMODE_HLT')
            row = box.row(align=True)
            brushes_in_row = 0
            for brush_item in prefs.available_brushes:
                prop_name = f"show_brush_{brush_item[0]}"
                if getattr(prefs, prop_name):
                    op = row.operator("paint.brush_select", text=brush_item[1])
                    op.sculpt_tool = brush_item[0]
                    brushes_in_row += 1
                    if brushes_in_row >= 4:
                        row = box.row(align=True)
                        brushes_in_row = 0
        else:
            layout.label(text="No active brush", icon='ERROR')

# Pie Menu
class SCULPT_MT_easy_pie_menu(Menu):
    bl_label = "Easy Sculpt Pie Menu"
    bl_idname = "SCULPT_MT_easy_pie_menu"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        prefs = context.preferences.addons[__name__].preferences

        # NW - Brush Settings
        pie.operator("sculpt.easy_brush_settings", text="Brush Settings")

        # NE - Brush Selection
        box = pie.box()
        box.label(text="Brush Selection")
        col = box.column()
        for brush_item in prefs.available_brushes:
            prop_name = f"show_brush_{brush_item[0]}"
            if getattr(prefs, prop_name):
                op = col.operator("paint.brush_select", text=brush_item[1])
                op.sculpt_tool = brush_item[0]

        # SW - Advanced Settings
        pie.operator("sculpt.easy_advanced_settings", text="Advanced Settings")

        # SE - Reset Brush Settings
        pie.operator("brush.reset", text="Reset Brush Settings")

        # N - Empty
        pie.separator()
        # S - Empty
        pie.separator()
        # W - Empty
        pie.separator()
        # E - Empty
        pie.separator()

# Operator for Brush Settings
class SCULPT_OT_easy_brush_settings(Operator):
    """Adjust Brush Settings"""
    bl_idname = "sculpt.easy_brush_settings"
    bl_label = "Brush Settings"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        settings = context.tool_settings
        brush = settings.sculpt.brush
        unified = settings.unified_paint_settings

        if brush:
            layout.prop(unified, "use_unified_size", text="Unified Size")
            if unified.use_unified_size:
                layout.prop(unified, "size", text="Size")
            else:
                layout.prop(brush, "size", text="Size")
            layout.prop(unified, "use_unified_strength", text="Unified Strength")
            if unified.use_unified_strength:
                layout.prop(unified, "strength", text="Strength")
            else:
                layout.prop(brush, "strength", text="Strength")
        else:
            layout.label(text="No active brush", icon='ERROR')

# Operator for Advanced Settings
class SCULPT_OT_easy_advanced_settings(Operator):
    """Adjust Advanced Brush Settings"""
    bl_idname = "sculpt.easy_advanced_settings"
    bl_label = "Advanced Brush Settings"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        brush = context.tool_settings.sculpt.brush

        if brush:
            layout.prop(brush, "auto_smooth_factor", slider=True)
            layout.prop(brush, "normal_radius_factor", slider=True)
            layout.prop(brush, "hardness", slider=True)
            layout.prop(brush, "use_frontface", text="Front Faces Only")
            layout.prop(brush, "use_accumulate")
            layout.operator("brush.reset", text="Reset Brush Settings")
        else:
            layout.label(text="No active brush", icon='ERROR')

def register():
    bpy.utils.register_class(EasySculptMenuPreferences)
    bpy.utils.register_class(SCULPT_OT_easy_brush_settings)
    bpy.utils.register_class(SCULPT_OT_easy_advanced_settings)
    bpy.utils.register_class(SCULPT_OT_easy_regular_menu)
    bpy.utils.register_class(SCULPT_MT_easy_pie_menu)
    bpy.utils.register_class(SCULPT_OT_easy_menu_call)

    # Assign the keymap
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        prefs = bpy.context.preferences.addons[__name__].preferences
        km = kc.keymaps.new(name='Sculpt', space_type='EMPTY')
        kmi = km.keymap_items.new(
            "wm.easy_sculpt_menu_call",
            type=prefs.shortcut_key.upper(),
            value='PRESS',
        )
        addon_keymaps.append((km, kmi))

def unregister():
    # Remove the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(SCULPT_OT_easy_menu_call)
    bpy.utils.unregister_class(SCULPT_MT_easy_pie_menu)
    bpy.utils.unregister_class(SCULPT_OT_easy_regular_menu)
    bpy.utils.unregister_class(SCULPT_OT_easy_advanced_settings)
    bpy.utils.unregister_class(SCULPT_OT_easy_brush_settings)
    bpy.utils.unregister_class(EasySculptMenuPreferences)

if __name__ == "__main__":
    register()
