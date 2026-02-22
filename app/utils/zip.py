import io
import zipfile


def make_zip(files: list[tuple[str, io.BytesIO]]) -> io.BytesIO:
    zip_buffer = io.BytesIO()  # make empty buffer to save the zip file
    # create a zip file in the buffer
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for filename, buffer in files:
            zip_file.writestr(filename, buffer.read())  # add the files to the zip file

    zip_buffer.seek(0)  # set the pointer to the beginning of the buffer
    return zip_buffer
