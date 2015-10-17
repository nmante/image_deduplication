#Image Deduplication In Python

#####Nii Mante
	usage: main.py [-h] [-e | -n] [-i DUMP_DIR | -l JSON_METADATA]
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
	                        The absolute path to your dump directory
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

	
##Overview

The purpose of this program is to deduplicate images! The program gives the option of deduplicating in two styles:

- Near duplicates
- Exact duplicates                        

##Install

This program relies on some external modules. Simply install them using pip. 

	pip install tika
	pip install simhash
	pip install exifread
	pip install git+https://github.com/uqfoundation/pathos
	pip install Pillow

Those commands should install the modules globally to your system.
	

##Quick Use

To try out the program on a few images, you can use the test_images/ directory.  Just run these commands in this `deduplication` directory:

	chmod a+x test.sh
	./test.sh

This will create two output directories:

	test_output_exact_deduplicated_images/
	test_output_near_deduplicated_images/

The directories will contain a few things

- Unique images
- And a folder `_duplicates` with the duplicate images
	

##Generate Metadata For Near Deduplication

You can generate in two ways:

- Apache Tika Java Plugin
- Our Program `python main.py`

####Apache Tika Java

There's a program in the `../metadata-dumper/target` directory. This is how you run it.

	java -jar ../metadata-dumper/target/metadata-dumper-0.1-SNAPSHOT-jar-with-dependencies.jar -inputDir <AN_IMAGE_DUMP_DIRECTORY> -output <A_JSON_METADATA_FILE>

This takes a directory of images and outputs a json file for reading the metadata for each image.

Then to use this metadata file with our deduplication program, you would run commands like so:

	# -n for near duplicate, and -l for using a json file
	python main.py -n -l <A_JSON_METADATA_FILE>

####Our Program

If you don't have apache tika installed, you can use our program to generate metadata. See next section for how to use this

- It uses `PIL` imaging library to grab metadata, and falls back on `tika-py` if `PIL` fails.

##Large Image Batch Examples

The program **requires** a directory of images. You don't need to worry about the structure of the folder (i.e. subdirectories). If there are images in the directory, the program will find them.

###Using Nutch?

If you're using Apatche Nutch, generate a dump directory

	# Merge segments from crawl
	bin/nutch mergesegs <MERGED_SEG_DIR_TO_CREATE> -dir <CRAWL_SEGMENTS_DIR>
	
	# Create a dump directory from that merged segment
	bin/nutch dump -segment <PREVIOUSLY_CREATED_MERGED_SEG_DIR> -outputDir <OUTPUT_DUMP_DIR_TO_CREATE>
	
This dump directory would be what you pass to the deduplication script.

####Exact duplicate

	# Use the -s flag to also show duplicate images
	# Also split this among 8 jobs with the -j flag
	python main.py -i <PREVIOUSLY_CREATED_OUTPUT_DUMP_DIR> -d <DEDUP_IMAGE_DIR_TO_CREATE> -s -j 8
	
####Near duplicate

	# Use the -n flag to do near deduplication
	# Use the -j flag to split this among 4 jobs
	python main.py -i <PREVIOUSLY_CREATED_OUTPUT_DUMP_DIR> -d <DEDUP_IMAGE_DIR_TO_CREATE> -s -n -j 4

##Program Output

The program outputs a few things:

- **JSON** - JSON file which shows the file locations of deduplicated images, as well as the locations of the duplicates
- **Initial_Image_Count** - The number of images before the algorithm runs
- **Final_Image_Count** - The final number of images after deduplication
- **Images (OPTIONAL)** - If you choose, the program can conveniently put the deduplicated (and duplicate) images into an output folder



