FROM docker.io/fnndsc/mni-conda-base:civet2.1.1-python3.10.2

LABEL org.opencontainers.image.authors="FNNDSC <dev@babyMRI.org>" \
      org.opencontainers.image.title="ep-skimage-mcubes-mni" \
      org.opencontainers.image.description="A ChRIS ds plugin wrapper around scikit-image's implementation of marching-cubes"

WORKDIR /usr/local/src/ep-skimage-mcubes-mni

# Install binary Python packages using conda, but install
# nibabel using pip for ppc64le support

RUN conda install -y -c conda-forge h5py=3.6.0 scikit-image=0.19.1

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install .

CMD ["skimc", "--help"]
