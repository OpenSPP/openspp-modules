import random
import string


def _generate_unique_id():
    # Adjust the desired length of the unique identifier
    length = 8
    # Define the characters allowed in the unique identifier
    characters = string.digits + string.ascii_uppercase
    # Exclude characters that can be confused
    excluded_characters = ["0", "O", "1", "I"]
    # Filter the characters to exclude
    allowed_characters = [c for c in characters if c not in excluded_characters]
    # Generate the unique identifier by randomly selecting characters
    unique_id = "".join(random.choice(allowed_characters) for _ in range(length))

    return unique_id
