import os
import click
from pypdf import PdfReader, PdfWriter


def is_pdf_file(filename):
    return filename.lower().endswith('.pdf')


def get_pdf_files(directory):
    return [
        os.path.join(directory, filename)
        for filename in os.listdir(directory)
        if is_pdf_file(filename)
    ]


def create_output_filepath(input_path, postfix='_compressed'):
    full_path = os.path.abspath(input_path)
    base, ext = os.path.splitext(full_path)
    return os.path.abspath(base + postfix + ext)


def compress(input_path, output_path, quality):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # Copy metadata
    writer.add_metadata(reader.metadata)

    # Reduce image quality
    for page in writer.pages:
        for img in page.images:
            img.replace(img.image, quality=quality)

    with open(output_path, "wb") as f:
        writer.write(f)


def lossless_compression(input_path, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    for page in writer.pages:
        page.compress_content_streams()  # ⚠️ CPU intensive!

    with open(output_path, "wb") as f:
        writer.write(f)


def process_file(input_filepath, image_quality, lossless):
    output_filepath = create_output_filepath(input_filepath)

    input_file = os.path.basename(input_filepath)
    output_file = os.path.basename(output_filepath)

    # Check if the output file already exists
    if (os.path.exists(output_filepath)
            and not click.confirm(
                f"The file {output_file} already exists.\n"
                f"Do you want to overwrite it?")):
        click.echo(f"[INFO] Compression operation canceled for file {input_file}.")
        return

    if lossless:
        lossless_compression(input_filepath, output_filepath)
    else:
        compress(input_filepath, output_filepath, image_quality)

    click.echo(f"[INFO] Compressed \"{input_file}\" to \"{output_file}\"")


def process_directory(directory, image_quality, lossless):
    filepaths = get_pdf_files(directory)
    for filepath in filepaths:
        process_file(filepath, image_quality, lossless)


@click.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('-q', '--image-quality', default=50, help='Image compression quality (0-100).')
@click.option('-l', '--lossless', is_flag=True, help='Enable lossless compression for PDFs.')
def main(path, image_quality, lossless):
    """
    Compress a PDF or all PDFs in a directory.

    You can choose to compress using lossy image compression with
    the --image-quality option, or apply lossless compression using
    the --lossless flag.

    Lossy and lossless options cannot be combined.
    """

    if image_quality < 0 or image_quality > 100:
        click.echo("[ERROR] Image quality must be between 0 and 100.")
        return

    if lossless:
        click.echo("[INFO] Lossless compression enabled.")
        click.echo("[INFO] The --image-quality option if set will be ignored.")

    if os.path.isdir(path):
        process_directory(os.path.abspath(path), image_quality, lossless)
    elif os.path.isfile(path) and is_pdf_file(path):
        process_file(os.path.abspath(path), image_quality, lossless)
    else:
        click.echo("[ERROR] The provided path is not a valid PDF file or directory.")


if __name__ == "__main__":
    main()
