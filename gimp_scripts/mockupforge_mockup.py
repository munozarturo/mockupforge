from gimpfu import *
import random


def get_all_layers(image):
    def recursive_get_layers(layer_or_group, layers):
        if isinstance(layer_or_group, gimp.GroupLayer):
            for child in layer_or_group.children:
                recursive_get_layers(child, layers)
        else:
            layers.append(layer_or_group)

    all_layers = []
    for layer in image.layers:
        recursive_get_layers(layer, all_layers)
    return all_layers


def mockupforge_mockup(
    output_path,
    mockup_path,
    image_path,
    fg_red,
    fg_green,
    fg_blue,
):
    # Open the mockup image
    mockup_image = pdb.gimp_file_load(mockup_path, mockup_path)

    # Replace the image in the desired layer
    layers = get_all_layers(mockup_image)
    for layer in layers:
        if layer.name.startswith("mf_img:"):
            # Get the dimensions of the layer
            width = layer.width
            height = layer.height

            # Open the new image
            new_image = pdb.gimp_file_load(image_path, image_path)

            # Get the new layer from the opened image
            new_layer = new_image.layers[0]

            # Scale the new layer to match the size of the target layer
            pdb.gimp_layer_scale(new_layer, width, height, False)

            # Create a new layer in the mockup image with the same name as the target layer
            new_layer_copy = pdb.gimp_layer_new_from_drawable(new_layer, mockup_image)
            new_layer_copy.name = layer.name

            # Get the parent group of the target layer
            parent_group = pdb.gimp_item_get_parent(layer)

            # Get the position of the target layer within its parent group or image
            if parent_group is not None:
                position = pdb.gimp_image_get_item_position(mockup_image, layer)
            else:
                position = pdb.gimp_image_get_item_position(mockup_image, layer)

            # Calculate the coordinates to center the layer
            image_width = mockup_image.width
            image_height = mockup_image.height
            x = (image_width - width) // 2
            y = (image_height - height) // 2

            # Set the layer position to center it
            new_layer_copy.set_offsets(x, y)

            # Insert the new layer into the parent group (if it exists) or the image
            pdb.gimp_image_insert_layer(
                mockup_image, new_layer_copy, parent_group, position
            )

            # Remove the target layer from the mockup image
            mockup_image.remove_layer(layer)

            # Close the new image without saving
            pdb.gimp_image_delete(new_image)

            break  # Exit the loop since we found and replaced the desired layer

    layers = get_all_layers(mockup_image)
    for layer in layers:
        if layer.name.startswith("mf_fg:"):
            # Create a new RGB color
            color = gimpcolor.RGB(fg_red / 255.0, fg_green / 255.0, fg_blue / 255.0)

            # Push the current context
            pdb.gimp_context_push()

            # Set the foreground color
            pdb.gimp_context_set_foreground(color)

            # Fill the layer with the foreground color
            pdb.gimp_drawable_fill(layer, FOREGROUND_FILL)

            # Pop the context
            pdb.gimp_context_pop()
            # Do not exit loop since there are multiple foreground layers

    # Merge the visible layers
    merged_layer = pdb.gimp_image_merge_visible_layers(mockup_image, CLIP_TO_IMAGE)

    # Save the modified mockup image as PNG
    pdb.gimp_file_save(mockup_image, merged_layer, output_path, output_path)

    # Close the mockup image without saving
    pdb.gimp_image_delete(mockup_image)


register(
    "mockupforge_mockup",
    "Mockup",
    "Generates a Mockup",
    "Mockup Forge",
    "Mockup Forge",
    "2024",
    "",
    "",
    [
        (PF_STRING, "output_path", "Output Path", ""),
        (PF_STRING, "mockup_path", "Mockup Path", ""),
        (PF_STRING, "image_path", "Image Path", ""),
        (PF_INT, "fg_red", "Foreground Red", 255),
        (PF_INT, "fg_green", "Foreground Green", 255),
        (PF_INT, "fg_blue", "Foreground Blue", 255),
    ],
    [],
    mockupforge_mockup,
)

main()
