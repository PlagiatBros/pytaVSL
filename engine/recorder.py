from pi3d.util.Screenshot import screenshot

import logging

LOGGER = logging.getLogger(__name__)

class Recorder(object):

    def __init__(self, engine):

        self.engine = engine
        self.path = None
        self.writer = None
        self.recording = False

    def start(self, path):

        try:
            global cv2
            import cv2
        except:
            LOGGER.error('python-opencv is required to record videos')
            return

        if self.recording:
            self.stop()

        ext =  path.split('.')[-1].lower()
        if ext == 'avi':
            fourcc = ('M', 'J', 'P', 'G')
        elif ext == 'mp4':
            fourcc = ('a', 'v', 'c', '1')
        else:
            LOGGER.error('no codec preset for video extension "%s"' % ext)
            return

        self.path = path
        self.writer = cv2.VideoWriter(self.path, cv2.VideoWriter_fourcc(*fourcc), self.engine.fps, (self.engine.width, self.engine.height))
        self.recording = True

        LOGGER.info('started video capture to %s' % self.path)

    def write(self):

        frame = screenshot()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.writer.write(frame)

    def stop(self):

        self.writer.release()
        self.recording = False

        LOGGER.info('stopped video capture to %s' % self.path)
