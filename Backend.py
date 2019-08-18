import logging
import os
import shutil
from os.path import expanduser

import gphoto2
import shortuuid
from flask import Flask, send_from_directory
from gphoto2 import gp_camera_exit, gp_context_new, gp_camera_init, \
    gp_camera_new, gp_camera_get_summary, GPhoto2Error

app = Flask(__name__)

logging.root.setLevel(logging.NOTSET)


@app.route('/pizza')
def send_pizza():
    return send_from_directory(expanduser("~") + "/booth/", '2019-08-18 16:52:29.jpg')


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
    name = shortuuid.uuid()
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
    logging.debug('Camera file path: {0}/{1}'.format(file_path.folder, file_path.name))
    target = os.path.join('/tmp', file_path.name)
    logging.info('Copying image to', target)
    camera_file = camera.file_get(file_path.folder, file_path.name, gphoto2.GP_FILE_TYPE_NORMAL)
    camera_file.save(target)
    return target


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)
