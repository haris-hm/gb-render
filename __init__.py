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
from .ui import UIProperties, VIEW3D_PT_controls, WM_OT_parameter_tuning

classes = [UIProperties, RENDER_OT_render_pairs, WM_OT_parameter_tuning, VIEW3D_PT_controls]
    
def register():
    for c in classes:
        bpy.utils.register_class(c)

        if hasattr(c, 'register') and callable(c.register):
            c.register()
    
def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)

        if hasattr(c, 'unregister') and callable(c.unregister):
            c.register()
    
if __name__ == '__main__':
    register()
