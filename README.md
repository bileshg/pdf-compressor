# PDF Compressor

A Python-based command-line utility that compresses PDF files by reducing image quality or applying lossless compression. The tool can process single PDF files or all PDFs within a specified directory.

## Features

- **Lossless Compression**: Removes unnecessary duplications and compresses content streams for minimal file size while maintaining the original quality of images and text.
- **Lossy Compression**: Reduces the image quality within the PDF to save space. You can control the compression quality via the `--image-quality` option.
- **Batch Processing**: Compress all PDF files within a given directory.
- **Cross-Platform Compatibility**: Works on both Windows and UNIX-based systems, with built-in handling for Windows-specific path length limitations.

## Requirements

The following Python libraries are required for this project:

- [click](https://pypi.org/project/click/) - A package for creating command-line interfaces.
- [pypdf](https://pypi.org/project/pypdf/) - A library for reading, manipulating, and writing PDFs.

To install these dependencies, run:
```bash
pip install click pypdf
```

## Usage

### Command-line Options

```bash
python pdf-compressor.py [OPTIONS] PATH
```

**Arguments:**
- `PATH`: The path to the PDF file or directory containing PDFs to compress.

**Options:**
- `-q`, `--image-quality`: (Optional) Set the image compression quality (0-100). Default is `50`. This option is ignored when using lossless compression.
- `-l`, `--lossless`: (Optional) Enable lossless compression. If this is set, the image quality option is ignored.

### Examples

#### Compress a Single PDF with Lossy Compression

```bash
python pdf-compressor.py example.pdf -q 70
```
This will compress `example.pdf` by reducing the image quality to 70%.

#### Compress All PDFs in a Directory with Lossless Compression

```bash
python pdf-compressor.py /path/to/directory --lossless
```
This will apply lossless compression to all PDF files in the specified directory.

### Handling Existing Compressed Files

If the compressed output file already exists, the program will prompt you to confirm whether to overwrite the file or cancel the operation for that file.

## Implementation Overview

1. **File Handling**: The script checks whether the provided `PATH` is a file or directory and processes accordingly.
2. **Compression Methods**:
   - **Lossless**: Optimizes the PDF structure and content streams without affecting image quality.
   - **Lossy**: Compresses images based on the quality specified.
3. **Windows Path Length Handling**: Checks for potential issues with file path length on Windows systems and provides an error message if the path exceeds allowed limits.
