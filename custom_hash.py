import sys

def custom_hash(input_message):
    # Initial hash value
    hash_value = 0xDEADBEEF

    # Process each character in the input message
    for char in input_message:
        # XOR the current hash value with the ASCII value of the character
        hash_value ^= ord(char)

        # Rotate the hash value left by a fixed number of bits
        hash_value = (hash_value << 3) | (hash_value >> (32 - 3))

    # Finalize the hash value
    hash_value &= 0xFFFFFFFF  # Ensure the hash value fits within 32 bits

    return hash_value

def calculate_file_hash(file_name):
    try:
        # Open the file and read its contents
        with open(file_name, 'r') as file:
            file_contents = file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found.")
        sys.exit(1)

    # Calculate the custom hash value of the file contents
    hash_result = custom_hash(file_contents)
    print(f"The custom hash value of '{file_name}' is: {hash_result}")

if __name__ == "__main__":
    # Check if the user provided a filename as an argument
    if len(sys.argv) != 2:
        print("Usage: python custom_hash.py <filename>")
        sys.exit(1)

    # Extract the filename from the command line argument
    file_name = sys.argv[1]

    # Calculate the custom hash value for the file
    calculate_file_hash(file_name)
