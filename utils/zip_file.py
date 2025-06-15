import zipfile
import io

def create_export_zip(code: str, filename: str, test_code: str = None, review: str = None) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr(filename, code)

        if test_code:
            test_filename = filename.replace(".py", "_test.py")
            zf.writestr(test_filename, test_code)

        if review:
            zf.writestr("review.txt", review)

    buffer.seek(0)
    return buffer.getvalue()
