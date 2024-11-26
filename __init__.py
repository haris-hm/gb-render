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
    'name': 'Grease Bin Rendering',
    'author': 'Haris Mehuljic',
    'version': (0, 0, 1),
    'blender': (4,2,0),
    'location': '3D Viewport > Sidebar > Grease Bin Rendering',
    'description': 'Provides a useful UI for adjusting parameters and rendering our grease bins.',
    'category': 'gb-research'
}

import bpy
from .gb_utils import *
from .operators import RENDER_OT_render_pairs
from .ui import MyAddonProperties, VIEW3D_PT_custom_panel

classes = [MyAddonProperties, RENDER_OT_render_pairs, VIEW3D_PT_custom_panel]
    
def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Scene.my_addon_props = bpy.props.PointerProperty(type=MyAddonProperties)
    
def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)

    del bpy.types.Scene.my_addon_props
    
if __name__ == '__main__':
    register()
