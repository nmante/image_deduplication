#Tests

Using `Lettuce` for BDD testing. To run the tests, run this command in the `tests` directory

	lettuce
	
You'll see some passing tests! The tests look at two things:

- Near deduplication on a set of 15 images (with 2 sets of 2 duplicate images)
- Exact deduplication on a set of 15 images (with 2 sets of 2 duplicate images)

The tests make sure the program satisfies these constraints:
	
- After deduplication there should be **13 unique** images, and **2** sets of **duplicate** images 