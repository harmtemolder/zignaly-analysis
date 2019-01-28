"""This module uses pandas and Matplotlib to analyse the CSV data
of closed positions downloaded from Zignaly.
"""

from datetime import datetime
import itertools
import locale
import math
import os

from bs4 import BeautifulSoup
import matplotlib
matplotlib.use('TkAgg')  # Added to prevent NSInvalidArgumentException
from matplotlib import pyplot as plt
import numpy.polynomial.polynomial as poly
import pandas as pd
import seaborn as sns


def get_data_from_csv(filename):
    """Opens the given CSV file into a correctly parsed and formatted
    pandas dataframe

    :param filename: (relative) path to CSV file of backtest results
    :return: pandas dataframe containing these trading results

    TODO Finish this function as soon as I have a CSV file available
    """

    df = pd.read_csv(filename)
    return df


def get_data_from_html(filename):
    """Opens the table from the given HTML file into a correctly parsed
    and formatted pandas dataframe

    :param filename: (relative) path to HTML file with closed positions
    :return: pandas dataframe containing these trading results
    """

    # Set locale to properly parse decimals and thousands
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

    parsed_table = []

    with open(filename, mode='rb') as html_file:
        soup = BeautifulSoup(html_file, features='lxml')
        html_file.close()

    table = soup.find('table', {'class': 'table-striped'})
    table_header = list(map(
        BeautifulSoup.get_text,
        table.find('thead').find_all('th')))

    table_rows = table.find('tbody').find_all('tr')

    for row in table_rows:
        parsed_row = {}

        row_cells = row.find_all('td')

        # Parse the first time in the date cell to a new "Open" column
        open_close = row.find('td', {'class':'date'}).find_all('time')
        parsed_row['Open'] = datetime.fromtimestamp(
            int(open_close[0].attrs['datetime']) / 1000)

        # And the second time to a new "Close" column
        parsed_row['Close'] = datetime.fromtimestamp(
            int(open_close[1].attrs['datetime']) / 1000)

        # Get the provider name from the title attribute of the logo
        parsed_row['Provider'] = row.find('img').attrs['title']

        # Get the pair and status from their corresponding cells
        parsed_row['Pair'] = row_cells[table_header.index('Pair')].text
        parsed_row['Status'] = row_cells[table_header.index('Status')].text

        # Get and parse most of the other statistics
        for stat in ['Buy Price', 'Sell Price', 'Amount', 'Invested', 'Profit BTC']:
            parsed_row[stat] = locale.atof(row_cells[table_header.index(stat)].text
                                     .split('\xa0')[0])
            # Note that Amount is in Asset, the others in Currency

        # Rename "Profit BTC" to "Profit"
        parsed_row['Profit'] = parsed_row.pop('Profit BTC')

        # Add some new statistics, calculated off of the existing ones

        # Starting with the duration of the position, in seconds
        parsed_row['Duration (s)'] = (parsed_row['Close']
                                      - parsed_row['Open']).total_seconds()

        # Calculate the profit percentage instead of using Zignaly's
        parsed_row['Profit (%)'] = parsed_row['Profit'] \
                                   / parsed_row['Invested']

        # Split the Pair cell into two separate cells as well
        parsed_row['Asset'] = parsed_row['Pair'].split('/')[0]
        parsed_row['Currency'] = parsed_row['Pair'].split('/')[1]

        # Append everything to the list of parsed rows
        parsed_table.append(parsed_row)

    return pd.DataFrame(parsed_table)


def draw_lmplots(data, combinations):
    """Draw Seaborn's lmplots from data for all combinations of
    variables.

    :param data: A dataframe containing all columns mentioned in combinations
    :param combinations: A list of tuples of column threesomes, where:
                            0 = the independent variable
                            1 = the dependent variable
                            2 = a categorical to be used for colors
    :return: Nothing, just draw to plt
    """

    num_plots = len(combinations)

    # if num_plots > 16:
    #     raise ValueError('Too many subplots to fit in your screen, select less')

    num_columns = int(math.floor(math.sqrt(num_plots)))
    num_rows = int(math.ceil(num_plots / num_columns))
    count = 1

    for combination in combinations:
        plt.subplot(num_rows, num_columns, count)

        sns.lmplot(
            x=combination[0],
            y=combination[1],
            data=data,
            hue=combination[2],
            col='Provider',  # TODO Make this less hacky
            col_wrap=2,
            fit_reg=False)

        count += 1


if __name__ == '__main__':
    # Set the path to your input file here:
    input_file = 'input-20190122.html'

    print('zignaly_analysis: Reading {}...'.format(input_file))

    # Get the file extension to parse the input_file accordingly
    input_file_name, input_file_ext = os.path.splitext(input_file)

    if (input_file_ext == '.csv'):
        data = get_data_from_csv(input_file)
    elif (input_file_ext == '.html'):
        data = get_data_from_html(input_file)
    else:
        raise ValueError('Please input either a CSV or an HTML file...')

    print('zignaly_analysis: Available columns:\n\t{}'.format(
        '\n\t'.join(list(data))
    ))

    # Set the independent variables you'd like to plot in PyPlot here
    independent_vars = [
        'Duration (s)']

    # And the dependent ones here
    dependent_vars = [
        'Profit (%)']

    # And possible modifying categoricals here
    modifiers = [
        'Asset',
        'Provider',
        'Status']

    combinations = list(itertools.product(
        independent_vars,
        dependent_vars,
        modifiers))

    print('zignaly_analysis: Drawing scatter plots for selected column '
          'combinations...')

    # Setup PyPlot
    plt.tight_layout()
    sns.set(style='darkgrid')

    # Draw scatterplots
    draw_lmplots(data, combinations)

    # Save the resulting plots to file
    plt.savefig(
        input_file_name + '.png',
        dpi=72,
        bbox_inches='tight',
        pad_inches=1)

    print('zignaly_analysis: Finished running module. Now what?')
