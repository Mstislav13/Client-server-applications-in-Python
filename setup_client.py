from setuptools import setup, find_packages

setup(name="my_client_proj",
      version="0.0.1",
      description="my_client_proj",
      author="Mstislav Agafontsev",
      author_email="slava9mst@mail.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
