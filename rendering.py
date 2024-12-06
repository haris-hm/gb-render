import bpy 

from bpy.types import Operator, Scene, Context, Event
from .gb_utils import *
from .ui import UIProperties

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
        
class RENDER_OT_render_as_animation(Operator):
    """
    Adapted from: https://blender.stackexchange.com/a/71830    
    """

    bl_idname = "render.render_as_animation"
    bl_label = "Render as Animation"
    bl_description = "Creates keyframes for each state. Can be faster when rendering, but can only render all masks, then all images"
    bl_options = {"REGISTER"}

    timer = None
    animation: AnimationSequence = None
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

        frames = create_frames(ctx.scene, sequence_override=True)
        self.animation = AnimationSequence(ctx, frames)

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
            if self.stop is True and self.animation.fully_rendered: 
                bpy.app.handlers.render_pre.remove(self.pre)
                bpy.app.handlers.render_post.remove(self.post)
                bpy.app.handlers.render_cancel.remove(self.cancelled)
                ctx.window_manager.event_timer_remove(self.timer)
                
                return {"FINISHED"}
            elif self.rendering is False:
                try:
                    if (self.animation.rendered_masks):
                        self.animation.render_images()
                    else:
                        self.animation.render_masks()
                except Exception as e:
                    self.report({"ERROR"}, str(e))
                    return {"CANCELLED"}
                
        return {"PASS_THROUGH"}
    
    def __is_path_valid(self, path) -> bool:
        if (os.path.exists(path) and os.path.isdir(os.path.abspath(path)) and path != ''):
            return True
        else:
            return False

def create_frames(scene: Scene, sequence_override: bool=False) -> RenderQueue:
    cfg: RenderConfig = RenderConfig(scene)

    # Creating Directories
    if (not os.path.exists(cfg.mask_dir)):
        os.mkdir(cfg.mask_dir)
    if (not os.path.exists(cfg.image_dir)):
        os.mkdir(cfg.image_dir)

    # Loop variables
    image_frames: RenderQueue = RenderQueue()
    mask_frames: RenderQueue = RenderQueue()
    paired_frames: RenderQueue = RenderQueue()

    curr_azimuth: int = 0
    curr_elevation: int = 0
    file_name_counter = 0

    while curr_elevation <= cfg.max_elevation:
        while curr_azimuth < 360:
            scene_data: SceneData = SceneData(scene, curr_azimuth, curr_elevation, cfg.focal_length, cfg.liquid_level)
            mask_file_name = f'{cfg.mask_prefix}_{file_name_counter:>08}.png'
            image_file_name = f'{cfg.image_prefix}_{file_name_counter:>08}.png'

            image = RenderFrame(cfg.image_dir, image_file_name, scene, FrameType.RAW, scene_data, width=cfg.width, height=cfg.height, samples=cfg.sample_amount)
            mask = RenderFrame(cfg.mask_dir, mask_file_name, scene, FrameType.MASK, scene_data, width=cfg.width, height=cfg.height)

            image_frames.add(image)
            mask_frames.add(mask)
            paired_frames.add(image).add(mask)

            file_name_counter += 1
            curr_azimuth += cfg.azimuth_step

        curr_elevation += cfg.elevation_step
        curr_azimuth = 0

    if sequence_override:
        return image_frames

    # Return correct render queue
    if cfg.sequence_setting == 0:
        return paired_frames
    elif cfg.sequence_setting == 1:
        return mask_frames + image_frames
    elif cfg.sequence_setting == 2:
        return image_frames
    else:
        return mask_frames
    