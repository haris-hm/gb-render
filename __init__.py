# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
bl_info = {
    'name': 'GB Render',
    'author': 'Haris Mehuljic',
    'version': (1,0,0),
    'blender': (4,2,0),
    'location': '3D Viewport > Sidebar > Grease Bin Rendering',
    'description': 'Provides a useful UI for adjusting parameters and rendering our grease bins.',
    'category': 'gb-research'
}

import bpy  # noqa: E402

from . import rendering, ui_elements, ui_layout  # noqa: E402

CLASSES = (
    ui_elements.DataElements, 
    ui_elements.ObjectSelectionElements, 
    ui_elements.SegmentationColorsElements,
    ui_elements.MaterialElements,
    ui_elements.ParameterSettingsElements,
    ui_elements.RenderSettingsElements,
    rendering.RENDER_OT_render,
    ui_layout.WM_OT_parameter_tuning, 
    ui_layout.WM_OT_render_settings,
    ui_layout.VIEW3D_PT_objects, 
    ui_layout.VIEW3D_PT_seg_colors,
    ui_layout.VIEW3D_PT_materials,
    ui_layout.VIEW3D_PT_controls
)
    
def register():
    for c in CLASSES:
        bpy.utils.register_class(c)

        if hasattr(c, 'register') and callable(c.register):
            c.register()
    
def unregister():
    for c in reversed(CLASSES):
        bpy.utils.unregister_class(c)

        if hasattr(c, 'unregister') and callable(c.unregister):
            c.register()
    
if __name__ == '__main__':
    register()
