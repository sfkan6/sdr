class ImageCutter:
    def __init__(self, image):
        self._image = image

    @property
    def image(self):
        return self._image.copy()

    def get_images_by_frames(self, frames):
        return [self.get_cropped_image_by_frame(frame) for frame in frames]

    def get_cropped_image_by_frame(self, frame):
        x0, y0, x1, y1 = frame.get_start_and_end_points()
        return self.image[y0:y1, x0:x1]
