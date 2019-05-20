# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import liblo
import glob
import logging


from utils import osc_range_method
from config import *

LOGGER = logging.getLogger(__name__)

class OscServer(object):

    def __init__(self, port):

        self.server = liblo.ServerThread(port)
        self.server.register_methods(self)
        LOGGER.info("Listening on OSC port: " + str(port))

    def start(self):

        self.server.start()


    @liblo.make_method('/pyta/slide/lock', 'si')
    @liblo.make_method('/pyta/slide/lock', 'ii')
    def slide_lock_cb(self, path, args):

        if args[0] == -1:
            LOGGER.error("ERROR: can't lock all slides")
            return

        slides = self.get_slide(args[0])
        for slide in slides:
            if args[1] == 1:
                if slide not in self.locked_slides:
                    self.locked_slides.append(slide)
            elif args[1] == 0:
                if slide in self.locked_slides:
                    self.locked_slides.remove(slide)

    @liblo.make_method('/pyta/slide/unload', 's')
    @liblo.make_method('/pyta/slide/unload', 'i')
    def slide_unload_cb(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
            slide.unload()

    @liblo.make_method('/pyta/slide/visible', 'si')
    @liblo.make_method('/pyta/slide/visible', 'ii')
    def slide_visible_cb(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
	        slide.set_visible(args[1])

    @liblo.make_method('/pyta/slide/alpha', 'sf')
    @liblo.make_method('/pyta/slide/alpha', 'if')
    def slide_alpha_cb(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
            slide.set_alpha(args[1])

    @liblo.make_method('/pyta/slide/position', 'sfff')
    @liblo.make_method('/pyta/slide/position', 'sff')
    @liblo.make_method('/pyta/slide/position_x', 'sf')
    @liblo.make_method('/pyta/slide/position_y', 'sf')
    @liblo.make_method('/pyta/slide/position_z', 'sf')
    @liblo.make_method('/pyta/slide/position', 'ifff')
    @liblo.make_method('/pyta/slide/position', 'iff')
    @liblo.make_method('/pyta/slide/position_x', 'if')
    @liblo.make_method('/pyta/slide/position_y', 'if')
    @liblo.make_method('/pyta/slide/position_z', 'if')
    def slide_position_cb(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
            if path == "/pyta/slide/position":
                slide.set_position(args[1], args[2], (args[3] + SLIDE_BASE_Z) if len(args) == 4 else slide.z())
            elif path == "/pyta/slide/position_x":
                slide.set_position(args[1], slide.y(), slide.z())
            elif path == "/pyta/slide/position_y":
                slide.set_position(slide.x(), args[1], slide.z())
            elif path == "/pyta/slide/position_z":
                z = slide.z()
                nz = args[1] + SLIDE_BASE_Z
                if z != nz:
                    slide.set_position(slide.x(), slide.y(), nz)
                    self.sort_slides()

    @liblo.make_method('/pyta/slide/translate', 'sfff')
    @liblo.make_method('/pyta/slide/translate', 'sff')
    @liblo.make_method('/pyta/slide/translate_x', 'sf')
    @liblo.make_method('/pyta/slide/translate_y', 'sf')
    @liblo.make_method('/pyta/slide/translate_z', 'sf')
    @liblo.make_method('/pyta/slide/translate', 'ifff')
    @liblo.make_method('/pyta/slide/translate', 'iff')
    @liblo.make_method('/pyta/slide/translate_x', 'if')
    @liblo.make_method('/pyta/slide/translate_y', 'if')
    @liblo.make_method('/pyta/slide/translate_z', 'if')
    def slide_translate_cb(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
            if path == "/pyta/slide/translate":
                slide.set_translation(args[1], args[2], args[3] if len(args) == 4 else 0.0)
            elif path == "/pyta/slide/translate_x":
                slide.set_translation(args[1], 0.0, 0.0)
            elif path == "/pyta/slide/translate_y":
                slide.set_translation(0.0, args[1], 0.0)
            elif path == "/pyta/slide/translate_z":
                slide.set_translation(0.0, 0.0, args[1])
                self.sort_slides()

    @liblo.make_method('/pyta/slide/scale', 'sfff')
    @liblo.make_method('/pyta/slide/scale', 'sff')
    @liblo.make_method('/pyta/slide/scale_x', 'sf')
    @liblo.make_method('/pyta/slide/scale_y', 'sf')
    @liblo.make_method('/pyta/slide/scale_z', 'sf')
    @liblo.make_method('/pyta/slide/relative_scale_xy', 'sf')
    @liblo.make_method('/pyta/slide/rsxy', 'sf')
    @liblo.make_method('/pyta/slide/zoom', 'sf')
    @liblo.make_method('/pyta/slide/scale', 'ifff')
    @liblo.make_method('/pyta/slide/scale', 'iff')
    @liblo.make_method('/pyta/slide/scale_x', 'if')
    @liblo.make_method('/pyta/slide/scale_y', 'if')
    @liblo.make_method('/pyta/slide/scale_z', 'if')
    @liblo.make_method('/pyta/slide/relative_scale_xy', 'if')
    @liblo.make_method('/pyta/slide/rsxy', 'if')
    @liblo.make_method('/pyta/slide/zoom', 'if')
    def slide_scale_cb(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
            if path == "/pyta/slide/scale":
                slide.set_scale(args[1], args[2], args[3] if len(args) == 4 else slide.sz)
            elif path == "/pyta/slide/scale_x":
                slide.set_scale(args[1], slide.sy, slide.sz)
            elif path == "/pyta/slide/scale_y":
                slide.set_scale(slide.sx, args[1], slide.sz)
            elif path == "/pyta/slide/scale_z":
                slide.set_scale(slide.sx, slide.sy, args[1])
            elif path == "/pyta/slide/relative_scale_xy" or path == "/pyta/slide/rsxy" or path == "/pyta/slide/zoom":
                slide.set_zoom(args[1])


    @liblo.make_method('/pyta/slide/reset', 'i')
    @liblo.make_method('/pyta/slide/reset', 's')
    @liblo.make_method('/pyta/slide/scale/reset', 's')
    def slide_reset_scale_cb(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
            slide.reset()

    @liblo.make_method('/pyta/slide/rotate', 'sfff')
    @liblo.make_method('/pyta/slide/rotate_x', 'sf')
    @liblo.make_method('/pyta/slide/rotate_y', 'sf')
    @liblo.make_method('/pyta/slide/rotate_z', 'sf')
    @liblo.make_method('/pyta/slide/rotate', 'ifff')
    @liblo.make_method('/pyta/slide/rotate_x', 'if')
    @liblo.make_method('/pyta/slide/rotate_y', 'if')
    @liblo.make_method('/pyta/slide/rotate_z', 'if')
    def slide_rotate_cb(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
            if path == "/pyta/slide/rotate":
                slide.set_angle(args[1], args[2], args[3])
            elif path == "/pyta/slide/rotate_x":
                slide.set_angle(args[1], slide.ay, slide.az)
            elif path == "/pyta/slide/rotate_y":
                slide.set_angle(slide.ax, args[1], slide.az)
            elif path == "/pyta/slide/rotate_z":
                slide.set_angle(slide.ax, slide.ay, args[1])

    @liblo.make_method('/pyta/slide/animate', None)
    # args: slide param_name from to duration loop
    def slide_animate(self, path, args):
        if not 5 <= len(args) <= 6:
            return
        slides = self.get_slide(args[0])
        for slide in slides:
            slide.animate(*args[1:])

    @liblo.make_method('/pyta/slide/animate/stop', 'i')
    @liblo.make_method('/pyta/slide/animate/stop', 's')
    @liblo.make_method('/pyta/slide/animate/stop', 'is')
    @liblo.make_method('/pyta/slide/animate/stop', 'ss')
    def slide_stop_animate(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
            slide.stop_animate(args[1] if len(args) > 1 else None)


    @liblo.make_method('/pyta/slide/rgb', 'sfff')
    @liblo.make_method('/pyta/slide/rgb', 'ifff')
    def slide_enlighten(self, path, args):
        '''
        Colorize the slide with rgb color.
        '''
        slides = self.get_slide(args[0])
        for slide in slides:
            slide.set_color((args[1], args[2], args[3]))

    @liblo.make_method('/pyta/slide/rgb/strobe', 'ii')
    @liblo.make_method('/pyta/slide/rgb/strobe', 'si')
    def set_slide_color_strobe(self, path, args):
        '''
        Enable color shit show
        '''
        slides = self.get_slide(args[0])
        for slide in slides:
            slide.set_color_strobe(args[1])

    @liblo.make_method('/pyta/slide/strobe', 'ii')
    @liblo.make_method('/pyta/slide/strobe', 'iiff')
    @liblo.make_method('/pyta/slide/strobe', 'si')
    @liblo.make_method('/pyta/slide/strobe', 'siff')
    def set_slide_strobe(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
            slide.set_strobe(*args[1:])

    @liblo.make_method('/pyta/slide/strobe/period', 'if')
    @liblo.make_method('/pyta/slide/strobe/period', 'sf')
    def set_slide_strobe_len(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
            slide.set_strobe(None, args[1], None)

    @liblo.make_method('/pyta/slide/strobe/ratio', 'if')
    @liblo.make_method('/pyta/slide/strobe/ratio', 'sf')
    def set_slide_strobe_per(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
            slide.set_strobe(None, None, args[1])


    @liblo.make_method('/pyta/slide/clone', 'ss')
    def slide_clone(self, path, args):
        '''
        Create a slide clone
        '''
        slides = self.get_slide(args[0])
        if len(slides) > 1:
            LOGGER.error('ERROR: cannot clone more than one slide at a time')
        elif len(slides) == 1:
            if args[1] not in self.slides:
                self.slides[args[1]] = slides[0].clone(args[1])
                self.sort_slides()

    @liblo.make_method('/pyta/slide/load_file', 's')
    def slide_load_file_cb(self, path, args):
        files = glob.glob(args[0])
        if len(files):
            for file in files:
                self.fileQ.put(file)
        else:
            LOGGER.info("ERROR: file \"%s\" not found" % args[0])

    @liblo.make_method('/pyta/slide/slide_info', 'si')
    @liblo.make_method('/pyta/slide/slide_info', 'ii')
    def slide_info_cb(self, path, args, types, src):
        slides = self.get_slide(args[0])
        for slide in slides:
            dest = src.get_url().split(":")[0] + ':' + src.get_url().split(":")[1] + ':' + str(args[1])
            prefix = '/pyta/slide_info/'
            liblo.send(dest, prefix + 'slidenumber', args[0])
            liblo.send(dest, prefix + 'position', slide.x(), slide.y(), slide.z())
            liblo.send(dest, prefix + 'scale', slide.sx, slide.sy, slide.sz)
            liblo.send(dest, prefix + 'angle', slide.ax, slide.ay, slide.az)
            liblo.send(dest, prefix + 'visible', slide.visible)
            liblo.send(dest, prefix + 'alpha', slide.alpha())

    @liblo.make_method('/pyta/slide/save_state', 's')
    @liblo.make_method('/pyta/slide/save_state', 'i')
    def slide_save_state(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
            prefix = '/pyta/slide/'
            filename = 's' + str(slide.name + '.state')
            LOGGER.info('Write in progress in ' + filename)

            statef = open(filename, 'w')
            statef.write("slide " + str(args[0]) + "\n")
            statef.write("file " + str(slide.path) + "\n")
            statef.write("position " + str(slide.x()) + " " + str(slide.y()) + " " + str(slide.z()) + "\n")
            statef.write("scale " + str(slide.sx) + " " + str(slide.sy) + " " + str(slide.sy) + "\n")
            statef.write("angle " + str(slide.ax) + " " + str(slide.ay) + " " + str(slide.az) + "\n")
            statef.write("alpha " + str(slide.alpha()) + "\n")
            statef.close()

    @liblo.make_method('/pyta/slide/load_state', 's')
    def slide_load_state(self, path, args):
        statef = open(args[0], 'r')
        param = statef.read()
        # sn = int(param.split("\n")[0].split(" ")[1])
        # fn = param.split("\n")[1].split(" ")[1]
        sn = param.split("\n")[0].split(" ")[1]
        pos = param.split("\n")[2].split(" ")[1:]
        sc = param.split("\n")[3].split(" ")[1:]
        ag = param.split("\n")[4].split(" ")[1:]
        al = float(param.split("\n")[5].split(" ")[1])

        slides = self.get_slide(sn)
        for slide in slides:
            # self.slide_load_file_cb('/hop', (fn))
            slide.position(float(pos[0]), float(pos[1]), float(pos[2]))
            slide.set_scale(float(sc[0]), float(sc[1]), float(sc[2]))
            slide.set_angle(float(ag[0]), float(ag[1]), float(ag[2]))
            slide.set_alpha(al)


    @liblo.make_method('/pyta/slide/play', 'i')
    @liblo.make_method('/pyta/slide/play', 's')
    def set_slide_gif_play(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
            slide.gif_reset()

    @liblo.make_method('/pyta/slide/speed', 'if')
    @liblo.make_method('/pyta/slide/speed', 'sf')
    def set_slide_gif_speed(self, path, args):
        slides = self.get_slide(args[0])
        if args[1] == 0:
            args[1] = 1.0
        for slide in slides:
            slide.gif_speed = float(args[1])

    @liblo.make_method('/pyta/slide/duration', 'if')
    @liblo.make_method('/pyta/slide/duration', 'sf')
    def set_slide_gif_duration(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
            slide.gif_duration = args[1]

    @liblo.make_method('/pyta/slide/tiles', 'iff')
    @liblo.make_method('/pyta/slide/tiles', 'sff')
    @liblo.make_method('/pyta/slide/tiles', 'if')
    @liblo.make_method('/pyta/slide/tiles', 'sf')
    def set_slide_tiles(self, path, args):
        slides = self.get_slide(args[0])
        for slide in slides:
            slide.set_tiles(args[1], args[2] if len(args) == 3 else args[1])


    @liblo.make_method('/pyta/text', 'is')
    @osc_range_method(N_TEXTS)
    def set_text_string(self, path, args):
        self.text[args[0]].set_text(args[1])

    @liblo.make_method('/pyta/text/reset', 'i')
    @osc_range_method(N_TEXTS)
    def set_text_reset(self, path, args):
        self.text[args[0]].reset()

    @liblo.make_method('/pyta/text/size', 'if')
    @liblo.make_method('/pyta/text/size', 'is')
    @osc_range_method(N_TEXTS)
    def set_text_size(self, path, args):
        self.text[args[0]].set_size(args[1])

    @liblo.make_method('/pyta/text/scale', 'iff')
    @liblo.make_method('/pyta/text/scale_x', 'if')
    @liblo.make_method('/pyta/text/scale_y', 'if')
    @liblo.make_method('/pyta/text/zoom', 'if')
    @osc_range_method(N_TEXTS)
    def set_text_scale(self, path, args):
        text = self.text[args[0]]
        if path == "/pyta/text/scale":
            text.set_scale(args[1], args[2])
        elif path == "/pyta/text/scale_x":
            text.set_scale(args[1], text.sy)
        elif path == "/pyta/text/scale_y":
            text.set_scale(text.sx, args[1])
        elif path == "/pyta/text/scale_z":
            text.set_scale(text.sx, text.sy)
        elif path == "/pyta/text/zoom":
            text.set_zoom(args[1])

    @liblo.make_method('/pyta/text/visible', 'ii')
    @osc_range_method(N_TEXTS)
    def set_text_visible(self, path, args):
        self.text[args[0]].set_visible(args[1])

    @liblo.make_method('/pyta/text/strobe', 'ii')
    @liblo.make_method('/pyta/text/strobe', 'iiff')
    @osc_range_method(N_TEXTS)
    def set_text_strobe(self, path, args):
        self.text[args[0]].set_strobe(*args[1:])

    @liblo.make_method('/pyta/text/strobe/period', 'if')
    @osc_range_method(N_TEXTS)
    def set_text_strobe_len(self, path, args):
        self.text[args[0]].set_strobe(None, args[1], None)

    @liblo.make_method('/pyta/text/strobe/ratio', 'if')
    @osc_range_method(N_TEXTS)
    def set_text_strobe_per(self, path, args):
        self.text[args[0]].set_strobe(None, None, args[1])

    @liblo.make_method('/pyta/text/position', 'iii')
    @liblo.make_method('/pyta/text/position_x', 'ii')
    @liblo.make_method('/pyta/text/position_y', 'ii')
    @osc_range_method(N_TEXTS)
    def set_text_position(self, path, args):
        if path == '/pyta/text/position':
            self.text[args[0]].set_position(args[1], args[2])
        elif path == '/pyta/text/position_x':
            self.text[args[0]].set_position(args[1], None)
        elif path == '/pyta/text/position_y':
            self.text[args[0]].set_position(None, args[1])

    @liblo.make_method('/pyta/text/rotate', 'ifff')
    @liblo.make_method('/pyta/text/rotate_x', 'if')
    @liblo.make_method('/pyta/text/rotate_y', 'if')
    @liblo.make_method('/pyta/text/rotate_z', 'if')
    @osc_range_method(N_TEXTS)
    def set_text_rotate_x(self, path, args):
        if path == '/pyta/text/rotate':
            self.text[args[0]].set_rotation(args[1], args[2], args[3])
        elif path == '/pyta/text/rotate_x':
            self.text[args[0]].set_rotation(args[1], None, None)
        elif path == '/pyta/text/rotate_y':
            self.text[args[0]].set_rotation(None, args[1], None)
        elif path == '/pyta/text/rotate_z':
            self.text[args[0]].set_rotation(None, None, args[1])

    @liblo.make_method('/pyta/text/align', 'iss')
    @osc_range_method(N_TEXTS)
    def set_text_align(self, path, args):
        self.text[args[0]].set_align(args[1], args[2])

    @liblo.make_method('/pyta/text/rgb', 'iiiii')
    @liblo.make_method('/pyta/text/rgb', 'iiii')
    @osc_range_method(N_TEXTS)
    def set_text_color(self, path, args):
        self.text[args[0]].set_color((args[1] / 255., args[2] / 255., args[3] / 255.))
        if len(args) == 5:
            self.text[args[0]].set_alpha(args[4] / 255.)

    @liblo.make_method('/pyta/text/rgb/strobe', 'ii')
    @osc_range_method(N_TEXTS)
    def set_text_color_strobe(self, path, args):
        self.text[args[0]].set_color_strobe(args[1])

    @liblo.make_method('/pyta/text/alpha', 'if')
    @osc_range_method(N_TEXTS)
    def set_text_alpha(self, path, args):
        self.text[args[0]].set_alpha(args[1])

    @liblo.make_method('/pyta/text/animate', 'isfff')
    @liblo.make_method('/pyta/text/animate', 'issff')
    @liblo.make_method('/pyta/text/animate', 'isfsf')
    @liblo.make_method('/pyta/text/animate', 'isssf')
    @osc_range_method(N_TEXTS)
    def text_animate(self, path, args):
        self.text[args[0]].animate(*args[1:])

    @liblo.make_method('/pyta/text/animate/stop', 'is')
    @liblo.make_method('/pyta/text/animate/stop', 'i')
    @osc_range_method(N_TEXTS)
    def text_stop_animate(self, path, args):
        self.text[args[0]].stop_animate(args[1] if len(args) > 1 else None)


    @liblo.make_method('/pyta/post_process/active', 'f')
    @liblo.make_method('/pyta/post_process/active', 'i')
    def post_process_active(self, path, args):
        self.post_process.set_visible(args[0])

    @liblo.make_method('/pyta/post_process/animate', None)
    def post_process_animate(self, path, args):
        if 4 <= len(args) <= 5:
            self.post_process.animate(*args)

    @liblo.make_method('/pyta/post_process/animate/stop', '')
    @liblo.make_method('/pyta/post_process/animate/stop', 's')
    def post_process_animate_stop(self, path, args):
        self.post_process.stop_animate(args[0] if len(args) > 0 else None)

    @liblo.make_method('/pyta/post_process/set_all', None)
    def post_process_set_all(self, path, args):
        if len(args) > 0:
            self.post_process.set_visible(args[0])
        if len(args) > 1:
            self.post_process.set_glitch_strength(args[1])
        if len(args) > 2:
            self.post_process.set_glitch_noise(args[2])
        if len(args) > 3:
            self.post_process.set_color_hue(args[3])
        if len(args) > 4:
            self.post_process.set_color_saturation(args[4])
        if len(args) > 5:
            self.post_process.set_color_value(args[5])
        if len(args) > 6:
            self.post_process.set_color_alpha(args[6])
        if len(args) > 7:
            self.post_process.set_color_invert(args[7])

    @liblo.make_method('/pyta/post_process/glitch/strength', 'f')
    def post_process_glitch(self, path, args):
        self.post_process.set_glitch_strength(args[0])

    @liblo.make_method('/pyta/post_process/glitch/noise', 'f')
    def post_process_noise(self, path, args):
        self.post_process.set_glitch_noise(args[0])

    @liblo.make_method('/pyta/post_process/color/hue', 'f')
    def post_process_hue(self, path, args):
        self.post_process.set_color_hue(args[0])

    @liblo.make_method('/pyta/post_process/color/saturation', 'f')
    def post_process_saturation(self, path, args):
        self.post_process.set_color_saturation(args[0])

    @liblo.make_method('/pyta/post_process/color/value', 'f')
    def post_process_value(self, path, args):
        self.post_process.set_color_value(args[0])

    @liblo.make_method('/pyta/post_process/color/alpha', 'f')
    def post_process_alpha(self, path, args):
        self.post_process.set_color_alpha(args[0])

    @liblo.make_method('/pyta/post_process/color/invert', 'f')
    def post_process_invert(self, path, args):
        self.post_process.set_color_invert(args[0])


    @liblo.make_method('/pyta/post_process/tiles', 'ff')
    @liblo.make_method('/pyta/post_process/tiles', 'f')
    def post_process_tiles(self, path, args):
        self.post_process.set_tiles(args[0], args[1] if len(args) == 2 else args[0])

    @liblo.make_method('/pyta/post_process/reset', None)
    def post_process_reset(self, path, args):
        self.post_process.reset()
