import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["common", "log", "server", "unittest_tests"],
}
setup(
    name="my_server_proj",
    version="0.0.1",
    description="my_server_proj",
    options={
        "build_exe": build_exe_options
    },
    executables=[Executable('server.py',
                            # base='Win32GUI',
                            targetName='server.exe',
                            )]
)
