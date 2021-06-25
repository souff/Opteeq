import io
import json
import os
import uuid
from typing import Iterator, Tuple

from google.cloud import vision
from google.cloud.vision_v1.types.image_annotator import AnnotateImageResponse


def request_generator(image_folder: str) -> Iterator[Tuple[str, AnnotateImageResponse]]:
    """
    Create an iterator which return a tuple image name and the request from google vision for each
    file in image_folder.

    :param image_folder: path of the image folder
    :return: iterator, tuple name of image and google vision response
    """
    client = vision.ImageAnnotatorClient()
    for file in os.listdir(image_folder):
        with io.open(os.path.join(image_folder, file), 'rb') as image_file:
            content = image_file.read()
        image = vision.Image(content=content)
        yield file, client.text_detection(image=image)


def via_json(image_folder: str = "image") -> None:
    """
    Build json for VGG Image Annotator with anotation from google cloud response.

    :param image_folder: path of the image folder
    """
    # load default/blank project save without image.
    with open("default.json", "r") as f:
        output = json.load(f)
    for counter, (file_name, response) in enumerate(request_generator(image_folder)):
        counter = str(counter + 1)
        # part for add an image
        output["project"]["vid_list"].append(counter)
        output["file"][counter] = {"fid": counter, "fname": file_name, "type": 2,
                                   "loc": 3,
                                   "src": f"file:///{os.path.abspath(os.path.join(image_folder, file_name))}"}
        output["view"][counter] = {"fid_list": [counter]}
        # part for add box (struct["xy"] start with 7 = polygon, 2 = square) and text
        for box in response.text_annotations:
            struct = {"vid": counter, "flg": 0, "z": [],
                      "xy": [7] + [i for point in box.bounding_poly.vertices for i in
                                   [point.x, point.y]], "av": {"1": box.description}}
            output["metadata"][f"{counter}_{uuid.uuid1()}"] = struct.copy()
    # dump the file to json
    with open("output.json", "w") as f:
        json.dump(output, f)


if __name__ == '__main__':
    via_json()
