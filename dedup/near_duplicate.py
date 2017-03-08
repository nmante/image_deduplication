__author__ = "Nii Mante"
__license__ = "MIT"
__email__ = "nmante88@gmail.com"
__status__ = "Development"

"""
   This module contains methods to find near duplicate images.  
"""

import sys
from PIL import Image
import os

# Simhash algorithm https://github.com/liangsun/simhash 
from simhash import Simhash, SimhashIndex

class NearDuplicate:
    def __init__(self, filenames, k=2, metadata_dictionary=None):
        self.filenames = filenames
        self.simhash_index = None 
        self.image_dictionary = {}
        self.metadata_dictionary = metadata_dictionary
        self.k = k 
        # Need to store the image hashes in some fashion
        # Possibly cluster the hashes (k-means) 
    
    def exifread_metadata(self, filename):
        """Use the exifread module to grab metadata for a file"""
        f = open(filename, 'rb')
        tags = exifread.process_file(f)
        return tags

    def generate_features(self, filename):
        """Given an image generate a feature vector"""

        # Do native image metadata grabbing via the PIL Image module
        im = None
        try:
            im = Image.open(filename)
        except IOError:
            print >> sys.stderr, "ERROR in NearDuplicate.generate_features: PIL Image open failed for image: " + filename + ". Skipping featurization"
            return []
                    
        # Grab the metadata for the image
        metadata = {} 
        
        # We'll store features to use for simhash in a tuple array [(token, weight)]
        features = []

        """ 
            FEATURES
                We'll resize the image so all images are normalized to a certain size 
                Also make sure to retain aspect ratio

                Features to use (in order of importance)
                    - center region bytes 
                    - color histogram
                    - content type
                    - image width
                    - image height

            We can take subregions of the image, and hash those
        """
        
        # Resize the image so all images are normalized
        width = im.size[0]
        height = im.size[1]
        resize_width = 30 
        resize_height = resize_width*height/width
        resize_im = None
        histogram_bytes, histogram_weight = "", 0
        center_region_bytes, center_region_weight = "", 5
        extension = ""
        try :
            resize_im = im.resize((resize_width, resize_height), Image.ANTIALIAS)
            # Crop sub regions
            height_padding, width_padding = resize_height/5, resize_width/5
            box = (width_padding, height_padding, resize_width - width_padding, 
                    resize_height - height_padding)
            sub_region = resize_im.crop(box)
            
            # Generate a histogram
            histogram_bytes, histogram_weight = str(resize_im.histogram()), 4
            center_region_bytes, center_region_weight = str(list(sub_region.getdata())), 3
        except OSError:
            # Couldn't resize the image. Let's
            print >> sys.stderr, "Couldn't resize the image. Prob an eps or svg"
            resize_im = im
            resize_width = im.size[0]
            resize_height = im.size[1]
            sub_region = im

            # Grab the bytes of the entire file
            image_bytes = open(filename).read()
            # Get the central bytes 
            #image_bytes_str = str(image_bytes)
            histogram_bytes = "NONE"
            image_bytes_str = unicode( str(image_bytes), 'utf-8', "ignore")
            byte_offset = len(image_bytes_str)//4
            center_region_bytes = image_bytes_str[byte_offset:-byte_offset] 
         
        extension = resize_im.format if resize_im.format !=  None else os.path.splitext(filename)[1]
         
        # Figure out the content type (png, jpg, etc.)
        content_type = "image/" + str(extension.lower())
        
        feature_weight_dict = {
                "Image Height" : 1, 
                "Image Width" : 1,
                "Image Histogram" : histogram_weight,
                "Content-Type" : 5,
                "Center Region Bytes" : center_region_weight 
        }

        metadata = {
                "Image Height" : str(width), 
                "Image Width" : str(height),
                "Image Histogram" : histogram_bytes,
                "Content-Type" : content_type,
                "Center Region Bytes" : center_region_bytes 
        }
       
        # Create an array of (token, weight) tuples. These are our features and weights
        # to be used for the Simhash
        for (feature_tag, weight), (meta_tag, meta_value) in zip(feature_weight_dict.items(), 
                metadata.items()):
            features.append((meta_tag + ":" + meta_value, weight))

        return features 


    def merge_near_duplicate_dictionaries(self, nd):
        """Merge the current near duplicate instance with another near duplicate instance"""

        smaller_nd = self if len(self.image_dictionary) <= len(nd.image_dictionary) else nd
        larger_nd = self if len(self.image_dictionary) > len(nd.image_dictionary) else nd
        final_dict = larger_nd.image_dictionary

        # Iterate over the smaller near duplicate instance
        for key in smaller_nd.image_dictionary.keys():
            

            # If an exact duplicate exists, just grab it and merge them 
            if larger_nd.image_dictionary.get(key, None) != None:
                arr = smaller_nd.image_dictionary.get(key, []) +\
                        larger_nd.image_dictionary.get(key, [])
                final_dict[key] = arr
                continue

            # Find the closest near duplicate in the larger dictionary by
            # using it's index
            simhash_obj = smaller_nd.image_dictionary[key][0]["hash_object"]

            near_duplicates_keys = larger_nd.simhash_index.get_near_dups(simhash_obj)
            
            # If a near duplicate exists 
            if len(near_duplicates_keys) > 0:
                # grab the array of images at that key in the larger dictionary
                # Merge it the array of images in the smaller dictionary 
                near_dup_key = near_duplicates_keys[0]
                arr = smaller_nd.image_dictionary.get(key, []) +\
                        larger_nd.image_dictionary.get(near_dup_key, [])

                # create an entry in the new dictionary
                final_dict[near_dup_key] = arr
                continue
                
            # Otherwise we should just add this key-object from the dictionary
            # to this array
            final_dict[key] = smaller_nd.image_dictionary[key] 

            # Add this simhash to the Index for efficient searching
            larger_nd.simhash_index.add(key, simhash_obj)

        self.image_dictionary = final_dict
        self.simhash_index = larger_nd.simhash_index

        nd.image_dicionary = final_dict
        nd.simhash_index = larger_nd.simhash_index

        # Now simply return this final dict 
        return final_dict


    def simhash_value_to_key(self, simhash):
        """Given a simhash object, convert it's value to a hexadecimal key 
            This key will be used in our image_file dictionary
        """
        return str(hex(simhash.value))


    def deduplicate_images(self):
        """
            Given a list of image files "self.filenames", deduplicate the images using
            near deduplication 
        """
        # Iterate through our files
        for image_file in self.filenames:
            feature_array = []
            # Use our own function for grabbing metadata
            # Create a list of features
            feature_array = self.generate_features(image_file)
        
            # Simhash this list of features
            sHash = Simhash(feature_array)
            if self.simhash_index == None:
                # First image, so we create the index add it to the dictionary
                # And move on to next iteration
                key = self.simhash_value_to_key(sHash)

                # We will use this index to speed up the process for finding
                # nearby simhashes
                self.simhash_index = SimhashIndex([(key, sHash)], k=self.k)
                self.image_dictionary[key] = [{
                    "filename" : image_file, 
                    "hash_key" : key, 
                    "hash_object": sHash
                }] 
                continue

            near_duplicates_keys = self.simhash_index.get_near_dups(sHash)

            if len(near_duplicates_keys) > 0:
                # There are duplicates, so we should add them to the corresponding entry
                # in the file dictionary

                # Get the key for the nearest duplicate image
                near_dup_simhash_key = near_duplicates_keys[0] 

                # Get the key for this current image 
                current_simhash_key = self.simhash_value_to_key(sHash) 

                # Create an object comprised of the image filename and key
                # We'll store this in a dictionary to be used in our merge step
                current_simhash_object = {
                    "filename" : image_file, 
                    "hash_key" : current_simhash_key,
                    "hash_object" : sHash
                }
                self.image_dictionary[near_dup_simhash_key].append(current_simhash_object)
            else:
                # No duplicates, so let's create an entry in our image filename dictionary
                key = self.simhash_value_to_key(sHash)

                # Add this simhash to the Index for efficient searching
                self.simhash_index.add(key, sHash)

                # Create an object in our image file dictionary
                self.image_dictionary[key] = [{
                    "filename" : image_file, 
                    "hash_key" : key,
                    "hash_object" : sHash
                }]

