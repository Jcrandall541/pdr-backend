from dash import dcc, html
from plotly.graph_objs import Figure

figure_names = [
    "pdr_profit_vs_time",
    "trader_profit_vs_time",
    "pdr_profit_vs_ptrue",
    "trader_profit_vs_ptrue",
    "model_performance_vs_time",
    "aimodel_varimps",
    "aimodel_response",
]

empty_selected_vars = dcc.Checklist([], [], id="selected_vars")

empty_graphs_template = html.Div(
    [dcc.Graph(figure=Figure(), id=key) for key in figure_names]
    + [empty_selected_vars],
    style={"display": "none"},
)


def get_waiting_template(err):
    return html.Div(
        [html.H2(f"Error/waiting: {err}", id="sim_state_text")]
        + [empty_graphs_template],
        id="live-graphs",
    )


def get_header_elements(run_id, st, ts):
    return [
        html.H2(f"Simulation ID: {run_id}", id="sim_state_text"),
        html.H3(
            f"Iter #{st.iter_number} ({ts})" if ts != "final" else "Final sim state",
            id="sim_current_ts",
            # stops refreshing if final state was reached. Do not remove this class!
            className="finalState" if ts == "final" else "runningState",
            style={"marginTop": "0", "textAlign": "center"},
        ),
    ]


def side_by_side_graphs(
    figures,
    name1: str,
    name2: str,
    height: str = "50%",
    width1: str = "50%",
    width2: str = "50%",
):
    return html.Div(
        [
            dcc.Graph(figure=figures[name1], id=name1, style={"width": width1}),
            dcc.Graph(figure=figures[name2], id=name2, style={"width": width2}),
        ],
        style={
            "display": "flex",
            "justifyContent": "space-between",
            "width": "100%",
            "height": height,
        },
    )


def get_tabs(figures):
    return [
        {
            "name": "Profit",
            "components": [
                side_by_side_graphs(
                    figures, "pdr_profit_vs_time", "trader_profit_vs_time"
                ),
                side_by_side_graphs(
                    figures, "pdr_profit_vs_ptrue", "trader_profit_vs_ptrue"
                ),
            ],
        },
        {
            "name": "Model performance",
            "components": [
                html.Div(
                    [
                        dcc.Graph(
                            figure=figures["model_performance_vs_time"],
                            id="model_performance_vs_time",
                            style={"width": "100%", "height": "100%"},
                        ),
                    ],
                    style={"width": "100%", "height": "100%"},
                ),
            ],
        },
        {
            "name": "Model response",
            "components": [
                side_by_side_graphs(
                    figures,
                    name1="aimodel_varimps",
                    name2="aimodel_response",
                    height="100%",
                    width1="30%",
                    width2="70%",
                )
            ],
        },
    ]


def selected_var_checklist(state_options, selected_vars_old):
    return dcc.Checklist(
        options=[{"label": var, "value": var} for var in state_options],
        value=selected_vars_old,
        id="selected_vars",
        style={"display": "none"},
    )


def get_tabs_component(elements, selectedTab):
    return dcc.Tabs(
        id="tabs",
        value=selectedTab,
        children=[
            dcc.Tab(
                label=e["name"],
                value=e["name"],
                children=e["components"],
                style={"width": "250px"},
                selected_style={"borderLeft": "4px solid blue"},
            )
            for e in elements
        ],
        vertical=True,
        style={"fontSize": "20px"},
        content_style={
            "width": "100%",
            "height": "100%",
            "borderLeft": "1px solid #d6d6d6",
            "borderTop": "1px solid #d6d6d6",
        },
        parent_style={"width": "100%", "height": "100%"},
    )


def get_main_container():
    return html.Div(
        [
            html.Div(
                empty_graphs_template,
                id="header",
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "height": "100px",
                },
            ),
            html.Div(
                empty_graphs_template,
                id="tabs-container",
                style={"height": "calc(100% - 100px)"},
            ),
        ],
        id="main-container",
        style={
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "flexStart",
            "alignIntems": "start",
            "height": "100%",
        },
    )
