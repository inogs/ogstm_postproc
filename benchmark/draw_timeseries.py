import argparse
from pathlib import Path
from bitsea.utilities.argparse_types import existing_file_path, \
    path_inside_an_existing_dir


DEFAULT_MESHMASK = Path(
    '/pico/home/usera07ogs/a07ogs00/OPA/V2C/etc/static-data/MED1672_cut/MASK/meshmask.nc'
)


def read_command_line_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--maskfile', '-m',
        type=existing_file_path,
        default=DEFAULT_MESHMASK,
        required=False,
        help="Path of the maskfile"
    )

    parser.add_argument(
        '--settings_file', '-f',
        type=existing_file_path,
        default=Path("profiles_plotter_user_settings.txt"),
        required=False,
        help="Path of the setting file"
    )

    parser.add_argument(
        '--outdir', '-o',
        type=path_inside_an_existing_dir,
        default=None,
        required=True,
        help="Path where the output will be saved"
    )

    return parser.parse_args()


args = read_command_line_arguments()


from dataclasses import dataclass
from os import PathLike, environ
import re
from typing import Union, Tuple
from bitsea.validation.multirun.plot_profiles import Config, DataDirSource, \
    DepthProfilesOptions, PlotConfig, TimeSeriesOptions, draw_profile_plots, \
    OutputOptions
from bitsea.validation.multirun.plot_profiles.plot_inputs.single_line_plot import \
    SingleLineInputData
from bitsea.validation.multirun.plot_profiles.tools.depth_profile_algorithms import \
    DepthProfileMode, DepthProfileAlgorithm

from bitsea.basins.V2 import P


COAST_INDEX = 1
INDICATOR_INDEX = 0  # Read the average


@dataclass
class FileLine:
    label: str
    color: str
    data_path: Path


FILE_LINES = Tuple[FileLine, ...]


def parse_file_path(raw_file_path: str) -> Path:
    if raw_file_path.strip().lower() == 'actual':
        if 'STATPROFILESDIR' not in environ:
            raise Exception(
                'STATPROFILESDIR environment variable not set but "actual" is '
                'used in the setting file'
            )
        return Path(environ['STATPROFILESDIR']).resolve()
    return Path(raw_file_path).resolve()


def read_setting_file(setting_file_path: Union[str, PathLike]) -> FILE_LINES:
    with open(setting_file_path, "r") as f:
        file_lines = f.readlines()

    plots = []
    for i, raw_line in enumerate(file_lines, 1):
        clean_line = raw_line.strip()

        # Remove the comments from the lines
        if '#' in clean_line:
            hash_index = clean_line.index('#')
            clean_line = clean_line[:hash_index].strip()

        # Divide the line where there is a sequence of 1 or more
        # white chars. If the line is empty, discard the line
        clean_line_split = re.split(r'(\s+)', clean_line)
        if len(clean_line) == 0:
            continue
        if len(clean_line_split) < 5:
            raise ValueError(
                'Not enough fields found in line {}: {}'.format(
                    i,
                    clean_line
                )
            )
        label = clean_line_split[0]
        label_after_space = clean_line_split[1]
        color = clean_line_split[2]
        color_after_space = clean_line_split[3]
        first_part_line = label + label_after_space + color + color_after_space
        data_path = parse_file_path(clean_line[len(first_part_line):])

        line_content = FileLine(label, color, data_path)
        plots.append(line_content)
    return tuple(plots)


def find_all_dataset_variables(dataset_path: Union[str, PathLike]):
    dataset_path = Path(dataset_path)
    if not dataset_path.exists():
        raise IOError('Path {} does not exist'.format(dataset_path))
    if not dataset_path.is_dir():
        raise IOError('Path {} is not a directory'.format(dataset_path))

    variables = []
    for f in dataset_path.glob('*.pkl'):
        variable = f.stem
        variables.append(variable)

    return tuple(sorted(variables))


def main():
    output_dir = args.outdir
    output_dir.mkdir(exist_ok=True)

    plots = []
    file_data = read_setting_file(args.settings_file)
    for line in file_data:
        variables = find_all_dataset_variables(line.data_path)
        if len(variables) == 0:
            raise ValueError(
                'No variables (no pkl files) found inside dir {}'.format(
                    line.data_path
                )
            )

        plot_source = DataDirSource(line.data_path, args.maskfile)
        builder = SingleLineInputData.builder(COAST_INDEX, INDICATOR_INDEX)
        current_plot_config = PlotConfig(
            line.label,
            plot_source,
            variables,
            draw_time_series=True,
            plot_builder=builder,
            color=line.color,
            legend=line.label
        )
        plots.append(current_plot_config)
    plots = tuple(plots)

    timeseries_options = TimeSeriesOptions(
        levels=(0, 50, 100, 150),
        x_ticks_rotation=25,
        show_grid=True
    )

    depth_profiles_mode = DepthProfileMode(
        DepthProfileAlgorithm.SEASONAL,
        {'mode': 'square'}
    )
    depth_profiles_options = DepthProfilesOptions(
        mode=depth_profiles_mode,
        depth_ticks=(0, 50, 100, 150, 200, 400, 600, 800, 1_000),
        x_ticks_rotation=None,
        show_legend="no",
        show_y_ticks='right',
        y_ticks_position='right'
    )

    config = Config(
        plots,
        time_series_options=timeseries_options,
        depth_profiles_options=depth_profiles_options,
        output_options=OutputOptions(show_legend=True)
    )

    draw_profile_plots(config, P, output_dir)


if __name__ == "__main__":
    main()
