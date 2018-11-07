import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import pandas as pd
import plotly
from dash.dependencies import Input, Output, State
from plotly import graph_objs as go

from OnePy.sys_module.metabase_env import OnePyEnvBase

TRADE_LOG = OnePyEnvBase.full_trade_log

APP = dash.Dash()
APP.scripts.config.serve_locally = True

APP.layout = html.Div([
    html.H4('OnePy Trade Log Analysis'),
    dt.DataTable(
        rows=TRADE_LOG.to_dict('records'),

        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        id='trade_log'
    ),

    dcc.Graph(
        id='drawdown_pnl'
    ),

    dcc.Graph(
        id='run_up_pnl'
    ),

], className="container")


@APP.callback(
    Output('trade_log', 'selected_row_indices'),
    [Input('drawdown_pnl', 'clickData')],
    [State('trade_log', 'selected_row_indices')])
def update_selected_row_indices(clickData, selected_row_indices):
    if clickData:
        for point in clickData['points']:
            if point['pointNumber'] in selected_row_indices:
                selected_row_indices.remove(point['pointNumber'])
            else:
                selected_row_indices.append(point['pointNumber'])

    return selected_row_indices


@APP.callback(
    Output('drawdown_pnl', 'figure'),
    [Input('trade_log', 'rows'),
     Input('trade_log', 'selected_row_indices')])
def update_run_up_figure(rows, selected_row_indices):

    dff = pd.DataFrame(rows)
    profit_diff = dff.loc[dff.returns_diff > 0]
    loss_diff = dff.loc[dff.returns_diff < 0]

    fig = plotly.tools.make_subplots(
        rows=1, cols=1,
        shared_xaxes=True)

    fig['layout'].update(dict(title='Profit & Loss vs Run-up'))
    fig['layout']['xaxis'].update(dict(title='Run-up(%)'))
    fig['layout']['yaxis'].update(dict(title='Profit & Loss(%)'))

    fig.append_trace({
        'x': profit_diff['run_up']*100,
        'y': profit_diff['returns_diff']*100,
        'text': profit_diff.entry_date + ' to ' + profit_diff.exit_date,
        'type': 'scatter',
        'marker': dict(color='black'),
        'mode': 'markers',
        'name': 'win',
        'line': {'width': 1}
    }, 1, 1)
    fig.append_trace({
        'x': loss_diff['run_up']*100,
        'y': -loss_diff['returns_diff']*100,
        'type': 'scatter',
        'text': loss_diff.entry_date + ' to ' + loss_diff.exit_date,
        'marker': dict(color='red'),
        'mode': 'markers',
        'name': 'lose',
        'line': {'width': 1}
    }, 1, 1)

    fig.append_trace({
        'x': [0, 10],
        'y': [0, 10],
        'type': 'scatter',
        'mode': 'lines',
        'name': 'Win diagonal',
        'line': {'width': 1}
    }, 1, 1)

    return fig


@APP.callback(
    Output('run_up_pnl', 'figure'),
    [Input('trade_log', 'rows'),
     Input('trade_log', 'selected_row_indices')])
def update__drawdown_figure(rows, selected_row_indices):

    dff = pd.DataFrame(rows)
    profit_diff = dff.loc[dff.returns_diff > 0]
    loss_diff = dff.loc[dff.returns_diff < 0]

    fig = plotly.tools.make_subplots(
        rows=1, cols=1,
        shared_xaxes=True)
    fig['layout'].update(dict(title='Profit & Loss vs Drawdown'))
    fig['layout']['xaxis'].update(dict(title='Drawdown(%)'))
    fig['layout']['yaxis'].update(dict(title='Profit & Loss(%)'))

    fig.append_trace({
        'x': profit_diff['drawdown']*100,
        'y': profit_diff['returns_diff']*100,
        'type': 'scatter',
        'marker': dict(color='black'),
        'text': profit_diff.entry_date + ' to ' + profit_diff.exit_date,
        'mode': 'markers',
        'name': 'win',
        'line': {'width': 1}
    }, 1, 1)

    fig.append_trace({
        'x': loss_diff['drawdown']*100,
        'y': -loss_diff['returns_diff']*100,
        'text': loss_diff.entry_date + ' to ' + loss_diff.exit_date,
        'type': 'scatter',
        'marker': dict(color='red'),
        'mode': 'markers',
        'name': 'lose',
        'line': {'width': 1}
    }, 1, 1)

    fig.append_trace({
        'x': [0, 10],
        'y': [0, 10],
        'type': 'scatter',
        'mode': 'lines',
        'name': 'Loss diagonal',
        'line': {'width': 1}
    }, 1, 1)

    return fig


if __name__ == '__main__':
    APP.run_server(debug=True)
