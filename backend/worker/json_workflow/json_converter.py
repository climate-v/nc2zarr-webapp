import os
import os.path

import fsspec
import netCDF4
import ujson
from kerchunk.combine import MultiZarrToZarr
from kerchunk.hdf import SingleHdf5ToZarr

from worker.json_workflow.json_workflow_error import JsonWorkflowError

fs = fsspec.filesystem('file')


def gen_json(relative_input_path, relative_output_path, file_name):
    relative_input_path = build_input_path(relative_input_path)
    relative_output_path = build_output_path(relative_output_path)

    try:
        with fsspec.open(relative_input_path, 'rb') as f:
            h5chunks = SingleHdf5ToZarr(f, relative_input_path, inline_threshold=300)

            out_path = os.path.join(relative_output_path, file_name + ".json")
            with open(out_path, 'wb') as outf:
                outf.write(ujson.dumps(h5chunks.translate()).encode())
    except OSError as _:
        f = netCDF4.Dataset(relative_input_path)
        raise JsonWorkflowError(str(f))


def combine_json(relative_input_paths, relative_output_path, file_name):
    # The input files are in the output folder for the combine process.
    # Therefore, we want to build input paths like '../output/foo.json'.
    input_paths = list(map(build_output_path, relative_input_paths))

    multi_zarr_to_zarr = MultiZarrToZarr(
        input_paths,
        remote_protocol='file',
        concat_dims=['t']
    )

    if not file_name.endswith('.json'):
        file_name = file_name + '.json'

    output_path = os.path.join(build_output_path(relative_output_path), file_name)
    multi_zarr_to_zarr.translate(output_path)


def clean_up_after_combine(relative_input_path):
    # The input files are in the output folder for the combine process.
    # Therefore, we want to build input paths like '../output/foo.json'.
    input_path = build_output_path(relative_input_path)
    os.remove(input_path)


def build_input_path(path: str) -> str:
    return build_absolute_path(os.environ['NC2ZARR_INPUT'], path)


def build_output_path(path: str) -> str:
    return build_absolute_path(os.environ['NC2ZARR_OUTPUT'], path)


def build_absolute_path(prefix: str, suffix: str) -> str:
    return os.path.join(prefix, suffix).replace("\\", "/")
