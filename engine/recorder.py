from pi3d.util.Screenshot import screenshot

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

        self.path = path
        self.writer = cv2.VideoWriter(self.path, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), self.engine.fps, (self.engine.width, self.engine.height))
        self.recording = True

        LOGGER.info('started video capture to %s' % self.path)

    def write(self):

        if self.recording:

            self.writer.write(screenshot())

    def stop(self):

        if self.recording:

            self.writer.release()
            self.recording = False

            LOGGER.info('stopped video capture to %s' % self.path)
