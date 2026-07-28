# PDFtk is invoked with an absolute executable path and without a shell.
import subprocess  # nosec B404
import tempfile
from io import BytesIO
from os import environ, path
from secrets import randbelow
from shutil import which
from zipfile import ZIP_DEFLATED, ZipFile

from flask import Flask, abort, render_template, request, send_file

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

ORIGINAL = "original.pdf"
START = "start.pdf"
END = "end.pdf"
OUTPUT = "output.zip"


@app.route("/")
def main():
    return render_template("index.html")


def run_pdftk(arguments, *, cwd):
    executable = which("pdftk")
    if executable is None:
        abort(400, description="PDFtk is not available.")
    try:
        # The executable and structural arguments are fixed or internally generated.
        return subprocess.run(  # nosec B603
            [executable, *arguments],
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        abort(400, description="Unable to process the PDF.")


def page_count(*, cwd):
    result = run_pdftk([ORIGINAL, "dump_data"], cwd=cwd)
    for line in result.stdout.splitlines():
        key, separator, value = line.partition(":")
        if separator and key.strip() == "NumberOfPages":
            try:
                count = int(value.strip())
            except ValueError:
                break
            if count > 0:
                return count
            break
    abort(400, description="Unable to determine the PDF page count.")


@app.route("/split/<request_hash>", methods=["POST"])
def split(request_hash):
    del request_hash
    uploaded_pdf = request.files.get("pdf")
    if uploaded_pdf is None or not uploaded_pdf.filename:
        abort(400, description="A PDF upload is required.")

    requested_page = request.args.get("page")
    if requested_page is not None:
        try:
            requested_page = int(requested_page)
        except ValueError:
            abort(400, description="The page must be an integer.")

    with tempfile.TemporaryDirectory() as tmpdir:
        uploaded_pdf.save(path.join(tmpdir, ORIGINAL))
        num_pages = page_count(cwd=tmpdir)

        if requested_page is None:
            page = randbelow(max(1, num_pages - 1)) + 1
        else:
            page = min(max(requested_page, 1), num_pages)

        if page == num_pages:
            files_to_zip = [ORIGINAL]
        else:
            run_pdftk(
                [ORIGINAL, "cat", f"1-{page}", "output", START],
                cwd=tmpdir,
            )
            run_pdftk(
                [ORIGINAL, "cat", f"{page + 1}-end", "output", END],
                cwd=tmpdir,
            )
            files_to_zip = [END, START]

        archive = BytesIO()
        with ZipFile(archive, "w", compression=ZIP_DEFLATED) as zip_file:
            for filename in files_to_zip:
                zip_file.write(path.join(tmpdir, filename), arcname=filename)

    archive.seek(0)
    return send_file(
        archive,
        mimetype="application/zip",
        as_attachment=True,
        download_name=OUTPUT,
    )


if __name__ == "__main__":
    app.run(
        host=environ.get("HOST", "127.0.0.1"),
        port=int(environ.get("PORT", "5000")),
        debug=environ.get("FLASK_DEBUG") == "1",
    )
