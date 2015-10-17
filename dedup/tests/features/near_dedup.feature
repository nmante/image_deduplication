Feature: Near image deduplication 

	Background:
		Given I am deduplicating a set of images using near deduplication
			
	
	Scenario: Deduplicate a set of 15 test images
		Given I input "15" images with "2" sets of 2 duplicate images 
		Then I should see "13" unique images and "2" sets of 2 duplicate images 

