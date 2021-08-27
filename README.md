# Data Enums

An alternative to the built-in Python `enum` implementation. Data enums allow you to:

- Associate data with enum members
- Add secondary unique keys
- Lookup enum members by secondary unique keys

## Testing, etc.

Sort imports (Requires Python >= 3.6):

	make format

Lint (Requires Python >= 3.6):

	make lint

Test:

	make test