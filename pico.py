#! /usr/bin/env python

from functools import lru_cache
import itertools
import os
import re
import sys


import numpy as np
import pandas as pd
from pandashells.lib.lomb_scargle_lib import lomb_scargle


class PrintCatcher(object):  # pragma: no cover  This is a testing utility that doesn't need to be covered
    def __init__(self, stream='stdout'):
        self.text = ''
        if stream not in {'stdout', 'stderr'}:  # pragma: no cover  this is just a testing utitlity
            raise ValueError('stream must be either "stdout" or "stderr"')
        self.stream = stream

    def write(self, text):
        self.text += text

    def flush(self):
        pass

    def __enter__(self):
        if self.stream == 'stdout':
            sys.stdout = self
        else:
            sys.stderr = self
        return self

    def __exit__(self, *args):
        if self.stream == 'stdout':
            sys.stdout = sys.__stdout__
        else:
            sys.stderr = sys.__stderr__


# continuum stuff has annoying deprication warnings so blank them with stderr catcher
with PrintCatcher('stderr'):
    import datashader as ds
    import holoviews as hv
    from holoviews.operation.datashader import datashade
    hv.extension('bokeh')


class Pico:
    def __init__(self, file_name, nrows=None, standardize=True, max_sample_freq=1e6, **channel_names):
        """
        This class provides visualization capabilities for picoscope csv files


        :type file_name: str
        :param file_name: The csv file name

        :type nrows:  int
        :param nrows: Only read this many records from the csv file

        :type standardize: Bool
        :param standardize: Convert everything to SI units (default=True)

        :type max_sample_freq: float
        :param max_sample_freq: Downsample if freq exceeds max_sample_freq (hz)

        :type channel_names: str *kwargs
        :param channel_names: channel name mappings like a='primary', b='secondary'

        """
        is_csv = bool(re.match(r'.*\.csv$', file_name))
        if not is_csv:
            raise ValueError('You can only supply csv files')

        self.file_name = file_name

        if set(channel_names.keys()) - set('abcd'):
            raise ValueError('\n\nCan only supply names for channels labeled "a", "b", "c", or "d"')
        self._conversions = {
            'ms': (.001, 's'),
        }

        self.max_sample_freq = max_sample_freq
        self._channel_names = channel_names
        self._standardize = standardize
        self._units = None
        self._sample_freq = None
        self.df = self.load(nrows)

    @property
    def sample_freq(self):
        """
        The sample frequency of the loaded dataframe
        """
        return self.get_sample_freq(self.df)

    def get_sample_freq(self, df):
        """
        Returns the sample frequency from a dataframe

        :type df: pandas.DataFrame
        :param df: A pandas dataframe from which to compute sample frequency

        :rtype: float
        :return: Sample frequency in inverse units of the dataframe time units
        """
        sample_time = df.head(1000).iloc[:, 0].diff().median()
        return 1. / sample_time

    @property
    def units(self):
        """
        The units specified for the input csv columns
        """
        if self._units is None:
            with open(self.file_name) as in_file:
                for line_no, line in itertools.islice(enumerate(in_file), 2):
                    if line_no == 1:
                        units_line = line.strip()


            rex_list = [
                re.compile(r'\((\S+)\),\((\S+)\),\((\S+)\),\((\S+)\),\((\S+)\)'),
                re.compile(r'\((\S+)\),\((\S+)\),\((\S+)\),\((\S+)\)'),
                re.compile(r'\((\S+)\),\((\S+)\),\((\S+)\)'),
                re.compile(r'\((\S+)\),\((\S+)\)'),
            ]

            for rex in rex_list:
                m = rex.match(units_line)
                if m:
                    self._units = list(m.groups())
                    break

            ## when 3 channel present
            ## rex = re.compile(r'\((\S+)\),\((\S+)\),\((\S+)\),\((\S+)\)')

            ## when 4 channels present
            #rex = re.compile(r'\((\S+)\),\((\S+)\),\((\S+)\),\((\S+)\),\((\S+)\)')

            #self._units = list(rex.match(units_line).groups())
        return self._units

    @property
    def unit_map(self):
        """
        A dictionary mapping column name to unit name
        """
        return dict(zip(self.channels, self.units))

    @property
    def channels(self):
        """
        A list of channels names
        """
        return list(self.df.columns)

    def _do_standardize(self, df):
        """
        This method standardizes the units of all columns to be in SI

        :type df: pandas.DataFrame
        :param df: A pandas dataframe from which to compute sample frequency
        """
        for ind, (orig_unit, col_name) in enumerate(zip(self.units, df.columns)):
            multiplier, new_unit = self._conversions.get(orig_unit, (None, None))
            if multiplier is not None:
                df.loc[:, col_name] = multiplier * df.loc[:, col_name]
                self._units[ind] = new_unit
        return df

    def _rename_columns(self, df):
        """
        Rename columns to t, a, b, c, d

        :type df: pandas.DataFrame
        :param df: A pandas dataframe for renaming columns
        """
        new_names = {'Time': 't'}
        new_names.update({'Channel {}'.format(s.upper()): s for s in 'abcd'})
        df.rename(columns=new_names, inplace=True)
        return df

    def _customize_names(self, df):
        """
        Customizes column names to those specified by the user

        :type df: pandas.DataFrame
        :param df: A pandas dataframe for renaming columns
        """
        df.rename(columns=self._channel_names, inplace=True)
        return df

    def _down_sample(self, df, delta=None):
        """
        Downsample the supplied dataframe to have a minimum sample time.
        All measurements are averaged over the mininum sample time

        :type df: pandas.DataFrame
        :param df: A pandas dataframe for renaming columns

        :type delta: float
        :param delta: The minimum sample time in the same time uints as df
        """
        if delta is None:
            return df
        else:
            df.loc[:, 't'] = delta * (df.t // delta)
            dfg = df.groupby(by='t').mean().reset_index()
            return dfg

    def load(self, nrows=None):
        """
        Load data optionally limiting to nrows records

        :type nrows: int
        :param df: The maxinumum number of rows to load (defaults to all)
        """
        self.get_spectrum.cache_clear()
        df = pd.read_csv(self.file_name, skiprows=[1, 2], nrows=nrows)
        self._rename_columns(df)
        self._customize_names(df)
        if self._standardize:
            self._do_standardize(df)

        if self.get_sample_freq(df) > self.max_sample_freq:
            df = self._down_sample(df, 1. / self.max_sample_freq)
        return df

    @staticmethod
    def overlay_curves(*curves):
        """
        A utility method for overlaying holoviews curves

        :type curves:  holoviews.Curve
        :param curves: *args hold curves to overlay
        """
        disp = hv.Overlay(curves).collate()
        hv.util.opts('RGB [width=800 height=400]', disp)
        return disp

    def plot_time_series(self, *channels):
        """
        Plot time series for the supplied channel names.

        :type channels: str
        :param channels: *args of channel names
        """
        bad_channels = set(channels) - set(self.channels)
        if bad_channels or not channels:
            raise ValueError('\n\n Must supply channel names from {}'.format(self.channels))
        time_dim = hv.Dimension('time', label='time', unit=self.unit_map['t'])
        colors = ['blue', 'red', 'green', 'black']
        curves = []
        for ind, channel in enumerate(channels):
            chan_dim = hv.Dimension(channel, label=channel, unit=self.unit_map[channel])
            curve = hv.Curve((self.df.t, self.df.loc[:, channel]), kdims=[time_dim], vdims=[chan_dim])
            curve = datashade(curve, aggregator=ds.reductions.any(), cmap=[colors[ind]])

            curves.append(curve)

        return self.overlay_curves(*curves)

    @lru_cache()
    def get_spectrum(self, channel, db=True, normalized=False):
        df = lomb_scargle(self.df, 't', channel, freq_order=True)
        if normalized:
            df.loc[:, 'power'] = df.power / df.power.sum()
        if db:
            df.loc[:, 'power'] = 10 * np.log10(df.power)
        return df

    def plot_spectrum(self, channel, color='blue', db=True, normalized=False):
        """
        Plot spectrum for the supplied channel.

        :type channel: str
        :param channel: channel name

        :type db: bool
        :param db: Use dB scale for spectrum power

        :type normalize: bool
        :param normalize: Normalize spectrum so that sum(power) = 1
        """

        df = self.get_spectrum(channel, db=db, normalized=normalized)
        freq_dim = hv.Dimension('freq', label='freq', unit='Hz')

        if db:
            unit = 'db power'
        else:
            unit = 'power'

        chan_dim = hv.Dimension(channel, label=channel, unit=unit)
        curve = hv.Curve((df.freq, df.power), kdims=[freq_dim], vdims=[chan_dim])
        curve = datashade(curve, aggregator=ds.reductions.any(), cmap=[color])
        hv.util.opts('RGB [width=800 height=400]', curve)
        return curve


#####################################################################################################################
# Some day I want to get this working from the command line, but today is not that day
#####################################################################################################################
# def ensure_file_exists(file_name):
#     """
#     Raises a nice error message if filename does not exist
#     """
#     if not os.path.isfile(file_name):
#         msg = "\n\nThe file: '{}' does not exist\n\n".format(file_name)
#         sys.stderr.write(msg)
#         sys.exit(1)
# @click.command()
# @click.argument('channels', nargs=-1)
# @click.option('-f', '--file_name', default=None, type=str, help='A pico-generated csv file')
# @click.option('-s', '--spectrum', is_flag=True, help='Plot the spectrum instead of the time series')
# @click.option('-n', '--nrows', default=None, type=int, help='Limit number of rows to this number')
# @click.option('-m', '--max_freq', default=1e6, type=float, help='Average down to this max sample frequency')
# def main(file_name, spectrum, nrows, max_freq, channels):
#     if file_name is None or not channels:
#         sys.stderr.write('\n{} --help\n\n'.format(__file__))
#         return
#
#     ensure_file_exists(file_name)
#
#     p = Pico(file_name, nrows=nrows, max_sample_freq=max_freq)
#     layout = p.plot_time_series(*channels)
#
#     renderer = hv.renderer('bokeh')
#     renderer = renderer.instance(mode='server')
#
#     renderer.server_doc(layout)
#
#
#
# if __name__ == '__main__':
#     main()
