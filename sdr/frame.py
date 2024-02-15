import cv2


class Frame:
    def __init__(self, x, y, w, h):
        self.setBoundaries(x, y, w, h)

    @property
    def bounding_rect(self):
        return [self.x, self.y, self.w, self.h]

    def get_start_and_end_points(self):
        return [self.x, self.y, self.x + self.w, self.y + self.h]

    def union(self, frame):
        x = min(self.x, frame.x)
        y = min(self.y, frame.y)
        w = max(self.x + self.w, frame.x + frame.w) - x
        h = max(self.y + self.h, frame.y + frame.h) - y
        self.setBoundaries(x, y, w, h)

    def setBoundaries(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    @classmethod
    def create_from_contour(cls, contour):
        return cls(*cv2.boundingRect(contour))


class FrameOfDisplay(Frame):
    def is_horizontal_rectangle(self):
        if 2 <= self.w / self.h <= 4:
            return True
        return False

    def is_more_n_percent_of_image(self, n, image_width, image_height):
        if n <= self.w / image_width and n <= self.h / image_height:
            return True
        return False

    def is_frame_of_display(self, image_width, image_height):
        if self.is_horizontal_rectangle() and self.is_more_n_percent_of_image(
            0.1, image_width, image_height
        ):
            return True
        return False


class FrameOfDigit(Frame):
    def is_digit_one(self):
        if self.h / 2 > self.w:
            return True
        return False

    def is_nested_by_x(self, frame):
        if self.x + self.w >= frame.x + frame.w:
            return True
        return False

    def is_frame_of_digit(self, image_height):
        if self.is_vertical_rectangle() and self.is_height_more_n_percent_of_display(
            0.5, image_height
        ):
            return True
        return False

    def is_vertical_rectangle(self):
        if 1.2 <= self.h / self.w <= 8:
            return True
        return False

    def is_height_more_n_percent_of_display(self, n, image_height):
        if n <= self.h / image_height:
            return True
        return False

    def get_increase_frame_in_width_or_height(
        self, increase_in_width=0, increase_in_height=0
    ):
        return self.__class__(
            max(0, self.x - increase_in_width // 2),
            max(0, self.y - increase_in_height // 2),
            self.w + increase_in_width,
            self.h + increase_in_height,
        )
