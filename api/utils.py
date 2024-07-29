from django.core.files.uploadedfile import SimpleUploadedFile


def format_error(errors):
    main_error = None

    for field, messages in errors.items():
        print("Messages: ", messages)
        if messages:
            main_error = messages[0]
            break
    return main_error


def generate_image():
    image = SimpleUploadedFile(
        name="test_image.jpg",
        content=open("media/profile_pics/269376.jpg", "rb").read(),
        content_type="image/jpeg",
    )
    return image


def generate_file():
    dummy_file = SimpleUploadedFile(
        name="test_file.txt",
        content=b"This is a dummy file for testing.",
        content_type="text/plain",
    )
    return dummy_file
