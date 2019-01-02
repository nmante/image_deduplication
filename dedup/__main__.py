from __future__ import print_function
from near_duplicate import NearDuplicate
from exact_duplicate import ExactDuplicate
import argparse
import os, sys, errno
#from multiprocessing import Pool
from pathos.multiprocessing import Pool
import json
import shutil
import imghdr
from PIL import Image,ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

__author__ = "Nii Mante"
__license__ = "MIT"
__email__ = "nmante88@gmail.com"
__status__ = "Development"
""" This program takes a set of N image, finds duplicate images in the set,
    and returns a set of deduplicated images"""


def main(run_type=None):
    args, parser = None, create_parser() 

    # We are either running tests or an actual run
    if run_type == 'test_exact':
        args = parser.parse_args('-i images'.split())
    elif run_type == 'test_near':
        args = parser.parse_args('-n -i images'.split())
    else:
        parser = create_parser()
        args = parser.parse_args()
        if args.dump_dir == None and args.json_metadata == None:
            parser.print_help()
            return

    unique_images_count, duplicate_images_count = generate_output(args)
    return unique_images_count, duplicate_images_count
    
def create_parser():
    parser = argparse.ArgumentParser(description='This program takes a set of N images, finds duplicate images in the set, and returns a set of deduplicated images.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-e', '--exact_duplicates', action="store_true", default=True,
            help='Use this flag to deduplicate images via an "exact" deduplication methodology. Default behavior is to use exact duplicates.')
    group.add_argument('-n', '--near_duplicates', action="store_true", default=False,
            help='Use this flag to deduplicate images via a "near" deduplication methodology')

    group2 = parser.add_mutually_exclusive_group()

    group2.add_argument('-i', '--dump_dir', help="The input directory containing your unprocessed images")
    group2.add_argument('-l', '--json_metadata', help="A jsonlines file containing the filename and tika metadata files")

    parser.add_argument('-o', '--output_json', help="Write the locations and hashes of each deduplicated image to a JSON file. Defaults to 'image_locations.json'") 
    parser.add_argument('-d', '--output_dir', help="Output deduplicated images to directory. ")
    parser.add_argument('-s', '--show_duplicates', default=False, action="store_true", help="Use this flag to generate a directory which contains duplicates. Defaults behavior doesn't show duplicates." ) 
    parser.add_argument('-j', '--num_jobs', help="Number of worker threads to divide the deduplication. Defaults to 2. The more images the more jobs you should create", default=2, type=int)
    parser.add_argument('-k', '--bit_distance', help="Difference k between simhash fingerprints",
            default=1, type=int)
    
    return parser

def is_image(filename):
   # First do a simple check for file extensions
    extensions = [".jpg", ".png", ".svg", ".tiff", ".jpeg"]
    for ext in extensions:
        
        if filename.endswith(ext):
            # Compare the file extension
            return True
        elif imghdr.what(filename) != None:
            # If there's no extension, determine if it's an image by opening the file
            return True

    # If necessary try opening the file with an image module
    # If there's an error opening it, then it's not an image so return false
    try: 
        Image.open(filename)
        return True
    except IOError:
        return False 

    return False 

def find_all_images(dump_directory):
    """Find a list of images provided a root dump directory"""

    filenames = []
    for root, dirs, files in os.walk(dump_directory):
        for f in files:
            filename = os.path.join(root, f)
            abspath = os.path.abspath(filename)
            if is_image(abspath):
                 filenames.append(abspath)
    
    return filenames

def exact_deduplicate_images(workerId, file_array):
    """Given a list of file names, return a dictionary of "exactly" deduplicated images"""
    
    # Use our custom class "ExactDuplicate"
    # It deduplicates a list of images, and stores the deduplicated images in an image_dictionary
    ed = ExactDuplicate(file_array)
    ed.deduplicate_images()
    return ed.image_dictionary

def near_deduplicate_images(file_array, bit_distance, metadata = None):
    """Given a list of file names, return a dictionary of "nearly" deduplicated images"""
    nd = NearDuplicate(file_array, k=bit_distance, metadata_dictionary = metadata)
    nd.deduplicate_images()
    return nd.simhash_index,nd.image_dictionary 
    #return nd.image_dictionary

def partition_filenames(file_array, num_chunks=2):
    """ Given an array of file names, return "num_chunks" partitions"""
    chunk_size = len(file_array)//num_chunks

    for i in xrange(0, len(file_array), chunk_size):
        yield file_array[i:i+chunk_size]

def merge_near_duplicates(near_duplicate_objects):
    """ Iteratively merge nearly deduplicated images 

    Args:
        near_duplicate_objects: a list of tuples. 
            Each tuple is a (SimhashIndex, image_dictionary), where image_dictionary 
            is an object which contains simhash keys and image/filename values  
    Returns:
        a dictionary containing simhash keys and image/filename values 
    """

    if near_duplicate_objects == None or len(near_duplicate_objects) == 0:
        return {}

    if len(near_duplicate_objects) == 1:
        # near_duplicate_objects is a tuple (index, image_dictionary)
        return near_duplicate_objects[0][1]

    final_dict = {}
    first_nd = None
    second_nd = None
    for index, (simhash_index, image_dictionary) in enumerate(near_duplicate_objects):
        if index < len(near_duplicate_objects) - 1:
            sim_index1, img_dict1 = near_duplicate_objects[index]
            sim_index2, img_dict2 = near_duplicate_objects[index+1]

            first_nd, second_nd = NearDuplicate([]), NearDuplicate([])
            first_nd.image_dictionary, second_nd.image_dictionary  = img_dict1, img_dict2 
            first_nd.simhash_index, second_nd.simhash_index = sim_index1, sim_index2 

            final_dict.update(first_nd.merge_near_duplicate_dictionaries(second_nd))
            

    return final_dict

def merge_exact_duplicates(dictionaries):
    """ Given an array of dictionaries, merge the dictionaries into 1 final result"""
    final_dict = {}

    # Simple case for exact duplicates
    for d in dictionaries:
        duplicate_keys = set(d).union(final_dict)
        for key in duplicate_keys:
            arr = final_dict.get(key, []) + d.get(key, [])
            final_dict[key] = arr

    # If keys can have "nearness" we need a more advanced merge
        
    return final_dict

def mkdir_p(directory):
    try:
        os.makedirs(directory)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(directory):
            pass
        else: raise

def rm_dir(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory, ignore_errors=True)

def create_output_image_directory(args, final_dictionary):
    """ Given a deduplicated set of images, as well as an initial dump dir,
        output the deduplicated images to an output directory"""

    if args.output_dir == None:
        return
    #rm_dir(args.output_dir)
    print("Copying image files to output dir", file=sys.stderr)

    duplicate_dir = os.path.join( args.output_dir, '_duplicates')
    mkdir_p(args.output_dir)
    mkdir_p(duplicate_dir)
    
    for image_hash in final_dictionary:
        
        # Grab the file names from our image dictionary
        duplicate_image_array = final_dictionary[image_hash]
        src_path = duplicate_image_array[0]["filename"] 
        _, src_filename = os.path.split(src_path)
        dst_path = os.path.join(args.output_dir, src_filename) 

        # Copy image to new directory 
        shutil.copy2(src_path, dst_path) 
        
        # Copy all the duplicate images for this specific image to 
        # a subdirectory within '_duplicates'
        if len(duplicate_image_array) > 1 and args.show_duplicates:
            curr_duplicate_image_dir = os.path.join(duplicate_dir, image_hash)
            mkdir_p(curr_duplicate_image_dir)
            for index, dup_obj in enumerate(duplicate_image_array):
                src_path = dup_obj["filename"] 
                _, dst_filename = os.path.split(dup_obj["filename"]) 
                dst_path = os.path.join(curr_duplicate_image_dir, dst_filename)
                shutil.copy2(src_path, dst_path) 
           

    print("Copied unique images from:\n --- {} --- to\n --- {} ---".format(args.dump_dir, args.output_dir), file=sys.stderr)

    if args.show_duplicates:
        print("Duplicates stored in: \n --- {} ---".format(duplicate_dir), file=sys.stderr)

def process_json_line(lines):
    # load the line as json
    metadata_object = {}
    for line in lines:
        parts = line.split("\t:\t")
        file_path = parts[0].strip()
        json_string = parts[1].strip()
        meta = json.loads(json_string)
        metadata_object[file_path] = meta
    return metadata_object 

def process_json_file(json_file):
    metadata_object = {}
    filenames = []
    with open(json_file) as source_file:
        for line in source_file:
            #parts = line.split("\t:\t")
            #file_path = parts[0].strip()
            #json_string = parts[1].strip()
            #meta = json.loads(json_string)
            meta = json.loads(line)
            file_path = meta["__path__"]
            filenames.append(file_path)
            metadata_object[file_path] = meta
    return metadata_object, filenames

def json_to_metadata_chunks(args,file_chunks = []):
    # Open the json file, and split the reading of the file among worker threads
    results = [] 

    if args.json_metadata == None:
        return None
    num_proc = len(file_chunks)
    print (file_chunks, file=sys.stderr)
    pool = Pool(processes = num_proc)
    

    with open(args.json_metadata) as json_metadata_file:
        results = [pool.map(process_json_line,json_metadata_file, chunk) for index, chunk in enumerate(file_chunks)]
    #objs = [p.get() for p in results] 
    return merge_exact_duplicates(results)

def generate_output(args):
    """ Main application Driver
        
        1. Partition filenames into smaller chunks/arrays of image filenames
        2. Generate worker processes
        3. Pass the chunks to the workers
        4. Each worker deduplicates it's set of image files 
        5. Merge the results from each worker to one python dictionary
        6. OPTIONAL -- Output the deduplicated image files to a directory 
    """
    

    # Partition the list of filenames
    num_chunks = args.num_jobs 
    
    # Create a pool of worker threads
    # Each worker will deduplicate a set of images
    filenames = [] 
    metadata = None
    end_str = ""
    if args.json_metadata != None:
        metadata,filenames = process_json_file(args.json_metadata)
        end_str = "from metadata file: %s" % args.json_metadata
    else:
        # Find all image files in dump directory
        filenames = find_all_images(args.dump_dir)
        end_str = "from directory: %s" % args.dump_dir

    file_chunks = partition_filenames(filenames, num_chunks)
    print("Found {} images in directory: {}".format(len(filenames), end_str))

    """
    metadata_results = []
    file_chunk_list = list(file_chunks)
    num_proc = len(file_chunk_list)
    print >> sys.stderr, "Printing file chunks"
    print >> sys.stderr, file_chunks
    pool2 = Pool(processes = num_proc)
    with open(args.json_metadata) as json_metadata_file:
        metadata_results = [pool2.map(process_json_line,json_metadata_file, chunk) for index, chunk in enumerate(file_chunk_list)]
    #objs = [p.get() for p in results] 
    metadata =  merge_exact_duplicates(metadata_results)
    """
    
    pool = Pool(processes=num_chunks)

    # Pass the partitions to each thread
    results = []
    final_dictionary = {}
    if not args.near_duplicates:
        if args.num_jobs == 1:
            # If we're only using one worker, don't make overhead of starting a process
            result = exact_deduplicate_images(filenames)
            dictionaries = [result]
        else:
            # Get the results from each worker
            results = [pool.apply_async(exact_deduplicate_images, args=(index,chunk,)) 
                    for index, chunk in enumerate(file_chunks)]
            dictionaries = [p.get() for p in results]

        # Merge the results into one dictionary
        final_dictionary = merge_exact_duplicates(dictionaries)
    else:
        if args.num_jobs == 1:
            # If we're only using one worker, don't make overhead of starting a process
            result = near_deduplicate_images(filenames, args.bit_distance, metadata = metadata)
            near_duplicate_objects = [result]
        else:
            # Get the results from each near duplicate worker
            if metadata != None:
                results = [pool.apply_async(near_deduplicate_images, (chunk,args.bit_distance, ), dict(metadata=metadata)) for chunk in file_chunks] 
            else:
                results = [pool.apply_async(near_deduplicate_images, (chunk,args.bit_distance,))  for chunk in file_chunks] 
            # create an array of near duplicate objects
            near_duplicate_objects = [p.get() for p in results]

        # Merge the dictionaries together using the info from its corresponding indexes
        final_dictionary = merge_near_duplicates(near_duplicate_objects)

    print("Number of images prior to deduplication: {}".format(len(filenames)), file=sys.stderr)
    print("Number of images after deduplication: {}".format(len(final_dictionary)), file=sys.stderr)
    
    # Write the image locations to an output file
    
    
    if args.output_json != None:
        # TODO
        # For now, just do this with exact duplicates
        # Dumping the simhash class to JSON doesn't work because the object isn't
        # JSON serializable 
        outfile_name = args.output_json
        print("Writing to image dictionary to file: {}".format(outfile_name))
        with open(outfile_name, 'w') as outfile:
            json.dump(final_dictionary, outfile, indent=4, skipkeys=True, default=str)

    # Copy the images to an output directory
    create_output_image_directory(args, final_dictionary)

    return len(final_dictionary), len(filenames) - len(final_dictionary)

if __name__ == "__main__":
    main()
