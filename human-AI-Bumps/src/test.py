def modify_list_after_index(x, index, new_value):
    # Make a copy of the list to avoid modifying the original list directly
    modified_list = x.copy()

    # Get the original value at the specified index
    original_value = x[index]

    # Replace the value at the specified index with the new value
    modified_list[index] = new_value

    # Adjust the list to maintain the balance by looking at elements after the specified index
    for i in range(index + 1, len(modified_list)):
        if modified_list[i] == new_value:
            modified_list[i] = original_value
            break

    return modified_list

# Example usage
x = ['a', 'b', 'c', 'd', 'a', 'b', 'c', 'd']
index_to_replace = 2
new_value = 'a'

modified_list = modify_list_after_index(x, index_to_replace, new_value)
print(f"Original list: {x}")
print(f"Modified list: {modified_list}")
