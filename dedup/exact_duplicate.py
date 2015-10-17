__author__ = "Nii Mante"
__license__ = "MIT"
__email__ = "nmante88@gmail.com"
__status__ = "Development"

"""
    This module contains methods to find exact duplicate images
"""
import sys
import hashlib


class ExactDuplicate:
    def __init__(self, filenames):
        self.filenames = filenames
        self.image_dictionary = {}

    def create_image_hash(self, filename):
        """
            Generate a hash for an image with "filename"
            Using the md5 hashing algorithm
        """

        image_bytes = open(filename).read()
        image_hash = hashlib.md5(image_bytes).hexdigest() 
        return image_hash, image_bytes

    def deduplicate_images(self):

        """
            Deduplicate images by generating a hash of the image bytes.
            Then add images to to a dictionary with this structure
            {
                image_hash : { "filename" : filename }, ...
            }
        """

        for f_name in self.filenames:
            image_hash, image_bytes = self.create_image_hash(f_name)

            # If we haven't seen this image create an entry for it 
            if self.image_dictionary.get(image_hash, 0) == 0:
                self.image_dictionary[image_hash] = [] 

            self.image_dictionary[image_hash].append({"filename" : f_name})
