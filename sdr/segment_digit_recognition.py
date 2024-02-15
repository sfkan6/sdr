from .detection import DisplayDetector, DigitDetector
from .digit_recognition import DigitRecognizer
from .image_cutting import ImageCutter


class SDR:
    DisplayDetector = DisplayDetector
    DigitDetector = DigitDetector
    DigitRecognizer = DigitRecognizer
    ImageCutter = ImageCutter

    def __init__(self, image, print_codes=False):
        self._image = image
        self.digits = []
        self.print_codes = print_codes

    @property
    def image(self):
        return self._image.copy()

    def identify_and_get_digits(self):
        self.identify_digits()
        return self.digits

    def identify_digits(self):
        self.digits = [
            self.get_digits_from_display(image_of_display)
            for image_of_display in self.get_images_of_displays()
        ]

    def get_images_of_displays(self):
        DisplayDetector = self.DisplayDetector(self.image)
        frames_of_displays = DisplayDetector.search_and_get_frames()
        return self.ImageCutter(self.image).get_images_by_frames(frames_of_displays)

    def get_digits_from_display(self, image_of_display):
        threshold_images_of_digits = self.get_threshold_images_of_digits(
            image_of_display
        )
        return self.get_digits_by_images(threshold_images_of_digits)

    def get_threshold_images_of_digits(
        self, image_of_display, increase_in_width=3, increase_in_height=6
    ):
        DigitDetector = self.DigitDetector(image_of_display)
        DigitDetector.search_frames()
        frames_of_digits = DigitDetector.get_increased_frames(
            increase_in_width, increase_in_height
        )
        return self.ImageCutter(DigitDetector.threshold_image).get_images_by_frames(
            frames_of_digits
        )

    def get_digits_by_images(self, images_of_digits):
        return [
            self.DigitRecognizer(
                image_of_digit, self.print_codes
            ).define_and_get_digit()
            for image_of_digit in images_of_digits
        ]
