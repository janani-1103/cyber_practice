from PIL import Image
import argparse


def convert_msg_to_binary_list(message):
    binary_list = []

    for char in message:
        binary_list.append(format(ord(char), '08b'))

    return binary_list


def conv_int_to_bin(value):
    return format(value, '08b')


def conv_bin_to_int(binary_string):
    return int(binary_string, 2)


def change_to_lsb(color_binary, lsb):
    binary_list = list(color_binary)

    binary_list[-1] = lsb

    return ''.join(binary_list)


def change_pixels_to_lsb(binary_message, pixel_list, continue_bit):

    binary_message_index = 0

    for pixel_index in range(len(pixel_list)):

        new_colors = []

        for color_value in pixel_list[pixel_index]:

            color_binary = conv_int_to_bin(color_value)

            # Last bit for continuation
            if binary_message_index == len(binary_message):

                new_binary = change_to_lsb(color_binary, continue_bit)

            else:

                new_binary = change_to_lsb(
                    color_binary,
                    binary_message[binary_message_index]
                )

            new_colors.append(conv_bin_to_int(new_binary))

            binary_message_index += 1

        pixel_list[pixel_index] = (
            new_colors[0],
            new_colors[1],
            new_colors[2]
        )

    return pixel_list


def perform_lsb(new_img, binary_list):

    pixels = list(new_img.get_flattened_data())

    pixel_index = 0

    GROUP_SIZE = 3

    for index in range(len(binary_list)):

        current_pixel_list = []

        for i in range(GROUP_SIZE):

            current_pixel_list.append(
                pixels[pixel_index + i]
            )

        if index == len(binary_list) - 1:

            new_pixels = change_pixels_to_lsb(
                binary_message=binary_list[index],
                pixel_list=current_pixel_list,
                continue_bit='1'
            )

        else:

            new_pixels = change_pixels_to_lsb(
                binary_message=binary_list[index],
                pixel_list=current_pixel_list,
                continue_bit='0'
            )

        pixel_index += GROUP_SIZE

        yield new_pixels


def encrypt(file_path, message, output_path):

    binary_list = convert_msg_to_binary_list(message)

    image = Image.open(file_path)

    if image.mode != 'RGB':
        image = image.convert('RGB')

    width, height = image.size

    max_chars = (width * height) // 3

    if len(message) > max_chars:
        raise ValueError("Message too large for image")

    new_img = image.copy()

    current_pixel_x = 0
    current_pixel_y = 0

    for pixel_list in perform_lsb(
        new_img=new_img,
        binary_list=binary_list
    ):

        for pixel in pixel_list:

            new_img.putpixel(
                (current_pixel_x, current_pixel_y),
                pixel
            )

            if current_pixel_x == width - 1:

                current_pixel_x = 0
                current_pixel_y += 1

            else:

                current_pixel_x += 1

    new_img.save(output_path)

    print("Message hidden successfully!")


def decrypt(file_path):

    image = Image.open(file_path)

    pixels = list(image.get_flattened_data())

    hidden_message = ""

    for i in range(0, len(pixels), 3):

        binary_data = ""

        current_pixels = pixels[i:i+3]

        for pixel in current_pixels:

            for color in pixel:

                binary_data += conv_int_to_bin(color)[-1]

        hidden_message += chr(int(binary_data[:8], 2))

        if binary_data[8] == '1':
            break

    print("Hidden Message:", hidden_message)


def main():

    parser = argparse.ArgumentParser(
        description="Encrypt or decrypt message inside image"
    )

    parser.add_argument(
        '-d',
        action='store_true',
        help="Decrypt data"
    )

    parser.add_argument(
        '-e',
        action='store_true',
        help="Encrypt data"
    )

    parser.add_argument(
        '-f',
        required=True,
        help="Image file"
    )

    parser.add_argument(
        '-m',
        required=False,
        help="Message to hide"
    )

    parser.add_argument(
        '-o',
        required=False,
        help="Output image"
    )

    args = parser.parse_args()

    if not (args.e or args.d):

        parser.error("Choose either -e or -d")

    if args.e:

        if not args.m or not args.o:

            parser.error(
                "Encryption requires -m and -o"
            )

        encrypt(args.f, args.m, args.o)

    elif args.d:

        decrypt(args.f)


if __name__ == "__main__":
    main()