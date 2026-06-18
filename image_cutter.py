import cv2
import numpy as np
from config import WINDOW_HEIGHT, WINDOW_WIDTH


def crop_resize_and_compress(image_bytes: bytes, scale: float, left: float, top: float, quality: int = 90):
    np_arr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Failed to load image")
    img_width, img_height = image.shape[1], image.shape[0]
    max_left = img_width / scale / WINDOW_WIDTH - 1
    max_top = img_height / scale / WINDOW_HEIGHT - 1
    if left > max_left:
        left = max_left
    if top > max_top:
        top = max_top
    x = int(left * scale * WINDOW_WIDTH)
    y = int(top * scale * WINDOW_HEIGHT)
    x_overflow = 0
    y_overflow = 0
    if x < 0:
        x_overflow = int(-x / scale)
    if y < 0:
        y_overflow = int(-y / scale)
    width = int(scale * WINDOW_WIDTH)
    height = int(scale * WINDOW_HEIGHT)
    image = image[y if y >= 0 else 0:y + height, x if x >= 0 else 0:x + width]
    image = cv2.resize(image, (WINDOW_WIDTH-x_overflow, WINDOW_HEIGHT-y_overflow), interpolation=cv2.INTER_AREA)
    _, buffer = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return buffer.tobytes()


def get_image_size(image_bytes: bytes):
    np_arr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Failed to load image")
    img_width, img_height = image.shape[1], image.shape[0]
    return img_width, img_height


def resize_to_max_size_and_compress(image_bytes: bytes, max_length: int, quality: int):
    np_arr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Failed to load image")
    img_width, img_height = image.shape[1], image.shape[0]
    if img_width > max_length or img_height > max_length:
        if img_width > img_height:
            resized_width = max_length
            resized_height = int(img_height * max_length / img_width)
        else:
            resized_height = max_length
            resized_width = int(img_width * max_length / img_height)
        image = cv2.resize(image, (resized_width, resized_height), interpolation=cv2.INTER_AREA)
    _, buffer = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return buffer.tobytes()


if __name__ == '__main__':
    pass
