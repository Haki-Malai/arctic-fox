import cv2
import numpy as np
import tempfile
import random
from colorthief import ColorThief

from typing import Union

class MediaProcessor:
    def __init__(self, file_content: bytes) -> None:
        """Initialize MediaProcessor.

        :param file_content: File content
        """
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.write(file_content)
        self.temp_file.close()

        self.frame_count = None
        self.fps = None
        self.is_video = False

        self._initialize_media_properties()

    def _initialize_media_properties(self) -> None:
        """Initialize media properties."""
        cap = cv2.VideoCapture(self.temp_file.name)
        self.frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()

        self.is_video = self.frame_count > 1
        self.random_frame = self._get_random_frame()

    def _get_random_frame(self) -> Union[np.array, int]:
        """Get a random frame from the media file.

        :return: Random frame
        """
        if self.is_video:
            cap = cv2.VideoCapture(self.temp_file.name)
            random_frame_index = random.randint(0, self.frame_count - 1)
            cap.set(cv2.CAP_PROP_POS_FRAMES, random_frame_index)
            ret, frame = cap.read()
            cap.release()
            return frame
        else:
            return cv2.imread(self.temp_file.name)

    def _resize_frame(self, frame:np.array, size:tuple) -> np.array:
        """Resize frame.

        :param frame: Frame to resize
        :param size: New size
        :return: Resized frame
        """
        return cv2.resize(frame, size, interpolation=cv2.INTER_AREA)

    def get_dominant_color(self) -> str:
        """Extract dominant color using ColorThief library.
        
        :return: Dominant color in hex format
        """
        color_thief = ColorThief(self.temp_file.name)
        dominant_color = color_thief.get_color(quality=1)
        
        return "#{:02x}{:02x}{:02x}".format(*dominant_color)

    def get_fps(self) -> float:
        """Extract video FPS.

        :return: FPS ex. 29.97
        """
        cap = cv2.VideoCapture(self.temp_file.name)
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        return fps

    def _encode_image_to_binary(self, image:np.array) -> bytes:
        """Encode image to binary.

        :param image: Image to encode
        :return: Encoded image
        """
        retval, buffer = cv2.imencode('.jpg', image)
        return buffer.tobytes()

    def get_large_thumbnail(self) -> bytes:
        """Get large thumbnail.

        :return: Large thumbnail in binary format
        """
        large_thumb = self._resize_frame(self.random_frame, (320, 240))
        return self._encode_image_to_binary(large_thumb)

    def get_small_thumbnail(self) -> bytes:
        """Get small thumbnail.

        :return: Small thumbnail in binary format
        """
        aspect_ratio = self.random_frame.shape[1] / self.random_frame.shape[0]
        thumb_size = (100, int(100 / aspect_ratio)) if aspect_ratio > 1 else (int(100 * aspect_ratio), 100)
        small_thumb = self._resize_frame(self.random_frame, thumb_size)
        return self._encode_image_to_binary(small_thumb)
