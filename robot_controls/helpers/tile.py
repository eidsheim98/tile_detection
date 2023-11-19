class TileInfo():
    def __init__(self, image, offset, box):
        self.image = image
        self.offset = offset
        self.box = box
        self.rotated = None
        self.has_crack = False
        self.contour = None
        self.image_with_contour = None

    def set_crack_info(self, contour):
        self.has_crack = True
        self.contour = contour