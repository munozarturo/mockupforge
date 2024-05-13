from pathlib import Path
import os


def mockup(
    output_path: Path,
    mockup_path: Path,
    image_path: Path,
    foreground: list[int],
):
    # generate gimp command for mockup
    cmd = (
        "gimp -i -b "
        f"'(python-fu-mockupforge-mockup RUN-NONINTERACTIVE "
        f'"{str(output_path)}" "{str(mockup_path)}" "{str(image_path)}" '
        f"{foreground[0]} {foreground[1]} {foreground[2]} "
        ")' -b '(gimp-quit 1)'"
    )

    # Run the GIMP command using os.system()
    os.chdir(".")
    os.system(cmd)
