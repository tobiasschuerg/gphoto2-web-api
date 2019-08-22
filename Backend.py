import logging
import os
import shutil
from os.path import expanduser
from pathlib import Path

import gphoto2
import shortuuid
from PIL import Image
from flask import Flask, send_from_directory
from gphoto2 import gp_camera_exit, gp_context_new, gp_camera_init, \
    gp_camera_new, gp_camera_get_summary, GPhoto2Error

THUMBNAIL_PREFIXX = "thumb/"

app = Flask(__name__)

logging.root.setLevel(logging.DEBUG)
logging.getLogger("gphoto2").disabled = True


@app.route('/photo/<photo_id>')
def get_photo(photo_id):
    logging.info("Requested photo with id " + photo_id)
    path = expanduser("~") + "/booth/"
    filename = photo_id + ".jpg"
    file_size = os.path.getsize(path + filename)
    logging.debug("File size: " + convert_bytes(file_size))
    return send_from_directory(path, filename)


@app.route('/thumb/<photo_id>')
def get_thumb(photo_id):
    logging.info("Requested photo with id " + photo_id)
    path = expanduser("~") + "/booth/"
    filename = photo_id + ".jpg"
    file_size = os.path.getsize(path + filename)
    logging.debug("File size original: " + convert_bytes(file_size))

    thumbnail_path = path + THUMBNAIL_PREFIXX + "t" + filename
    if not os.path.exists(thumbnail_path):
        create_thumb(path + filename, thumbnail_path)
    else:
        logging.debug("Thumb already exists " + thumbnail_path)
    return send_from_directory(path + THUMBNAIL_PREFIXX, "t" + filename)


def create_thumb(original_file, filename_thumb):
    base_width = 400
    logging.debug("Create thumbnail with " + str(base_width) + "px width")
    img = Image.open(original_file)
    width_percentage = (base_width / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(width_percentage)))
    img = img.resize((base_width, hsize), Image.ANTIALIAS)
    logging.debug("Saving file to " + filename_thumb)
    img.save(filename_thumb)
    logging.info("Thumbnail created " + filename_thumb)


def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.2f %s" % (num, x)
        num /= 1024.0


def get_and_increase_number() -> str:
    file_path = Path(expanduser("~") + "/booth/" + 'filename.txt')
    content = file_path.read_text()
    if not content:
        logging.debug("Number file " + str(file_path) + " does not exist")
        content = '0'
    number = int(content) + 1
    logging.info("New number is " + str(number))
    file_path.write_text('%d' % number)
    return str(number)


@app.route('/info')
def info():
    context = gp_context_new()
    error, camera = gp_camera_new()
    error = gp_camera_init(camera, context)
    error, text = gp_camera_get_summary(camera, context)
    error = gp_camera_exit(camera, context)
    return text.text


@app.route('/capture')
def capture():
    try:
        path = capture_photo()
    except GPhoto2Error as error:
        error_message = "GPhoto Error: " + str(error)
        logging.error(error_message)
        return error_message, 500

    exists = os.path.exists(path)
    is_file = os.path.isfile(path)
    # name = str(datetime.datetime.now()).split('.')[0]
    name = get_and_increase_number() + "-" + shortuuid.uuid()
    new_path = expanduser("~") + "/booth/" + str(name) + ".jpg"
    if exists and is_file:
        shutil.move(path, new_path)
    return name


def capture_photo():
    callback_obj = gphoto2.check_result(gphoto2.use_python_logging())
    camera = gphoto2.Camera()
    camera.init()
    logging.debug('Capturing image')
    file_path = camera.capture(gphoto2.GP_CAPTURE_IMAGE)
    logging.debug('Camera file path: ${0}/${1}'.format(file_path.folder, file_path.name))
    target = os.path.join('/tmp', file_path.name)
    logging.info('Copying image to ' + target)
    camera_file = camera.file_get(file_path.folder, file_path.name, gphoto2.GP_FILE_TYPE_NORMAL)
    camera_file.save(target)
    return target


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)
