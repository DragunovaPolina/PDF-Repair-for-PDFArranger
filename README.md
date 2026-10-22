# PDF-Repair-for-PDFArranger
**PDF Repair** is a Linux utility that improves compatibility between OCR-scanned PDF documents and [PDF Arranger](https://github.com/pdfarranger/pdfarranger).

Some scanned PDFs contain problematic invisible OCR text layers or corrupted PDF structures that may cause PDF Arranger to crash. PDF Repair processes these files, removes problematic content where possible, saves a repaired copy, and automatically opens it in PDF Arranger.

## Features

- **OCR compatibility:** Removes problematic invisible OCR text layers from scanned PDFs.
- **PDF repair:** Rewrites PDF files to help resolve structural issues.
- **Automatic saving:** Creates a repaired copy without overwriting the original file.
- **PDF Arranger integration:** Automatically opens the repaired document in PDF Arranger.
- **Simple interface:** Select a PDF using the file chooser or drag and drop it into the application window.

## Requirements

- Linux operating system.
- PDF Arranger.
- Ghostscript.
- GTK 3 and Python GObject (PyGObject).

The RPM package manager should resolve the dependencies automatically if they are declared in the package metadata.

## Installation

1. Open the **Releases** section or the repository's file list.
2. Download the provided `.rpm` package.
3. Open a terminal in the directory containing the downloaded file.
4. Install the package using your distribution's package manager.

For example, on systems using DNF:

```bash
sudo dnf install ./pdf-repair-gui-1.0.0-2-rosa2021.1.noarch.rpm
```

If your system uses a different package manager, use the appropriate command for installing a local RPM package.

## Usage

1. Launch **PDF Repair** from your application menu.
2. Select a PDF file using the file chooser, or drag and drop the file into the application window.
3. Wait for processing to finish.
4. The repaired document will be saved in the same directory as the original file.
5. PDF Repair will automatically open the repaired document in PDF Arranger.

### Output files

The repaired file is saved with the suffix `_исправленный.pdf`.

For example:

```text
document.pdf
document_исправленный.pdf
```

If a file with that name already exists, a numbered suffix is added to avoid overwriting it.

The original PDF is preserved.

## How It Works

PDF Repair uses Ghostscript to rewrite PDF documents. This process can remove problematic OCR text-layer content and repair certain PDF structural issues that may interfere with PDF Arranger.

**Note:** The utility cannot guarantee recovery of every damaged PDF. Some files may be too severely corrupted to repair, and rewriting a PDF may affect its text layer, metadata, or other document properties.

## Troubleshooting

- **Ghostscript not found:** Install Ghostscript using your distribution's package manager.
- **PDF Arranger does not open:** Make sure PDF Arranger is installed and the `pdfarranger` command is available.
- **The PDF cannot be repaired:** Try opening the original file in another PDF viewer to check whether it is severely damaged.

## License

This project was created for personal work-related purposes. You are free to use this utility.
