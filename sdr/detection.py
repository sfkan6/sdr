import cv2, numpy as np
from .frame import Frame, FrameOfDigit, FrameOfDisplay


class Detector:
    Frame = Frame

    def __init__(self, image):
        self._image = image
        self._threshold_image = self.get_threshold_image()
        self.frames = []

    @property
    def image(self):
        return self._image.copy()

    @property
    def threshold_image(self):
        return self._threshold_image.copy()

    def get_width_and_height_of_image(self):
        height, width, _ = self.image.shape
        return width, height

    def search_and_get_frames(self):
        self.search_frames()
        return self.frames

    def search_frames(self):
        threshold_image = self.threshold_image
        contours, _ = cv2.findContours(
            threshold_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )
        self.frames = self.get_frames_by_contours(contours)
        self.frames = self.get_filtered_frames()
        self.frames = self.get_sorted_frames()

    def get_threshold_image(self):
        image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        _, threshold_image = cv2.threshold(image, 0, 255, cv2.THRESH_OTSU)
        kernel = np.ones((3, 3), np.uint8)
        threshold_image = cv2.morphologyEx(
            threshold_image, cv2.MORPH_CLOSE, kernel, iterations=5
        )
        threshold_image = cv2.morphologyEx(
            threshold_image, cv2.MORPH_OPEN, kernel, iterations=1
        )
        return threshold_image

    def get_filtered_frames(self):
        return self.frames

    def get_sorted_frames(self):
        return sorted(self.frames, key=lambda frame: frame.x)

    def get_frames_by_contours(self, contours):
        return [self.Frame(*cv2.boundingRect(contour)) for contour in contours]


class DisplayDetector(Detector):
    Frame = FrameOfDisplay

    hsv_ranges = [((0, 100, 30), (10, 255, 255)), ((175, 0, 40), (180, 255, 255))]

    def __init__(self, image, hsv_ranges=None):
        super().__init__(image)
        self.hsv_ranges = hsv_ranges or self.hsv_ranges

    def get_threshold_image(self):
        threshold_image = self.get_mask()
        kernel = np.ones((3, 3), np.uint8)
        threshold_image = cv2.morphologyEx(
            threshold_image, cv2.MORPH_OPEN, kernel, iterations=3
        )
        return threshold_image

    def get_mask(self):
        image = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        h, w, _ = self.image.shape
        mask = np.zeros((h, w), np.uint8)
        for hsv_range in self.hsv_ranges:
            mask += cv2.inRange(image.copy(), *hsv_range)
        return mask

    def get_filtered_frames(self):
        image_width, image_height = self.get_width_and_height_of_image()
        return [
            frame
            for frame in self.frames
            if frame.is_frame_of_display(image_width, image_height)
        ]


class DigitDetector(Detector):
    Frame = FrameOfDigit

    def get_increased_frames(self, increase_in_width=3, increase_in_height=6):
        return [
            frame.get_increase_frame_in_width_or_height(
                increase_in_width, increase_in_height
            )
            for frame in self.frames
        ]

    def search_frames(self):
        super().search_frames()
        self.frames = self.get_merging_of_close_frames()

    def get_filtered_frames(self):
        _, image_height = self.get_width_and_height_of_image()
        return [frame for frame in self.frames if frame.is_frame_of_digit(image_height)]

    def get_merging_of_close_frames(self):
        frames = self.frames
        i = 0
        while i < len(frames) - 1:
            if frames[i].is_nested_by_x(frames[i + 1]):
                frames[i].union(frames[i + 1])
                frames.pop(i + 1)
            else:
                i += 1
        return frames
