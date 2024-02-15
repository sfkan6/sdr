class DigitRecognizer:
    digit_codes = {
        "0101000": 1,
        "0110111": 2,
        "0101111": 3,
        "1101010": 4,
        "1001111": 5,
        "1011111": 6,
        "0101100": 7,
        "1111111": 8,
        "1101111": 9,
        "1111101": 0,
    }

    def __init__(self, threshold_image, id_mode_debug=False):
        self._threshold_image = threshold_image
        self.horizontal_segments = AnalysisHorizontalSegments(threshold_image)
        self.vertical_segments = AnalysisVerticalSegments(threshold_image)
        self.digit = None
        self.digit_code = None
        self.id_mode_debug = id_mode_debug

    @property
    def threshold_image(self):
        return self._threshold_image.copy()

    def define_and_get_digit(self):
        self.define_digit()
        return self.digit

    def define_digit(self):
        if self.is_digit_one():
            digit = 1
        else:
            self.digit_code = self.get_code_digit()
            digit = self.digit_codes.get(self.digit_code, "")

        self.digit = digit
        if not str(self.digit) and self.id_mode_debug:
            print(self.digit_code)

    def is_digit_one(self):
        height, width = self.threshold_image.shape
        if height > width * 3:
            return True
        return False

    def get_code_digit(self):
        return "".join(
            self.get_hoorizontal_code_of_digit() + self.get_vertical_code_of_digit()
        )

    def get_hoorizontal_code_of_digit(self):
        codes = self.horizontal_segments.get_codes([0.25, 0.75])
        return codes[0] + codes[1]

    def get_vertical_code_of_digit(self):
        vertical_codes = self.vertical_segments.get_codes([0.4, 0.55])
        return self.get_merge_code(vertical_codes)

    def get_merge_code(self, codes):
        number_of_codes = len(codes)
        code_length = len(codes[0])

        merge_code = ["0"] * code_length
        for i in range(code_length):
            if "0" not in [codes[j][i] for j in range(number_of_codes)]:
                merge_code[i] = "1"
        return merge_code


class SegmentAnalysis:
    def __init__(self, threshold_image):
        self.threshold_image = threshold_image

    def get_codes(self, locations):
        lines = self.get_lines(locations)
        return [self.get_code_of_line(line) for line in lines]

    def get_lines(self, locations):
        return [self.get_line(locate) for locate in locations]

    def get_line(self, locate):
        start_point, end_point = self.get_cut_points(locate)
        return self.threshold_image[0:-1, start_point:end_point]

    def get_cut_points(self, locate, side=0):
        size_of_side = self.threshold_image.shape[side]
        start_point = int(round(locate * size_of_side))
        return start_point, start_point + 1

    def get_code_of_line(self, line):
        sections = self.get_sections(line)
        return [self.get_segment_code(section) for section in sections]

    def get_sections(self, line):
        edge = len(line)
        return [line[0:edge]]

    def get_segment_code(self, section, N=6, threshold=100):
        num_in_row = 0
        max_in_row = 0

        for x in section:
            if x >= threshold:
                num_in_row += 1
            else:
                max_in_row = max(max_in_row, num_in_row)
                num_in_row = 0

        if max(max_in_row, num_in_row) > N:
            return "1"
        else:
            return "0"


class AnalysisHorizontalSegments(SegmentAnalysis):
    def get_line(self, locate):
        start_height, end_height = self.get_cut_points(locate)
        return self.threshold_image[start_height:end_height, 0:-1][0]

    def get_cut_points(self, locate, side=0):
        return super().get_cut_points(locate, side)

    def get_sections(self, line):
        edge = int(round(len(line) / 2))
        return [line[0:edge], line[edge:-1]]


class AnalysisVerticalSegments(SegmentAnalysis):
    def get_codes(self, locations):
        lines = self.get_lines(locations)
        return [self.get_code_of_line(line) for line in lines]

    def get_line(self, locate):
        start_width, end_width = self.get_cut_points(locate)
        return self.threshold_image[0:-1, start_width:end_width]

    def get_cut_points(self, locate, side=1):
        return super().get_cut_points(locate, side)

    def get_sections(self, line):
        edge = int(round(len(line) / 4))
        return [line[0:edge], line[edge : edge * 3], line[edge * 3 : -1]]
