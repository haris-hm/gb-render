import bpy 

from bpy.types import Operator, Scene, Context, Event
from .gb_utils import *
    
class RENDER_OT_render(Operator):
    """
    Adapted from: https://blender.stackexchange.com/a/71830    
    """

    bl_idname = "render.render_generated_animation"
    bl_label = "Render Animation"
    bl_description = "Renders the animation based on current settings"
    bl_options = {"REGISTER"}

    timer = None
    animation: AnimationSequence = None
    stop: bool = None
    rendering: bool = None
    masks_rendered: bool = None
    images_rendered: bool = None

    def execute(self, ctx: Context):
        # Validate all relevant objects are selected and the selected directory is valid
        try:
            get_objects(ctx.scene)
            if(not self.__is_path_valid(bpy.path.abspath(ctx.scene.render_settings_elements.directory))):
                raise Exception('Please choose a valid path under "Adjust Render Settings"')
        except Exception as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}

        # Create the animation keyframes based on settings
        frames = create_frames(ctx.scene)
        self.animation = AnimationSequence(ctx, frames)  

        # If rendering only masks or images
        seq_code: int = int(ctx.scene.render_settings_elements.render_sequence)
        print(seq_code)

        if seq_code > 0:
            self.__render(seq_code, self.animation) 
        
        # If rendering masks, then images
        self.stop = False
        self.rendering = False

        self.masks_rendered = False
        self.images_rendered = False

        bpy.app.handlers.render_pre.append(self.pre)
        bpy.app.handlers.render_post.append(self.post)
        bpy.app.handlers.render_cancel.append(self.cancelled)

        self.timer = ctx.window_manager.event_timer_add(0.5, window=ctx.window)
        ctx.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}
    
    def pre(self, scene: Scene, ctx: Context=None):
        self.rendering = True
        self.pause = False

    def post(self, scene: Scene, ctx: Context=None):
        self.rendering = False
    
    def cancelled(self, scene: Scene, ctx: Context=None):
        self.stop = True
    
    def modal(self, ctx: Context, event: Event):
        if event.type == 'TIMER':
            if True in (self.images_rendered, self.stop is True): 
                bpy.app.handlers.render_pre.remove(self.pre)
                bpy.app.handlers.render_post.remove(self.post)
                bpy.app.handlers.render_cancel.remove(self.cancelled)
                ctx.window_manager.event_timer_remove(self.timer)
                
                return {"FINISHED"}
            elif self.rendering is False:
                if not self.masks_rendered:
                    self.__render(2, self.animation)
                    self.masks_rendered = True
                else:
                    self.__render(1, self.animation)
                    self.images_rendered = True
                
        return {"PASS_THROUGH"}
    
    def __is_path_valid(self, path) -> bool:
        if (os.path.exists(path) and os.path.isdir(os.path.abspath(path)) and path != ''):
            return True
        else:
            return False
        
    def __render(self, seq_code: int, animation: AnimationSequence):
        if seq_code == 1:            
            animation.render(FrameType.RAW)
            return {"FINISHED"}
        elif seq_code == 2:
            animation.render(FrameType.MASK)
            return {"FINISHED"}
        