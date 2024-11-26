import bpy 
from bpy.types import Operator, Scene, Context, Event
from .gb_utils import *
class RENDER_OT_render_pairs(Operator):
    """
    Adapted from: https://blender.stackexchange.com/a/71830    
    """

    bl_idname = "render.render_pairs"
    bl_label = "Render Pairs"

    timer = None
    frames: list[RenderFrame] = []
    stop = None
    rendering = None

    def pre(self, scene: Scene, ctx: Context=None):
        self.rendering = True

    def post(self, scene: Scene, ctx: Context=None):
        self.frames.pop(0)
        self.rendering = False
    
    def cancelled(self, scene: Scene, ctx: Context=None):
        self.stop = True

    def execute(self, ctx: Context):
        self.stop = False
        self.rendering = False
        self.frames = create_frames(ctx.scene)

        bpy.app.handlers.render_pre.append(self.pre)
        bpy.app.handlers.render_post.append(self.post)
        bpy.app.handlers.render_cancel.append(self.cancelled)

        self.timer = ctx.window_manager.event_timer_add(0.5, window=ctx.window)
        ctx.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}
    
    def modal(self, ctx: Context, event: Event):
        if event.type == 'TIMER':
            if self.stop and len(self.frames) == 0:
                bpy.app.handlers.render_pre.remove(self.pre)
                bpy.app.handlers.render_post.remove(self.post)
                bpy.app.handlers.render_cancel.remove(self.cancelled)
                ctx.window_manager.event_timer_remove(self.timer)
                
                return {"FINISHED"}
            elif self.rendering is False:
                self.frames[0].render()
                
        return {"PASS_THROUGH"}
