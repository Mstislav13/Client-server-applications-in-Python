import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["common", "log", "client", "unittest_tests"],
}
setup(
    name="my_client_proj",
    version="0.0.1",
    description="my_client_proj",
    options={
        "build_exe": build_exe_options
    },
    executables=[Executable('client.py',
                            # base='Win32GUI',
                            targetName='client.exe',
                            )]
)
