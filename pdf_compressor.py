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

    if os.name == 'nt' and len(full_path) > 260 - len(postfix):
        click.echo("[ERROR] The file path is too long. Please move the file to a shorter path.")
        return

    base, ext = os.path.splitext(full_path)
    return os.path.abspath(base + postfix + ext)


def remove_duplication(input_path, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.add_metadata(reader.metadata)

    with open(output_path, "wb") as fp:
        writer.write(fp)


def reduce_image_quality(input_path, output_path, quality):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

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

    # Check if the output file already exists
    if (os.path.exists(output_filepath)
            and not click.confirm(
                f"The file {output_filepath} already exists."
                f"Do you want to overwrite it?")):
        click.echo(f"[INFO] Compression operation canceled for file {input_filepath}.")
        return

    if lossless:
        click.echo("[INFO] Lossless compression enabled.")
        click.echo("[INFO] The --image-quality option if set will be ignored.")
        lossless_compression(input_filepath, output_filepath)
    else:
        click.echo(f"[INFO] Image quality set to: {image_quality}")
        reduce_image_quality(input_filepath, output_filepath, image_quality)
        remove_duplication(output_filepath, output_filepath)

    click.echo(f"[INFO] Compressed \"{input_filepath}\" to \"{output_filepath}\"")


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

    if os.path.isdir(path):
        filepaths = get_pdf_files(path)
        for filepath in filepaths:
            process_file(filepath, image_quality, lossless)
    elif os.path.isfile(path) and is_pdf_file(path):
        process_file(os.path.abspath(path), image_quality, lossless)
    else:
        click.echo("[ERROR] The provided path is not a valid PDF file or directory.")


if __name__ == "__main__":
    main()
