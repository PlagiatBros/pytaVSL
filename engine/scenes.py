# encoding: utf-8

from osc import osc_method

import glob
import traceback
from threading import Thread

import toml
tomlencoder = toml.TomlEncoder()
def dump_float(f):
    return "%g" % f
tomlencoder.dump_funcs[float] = dump_float

import logging
LOGGER = logging.getLogger(__name__)

class Scenes(object):

    def __init__(self, *args, **kwargs):

        super(Scenes, self).__init__(*args, **kwargs)

        self.scenes = {}

    def scene_get(self):
        scene = {}

        for n in self.slides:
            slide = self.slides[n]
            if slide.visible:
                if not 'slides' in scene:
                    scene['slides'] = {}
                scene['slides'][slide.name] = slide.state_get()
                if slide.is_clone:
                    if not 'clones' in scene:
                        scene['clones'] = {}
                    scene['clones'][slide.name] = {'target': slide.is_clone}
                if slide.is_group:
                    if not 'groups' in scene:
                        scene['groups'] = {}
                    scene['groups'][slide.name] = {'children': slide.is_group}

        for n in self.texts:
            slide = self.texts[n]
            if slide.visible:
                if not 'texts' in scene:
                    scene['texts'] = {}
                scene['texts'][slide.name] = slide.state_get()

        if self.post_process.visible:
            scene['post_process'] = self.post_process.state_get()

        return scene

    @osc_method('scene_save')
    def scene_save(self, name):
        """
        Save current scene (visible slides/texts/clones/groups' state)
            name: slot name
        """
        name = str(name).lower()

        self.scenes[name] = self.scene_get()

    @osc_method('scene_recall')
    def scene_recall(self, name):
        """
        Recall scene (visible slides/texts/clones/groups' state)
            name: slot name
        """
        name = str(name).lower()

        if name not in self.scenes:
            LOGGER.error('scene "%s" not found' % name)
            return

        for slide in self.sorted_slides:
            slide.set_visible(0)

        scene = self.scenes[name]

        if 'clones' in scene:
            for name in scene['clones']:
                self.create_clone(*scene['clones'][name]['target'], clone_name=name)

        if 'groups' in scene:
            for name in scene['groups']:
                self.create_group(*scene['groups'][name]['children'], group_name=name)

        if 'slides' in scene:
            for name in scene['slides']:
                self.slides[name].state_set(scene['slides'][name], reset=True)

        if 'texts' in scene:
            for name in scene['texts']:
                self.texts[name].state_set(scene['texts'][name], reset=True)

        if 'post_process' in scene:
            self.post_process.state_set(scene['post_process'], reset=True)
        else:
            self.post_process.set_visible(0)

    @osc_method('scene_export')
    def scenes_export(self, file_or_name, file=None):
        """
        Save scene to file (visible slides/texts/clones/groups' state)
            file_or_name: scene slot name or file path to save current scene
            file: file path (if file_or_name is a slot name)
        """

        if file:
            name = str(file_or_name).lower()
            if name not in self.scenes:
                LOGGER.error('scene "%s" not found' % name)
                return
            scene = self.scenes[name]
        else:
            scene = self.scene_get()
            file = file_or_name

        def threaded():

            try:
                content  = '# pytaVSL scene file\n\n'
                content += toml.dumps(scene, tomlencoder)
                # content = content.replace(',]', ' ]')
                # content = content.replace(',]', '')
                # content = content.replace('= [ ', '= ')
                writer = open(file, 'w')
                writer.write(content)
                writer.close()
            except Exception as e:
                LOGGER.error('could not export scene to file %s' % file)
                print(traceback.format_exc())

        t = Thread(target=threaded)
        t.daemon = True
        t.start()

    @osc_method('scene_import')
    def scenes_import(self, *files):
        """
        Load scene files
            files: file path or glob patterns. Each scene is named after the file (whitout the extension)
        """
        paths = []
        for f in files:
            paths += glob.glob(f)

        size = len(paths)
        if len(paths) == 0:
            LOGGER.error("file \"%s\" not found" % files)

        def threaded():

            for i in range(size):
                try:
                    path = paths[i]
                    name = path.split('/')[-1].split('.')[0].lower()
                    _content = open(path, 'r').read()
                    # content = ''
                    # for line in _content.split('\n'):
                    #     if '=' in line:
                    #         line += ']'
                    #     content += line + '\n'
                    # content = content.replace('=', '= [')
                    self.scenes[name] = toml.loads(_content)
                except Exception as e:
                    LOGGER.error('could not load scene file %s' % path)
                    print(traceback.format_exc())

        t = Thread(target=threaded)
        t.daemon = True
        t.start()
