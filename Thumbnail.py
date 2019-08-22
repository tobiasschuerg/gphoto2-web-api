import logging

from PIL import Image


def create_thumb(original_file, filename_thumb, base_width=400):
    """
    Creates a thumbnail for a given image.
    """
    logging.debug("Create thumbnail with " + str(base_width) + "px width")
    img = Image.open(original_file)
    width_percentage = (base_width / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(width_percentage)))
    img = img.resize((base_width, hsize), Image.ANTIALIAS)
    logging.debug("Saving file to " + filename_thumb)
    img.save(filename_thumb)
    logging.info("Thumbnail created " + filename_thumb)
