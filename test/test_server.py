from io import BytesIO
from pathlib import Path
from subprocess import CompletedProcess
from unittest import TestCase
from unittest.mock import patch
from zipfile import ZipFile

import server


class ServerTestCase(TestCase):
    def setUp(self):
        server.app.config["TESTING"] = True
        self.client = server.app.test_client()

    @staticmethod
    def pdf_upload(contents=b"%PDF-1.4\n"):
        return {"pdf": (BytesIO(contents), "document.pdf")}

    def test_home_page_renders(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)

    def test_split_requires_a_pdf(self):
        response = self.client.post("/split/request")

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"A PDF upload is required.", response.data)

    def test_split_rejects_a_non_integer_page_before_running_pdftk(self):
        with patch("server.run_pdftk") as run_pdftk:
            response = self.client.post(
                "/split/request?page=first",
                data=self.pdf_upload(),
                content_type="multipart/form-data",
            )

        self.assertEqual(response.status_code, 400)
        run_pdftk.assert_not_called()

    def test_split_returns_both_semantic_page_ranges(self):
        commands = []

        def run_command(command, *, cwd, **options):
            commands.append(command)
            self.assertTrue(Path(cwd, server.ORIGINAL).is_file())
            self.assertEqual(
                options,
                {
                    "check": True,
                    "capture_output": True,
                    "text": True,
                },
            )
            if command[-1] == "dump_data":
                return CompletedProcess(
                    command,
                    returncode=0,
                    stdout="InfoBegin\nNumberOfPages: 3\n",
                    stderr="",
                )
            Path(cwd, command[-1]).write_bytes(command[3].encode())
            return CompletedProcess(command, returncode=0, stdout="", stderr="")

        with (
            patch("server.which", return_value="/usr/bin/pdftk"),
            patch("server.subprocess.run", side_effect=run_command),
        ):
            response = self.client.post(
                "/split/request?page=1",
                data=self.pdf_upload(),
                content_type="multipart/form-data",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/zip")
        self.assertEqual(
            commands,
            [
                ["/usr/bin/pdftk", "original.pdf", "dump_data"],
                [
                    "/usr/bin/pdftk",
                    "original.pdf",
                    "cat",
                    "1-1",
                    "output",
                    "start.pdf",
                ],
                [
                    "/usr/bin/pdftk",
                    "original.pdf",
                    "cat",
                    "2-end",
                    "output",
                    "end.pdf",
                ],
            ],
        )
        with ZipFile(BytesIO(response.data)) as archive:
            self.assertEqual(archive.namelist(), ["end.pdf", "start.pdf"])
            self.assertEqual(archive.read("end.pdf"), b"2-end")
            self.assertEqual(archive.read("start.pdf"), b"1-1")

    def test_split_returns_the_original_when_the_split_is_at_the_end(self):
        contents = b"%PDF-1.4\nsingle page"

        with (
            patch("server.which", return_value="/usr/bin/pdftk"),
            patch(
                "server.subprocess.run",
                return_value=CompletedProcess(
                    args=[],
                    returncode=0,
                    stdout="NumberOfPages: 1\n",
                    stderr="",
                ),
            ) as run_command,
        ):
            response = self.client.post(
                "/split/request?page=1",
                data=self.pdf_upload(contents),
                content_type="multipart/form-data",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(run_command.call_count, 1)
        with ZipFile(BytesIO(response.data)) as archive:
            self.assertEqual(archive.namelist(), ["original.pdf"])
            self.assertEqual(archive.read("original.pdf"), contents)

    def test_split_reports_when_pdftk_is_unavailable(self):
        with patch("server.which", return_value=None):
            response = self.client.post(
                "/split/request?page=1",
                data=self.pdf_upload(),
                content_type="multipart/form-data",
            )

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"PDFtk is not available.", response.data)

    def test_split_rejects_malformed_pdftk_page_metadata(self):
        with (
            patch("server.which", return_value="/usr/bin/pdftk"),
            patch(
                "server.subprocess.run",
                return_value=CompletedProcess(
                    args=[],
                    returncode=0,
                    stdout="NumberOfPages: many\n",
                    stderr="",
                ),
            ),
        ):
            response = self.client.post(
                "/split/request?page=1",
                data=self.pdf_upload(),
                content_type="multipart/form-data",
            )

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Unable to determine the PDF page count.", response.data)
