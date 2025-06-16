import zipfile, io, pathlib

def create_export_zip(code: str,
                      filename: str,
                      test_code: str | None = None,
                      review: str | None = None,
                      improved_code: str | None = None,
                      language: str = "python") -> bytes:
    """
    Build an in‑memory ZIP with:
      • main code      (filename)
      • improved code  (improved_code.<ext>)   ← NEW
      • tests          (<filename>_test.py)
      • review.txt     (final review)
    """
    ext = ".py" if language.lower() == "python" else pathlib.Path(filename).suffix
    # print("filename = " + filename) //debugging
    # print("ext = " + ext) //debugging
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr(filename, code)

        if improved_code:
            zf.writestr(f"improved_code{ext}", improved_code)

        if test_code:
            zf.writestr(filename.replace(ext, f"_test{ext}"), test_code)

        if review:
            zf.writestr("review.txt", review)

    buffer.seek(0)
    return buffer.getvalue()
