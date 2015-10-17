#!/bin/sh

main_file=__main__.py
exact_out_dir=test_output_exact_deduplicated_images
near_out_dir=test_output_near_deduplicated_images
large_out_dir=test_output_large_near_deduplicated

exact_out_json=exact_output.json
near_out_json=near_output.json
large_near_out_json=large_output.json

near_in_json_metadata=near_in_metadata.jsonl
large_in_json_metadata=armslist-images.jsonl

img_dir=images

rm -f $exact_out_json
rm -f $near_out_json
rm -f $large_near_out_json
rm -rf $exact_out_dir
rm -rf $near_out_dir
rm -rf $large_out_dir

echo "EXACT DEDUPLICATION TEST"
echo "================================"
echo "Running exact deduplication algorithm on images in folder test_images"
python $main_file -i $img_dir -d $exact_out_dir -s -o $exact_out_json
echo "================================"

echo "NEAR DEDUPLICATION TEST"
echo "================================"
echo "Running near deduplication algorithm on images in folder test_images"
python $main_file -i $img_dir -n -d $near_out_dir -s -o $near_out_json 
echo "================================"

echo ""
echo ""

#echo "================================"
#echo "JSONLINES NEAR DEDUPLICATION TEST LARGE IMAGE METADATA FILE"

#echo ""
#echo "---------"
#echo "Running near deduplication algorithm on using image metadata file"
#echo "Image metadata contains content-type, image-width, image-height, file-size, etc."
#echo "We attempt to open the image file. If an image file path is provided from another filesystem"
#echo "We ignore the error and keep processing"
#echo "---------"
#echo ""

#python main.py -n -j 8 -l $large_in_json_metadata  
#echo "================================"

