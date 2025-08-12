def to_pascal_case(string: str) -> str:
    """Converts a string to PascalCase."""
    words = string.split('_')
    camel_case = ''.join(word.capitalize() for word in words)
    return camel_case


def chunk_text(text: str, nchars: int = 79) -> list[str]:
    """Split text into lines with a maximum number of characters."""
    words = text.split()  # Split the text into words
    lines: list[str] = []  # This will store the final lines
    current_line: list[str] = []  # This will store words for the current line

    for word in words:
        # Check if adding the next word would exceed the length limit
        if (sum(len(w) for w in current_line) + len(word) + len(current_line)) > nchars:
            # If adding the word would exceed the limit, join current_line into a string and add to lines
            lines.append(' '.join(current_line))
            current_line = [word]  # Start a new line with the current word
        else:
            current_line.append(word)  # Add the word to the current line

    # Add the last line to lines if any words are left unadded
    if current_line:
        lines.append(' '.join(current_line))

    return lines
