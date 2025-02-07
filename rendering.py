import bpy 

from bpy.types import Operator, Scene, Context, Event
from .gb_utils import *

class RENDER_OT_render_queued_items(Operator):
    """
    Adapted from: https://blender.stackexchange.com/a/71830    
    """

    bl_idname = "render.render_queued_items"
    bl_label = "Render Images"
    bl_description = "Renders all images in the render queue. Make sure to select all relevant objects"
    bl_options = {"REGISTER"}

    timer = None
    frames: RenderQueue = None
    stop: bool = None
    rendering: bool = None

    def pre(self, scene: Scene, ctx: Context=None):
        self.rendering = True
        self.pause = False

    def post(self, scene: Scene, ctx: Context=None):
        self.rendering = False
    
    def cancelled(self, scene: Scene, ctx: Context=None):
        self.stop = True

    def execute(self, ctx: Context):
        self.stop = False
        self.rendering = False
        props = ctx.scene.ui_properties

        try:
            get_objects(ctx.scene)

            if(not self.__is_path_valid(bpy.path.abspath(ctx.scene.ui_properties.directory))):
                raise Exception('Please choose a valid path under "Adjust Render Settings"')
        except Exception as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}

        self.frames = create_frames(ctx.scene)
        print(self.frames)

        # Render progress bar
        props.show_render_progress = True
        props.render_progress = 0.0
        ctx.area.tag_redraw()

        bpy.app.handlers.render_pre.append(self.pre)
        bpy.app.handlers.render_post.append(self.post)
        bpy.app.handlers.render_cancel.append(self.cancelled)

        self.timer = ctx.window_manager.event_timer_add(0.5, window=ctx.window)
        ctx.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}
    
    def modal(self, ctx: Context, event: Event):
        if event.type == 'TIMER':
            if True in (not self.frames, self.stop is True): 
                bpy.app.handlers.render_pre.remove(self.pre)
                bpy.app.handlers.render_post.remove(self.post)
                bpy.app.handlers.render_cancel.remove(self.cancelled)
                ctx.window_manager.event_timer_remove(self.timer)
                
                return {"FINISHED"}
            elif self.rendering is False:
                props = ctx.scene.ui_properties

                try:
                    self.frames.pop().render()
                    # Update progress bar
                    props.render_progress = self.frames.current_frame()/self.frames.full_length() if self.frames.full_length() > 0 else 1.0
                    ctx.area.tag_redraw()
                except Exception as e:
                    self.report({"ERROR"}, str(e))
                    return {"CANCELLED"}
                
        return {"PASS_THROUGH"}
    
    def __is_path_valid(self, path) -> bool:
        if (os.path.exists(path) and os.path.isdir(os.path.abspath(path)) and path != ''):
            return True
        else:
            return False
class RENDER_OT_generate_keyframes(Operator):
    bl_idname = "render.generate_keyframes"
    bl_label = "Generate Keyframes"
    bl_description = "Generates keyframes based on defined parameters"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, ctx: Context):
        frames = create_frames(ctx.scene, True)
        frames.generate_keyframes(ctx)        
        return {"FINISHED"}

class RENDER_OT_render_mask_animation(Operator):
    bl_idname = "render.render_masks"
    bl_label = "Render Mask Animation"
    bl_description = "Renders all masks as an animation"
    bl_options = {"REGISTER"}

    def execute(self, ctx: Context):
        frames = create_frames(ctx.scene, True)
        animation = AnimationSequence(ctx, frames)       
        animation.render_masks()
        return {"FINISHED"}
    
class RENDER_OT_render_image_animation(Operator):
    bl_idname = "render.render_images"
    bl_label = "Render Image Animation"
    bl_description = "Renders all images as an animation"
    bl_options = {"REGISTER"}

    def execute(self, ctx: Context):
        frames = create_frames(ctx.scene, True)
        animation = AnimationSequence(ctx, frames)       
        animation.render_images()
        return {"FINISHED"}
    
class RENDER_OT_render(Operator):
    bl_idname = "render.render_images_then_masks"
    bl_label = "Render Animation"
    bl_description = "Renders the animation based on current settings"
    bl_options = {"REGISTER"}

    def execute(self, ctx: Context):
        frames = create_frames(ctx.scene, True)
        animation = AnimationSequence(ctx, frames)       
        animation.render_images()
        return {"FINISHED"}



    

    