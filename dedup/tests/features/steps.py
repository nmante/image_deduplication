from lettuce import step
from lettuce import world

import dedup.__main__ as dp

@step('I am deduplicating a set of images using exact deduplication')
def test_exact_deduplication(step):
    world.run_type = 'test_exact'

@step('I am deduplicating a set of images using near deduplication')
def test_exact_deduplication(step):
    world.run_type = 'test_near'

@step('I input "([^"]*)" images with "([^"]*)" sets of 2 duplicate images')
def do_deduplication(step, total_images, duplicate_images):
    world.unique_images, world.duplicate_images = dp.main(run_type=world.run_type)

@step('I should see "([^"]*)" unique images and "([^"]*)" sets of 2 duplicate images')
def result(step, expected_unique_images, expected_duplicate_images):
    num_unique_images = world.unique_images
    num_duplicate_images = world.duplicate_images
    assert int(expected_unique_images) ==  num_unique_images
    assert int(expected_duplicate_images) ==  num_duplicate_images







