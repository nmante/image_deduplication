#Image Deduplication In Python 2.x

#####Nii Mante

##Overview

The purpose of this program is to deduplicate images! The program gives the option of deduplicating in two styles:

- Near duplicates
- Exact duplicates                        

##Install

Just clone this repository and run the setup.py install. **NOTE:** *This library was written for Python 2.*

	git clone https://github.com/nmante/image_deduplication.git
	cd image_deduplication
	# You may need to run this setup.py install with sudo
	python setup.py install
	
Once you run that script, try running this command:

	dedup

You should see a help menu on how to use the Command Line Interface!


##Quick Use

To try out the program on a few images, you can use the images/ directory.  Just run these commands in the `dedup` directory:

	chmod a+x test.sh
	./test.sh

This will create two output directories:

	test_output_exact_deduplicated_images/
	test_output_near_deduplicated_images/

The directories will contain a few things

- Unique images
- And a folder `_duplicates` with the duplicate images

##Usage

	usage: dedup [-h] [-e | -n] [-i DUMP_DIR | -l JSON_METADATA]
               [-o OUTPUT_JSON] [-d OUTPUT_DIR] [-s] [-j NUM_JOBS]
               [-k BIT_DISTANCE]

	This program takes a set of N images, finds duplicate images in the set, and
	returns a set of deduplicated images.
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -e, --exact_duplicates
	                        Use this flag to deduplicate images via an "exact"
	                        deduplication methodology. Default behavior is to use
	                        exact duplicates.
	  -n, --near_duplicates
	                        Use this flag to deduplicate images via a "near"
	                        deduplication methodology
	  -i DUMP_DIR, --dump_dir DUMP_DIR
	                        The input directory containing your unprocessed images
	  -l JSON_METADATA, --json_metadata JSON_METADATA
	                        A jsonlines file containing the filename and tika
	                        metadata files
	  -o OUTPUT_JSON, --output_json OUTPUT_JSON
	                        Write the locations and hashes of each deduplicated
	                        image to a JSON file. Defaults to
	                        'image_locations.json'
	  -d OUTPUT_DIR, --output_dir OUTPUT_DIR
	                        Output deduplicated images to directory.
	  -s, --show_duplicates
	                        Use this flag to generate a directory which contains
	                        duplicates. Defaults behavior doesn't show duplicates.
	  -j NUM_JOBS, --num_jobs NUM_JOBS
	                        Number of worker threads to divide the deduplication.
	                        Defaults to 2. The more images the more jobs you
	                        should create
	  -k BIT_DISTANCE, --bit_distance BIT_DISTANCE
	                        Difference k between simhash fingerprints

	

	
##Large Image Batch Examples

The program **requires** a directory of images. You don't need to worry about the structure of the folder (i.e. subdirectories). If there are images in the directory, the program will find them.

###(OPTIONAL) Using Nutch?

If you're using Apatche Nutch, generate a dump directory

	# Merge segments from crawl
	bin/nutch mergesegs <MERGED_SEG_DIR_TO_CREATE> -dir <CRAWL_SEGMENTS_DIR>
	
	# Create a dump directory from that merged segment
	bin/nutch dump -segment <PREVIOUSLY_CREATED_MERGED_SEG_DIR> -outputDir <OUTPUT_DUMP_DIR_TO_CREATE>
	
This dump directory would be what you pass to the deduplication script.

####Exact duplicate

	# Use the -s flag to also show duplicate images
	# Also split this among 8 jobs with the -j flag
	dedup -i <INPUT_IMAGE_DIR> -d <OUTPUT_IMAGE_DIR_TO_CREATE> -s -j 8
	
####Near duplicate

	# Use the -n flag to do near deduplication
	# Use the -j flag to split this among 4 jobs
	dedup -i <INPUT_IMAGE_DIR> -d <OUTPUT_IMAGE_DIR_TO_CREATE> -s -n -j 4

##Program Output

The program outputs a few things:

- **JSON** - JSON file which shows the file locations of deduplicated images, as well as the locations of the duplicates
- **Initial_Image_Count** - The number of images before the algorithm runs
- **Final_Image_Count** - The final number of images after deduplication
- **Images (OPTIONAL)** - If you choose, the program can conveniently put the deduplicated (and duplicate) images into an output folder



