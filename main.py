import webbrowser
from io import StringIO
from threading import Timer

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html, dash_table

# =========================================================
# 1) CSV osadzone bezpośrednio w kodzie
# =========================================================

MW_CSV = """year,conflict,location,lat,lon,source_type,weight
1999,Ultranationalist coup / Russian-Chechen theater,Grozny; Chechnya; Russia,43.3171,45.6983,MW,6
2011,Afghanistan operation,Kabul; Afghanistan,34.5553,69.2075,MW,5
2011,Russian escalation,Moscow; Russia,55.7558,37.6173,MW,7
2011,Airport massacre,Sheremetyevo Airport; Moscow; Russia,55.9726,37.4146,MW,8
2013,Urzikstan insurgency (mapped to Syria),Aleppo; Syria,36.2021,37.1343,MW,7
2013,Urzikstan regime / regional war (mapped to Syria),Damascus; Syria,33.5138,36.2765,MW,6
2013,Urzikstan rural battles (mapped to central Syria),Central Syrian Desert; Syria,34.5000,38.0000,MW,4
2016,War in Eastern Europe,Donetsk; Ukraine,48.0159,37.8028,MW,7
2016,European terror operations,Prague; Czechia,50.0755,14.4378,MW,4
2016,European terror operations,London; United Kingdom,51.5074,-0.1278,MW,5
2016,Government district attack,Westminster; London; United Kingdom,51.4995,-0.1248,MW,6
2016,US invasion / escalation,Washington D.C.; USA,38.9072,-77.0369,MW,7
2016,White House assault,White House; Washington D.C.; USA,38.8977,-77.0365,MW,8
2016,NATO / port strike,Hamburg; Germany,53.5511,9.9937,MW,5
2016,Port battle,Port of Hamburg; Germany,53.5461,9.9661,MW,6
2019,Verdansk conflict (mapped to Donetsk basin),Donetsk; Ukraine,48.0159,37.8028,MW,7
2019,Verdansk stadium AO (mapped),Donbas Arena; Donetsk; Ukraine,48.0153,37.8090,MW,6
2019,Covert action,Saint Petersburg; Russia,59.9311,30.3609,MW,4
2019,Caucasus transit operations,Tbilisi; Georgia,41.7151,44.8271,MW,4
2019,Black Sea / Bosporus operation,Istanbul; Turkey,41.0082,28.9784,MW,5
2019,Maritime choke point,Bosporus; Turkey,41.1200,29.1000,MW,5
2020,US urban operation,Chicago; USA,41.8781,-87.6298,MW,4
2020,US urban operation,Central Chicago; USA,41.8818,-87.6231,MW,4
"""

REAL_CONFLICTS_CSV = """year,conflict,location,lat,lon,source_type,weight
1999,Second Chechen War,Grozny; Chechnya; Russia,43.3171,45.6983,REAL,8
2001,War in Afghanistan,Kabul; Afghanistan,34.5553,69.2075,REAL,9
2003,Iraq War,Baghdad; Iraq,33.3152,44.3661,REAL,9
2006,Lebanon War,Beirut; Lebanon,33.8938,35.5018,REAL,6
2008,Russo-Georgian War,Gori; Georgia,41.9842,44.1158,REAL,7
2011,Libyan Civil War,Tripoli; Libya,32.8872,13.1913,REAL,7
2011,Syrian Civil War,Damascus; Syria,33.5138,36.2765,REAL,10
2012,Battle of Aleppo,Aleppo; Syria,36.2021,37.1343,REAL,9
2014,War in Donbas,Donetsk; Ukraine,48.0159,37.8028,REAL,9
2014,War against ISIS in Iraq,Mosul; Iraq,36.3400,43.1300,REAL,8
2015,Yemeni Civil War,Sanaa; Yemen,15.3694,44.1910,REAL,8
2016,Battle of Mosul,Mosul; Iraq,36.3400,43.1300,REAL,9
2017,Battle of Raqqa,Raqqa; Syria,35.9594,38.9981,REAL,8
2018,Battle of Ghazni,Ghazni; Afghanistan,33.5451,68.4174,REAL,6
2019,Turkish offensive in northeast Syria,Ras al-Ayn; Syria,36.8486,40.0736,REAL,7
2020,Second Nagorno-Karabakh War,Shusha; Nagorno-Karabakh,39.7601,46.7499,REAL,8
"""

mw_df = pd.read_csv(StringIO(MW_CSV))
real_df = pd.read_csv(StringIO(REAL_CONFLICTS_CSV))

# Ujednolicenie typów
for df in (mw_df, real_df):
    df["year"] = df["year"].astype(int)
    df["lat"] = df["lat"].astype(float)
    df["lon"] = df["lon"].astype(float)
    df["weight"] = df["weight"].astype(float)
    df["conflict"] = df["conflict"].astype(str)
    df["location"] = df["location"].astype(str)
    df["source_type"] = df["source_type"].astype(str)

ALL_YEARS = list(range(1999, 2021))


# =========================================================
# 2) Pomocnicze funkcje
# =========================================================

def filter_df(year_min, year_max, show_mw=True, show_real=True):
    parts = []

    if show_mw:
        parts.append(mw_df[(mw_df["year"] >= year_min) & (mw_df["year"] <= year_max)])

    if show_real:
        parts.append(real_df[(real_df["year"] >= year_min) & (real_df["year"] <= year_max)])

    if not parts:
        return pd.DataFrame(columns=["year", "conflict", "location", "lat", "lon", "source_type", "weight", "label"])

    out = pd.concat(parts, ignore_index=True).copy()

    out["label"] = (
        out["source_type"] + " | "
        + out["year"].astype(str) + " | "
        + out["conflict"] + " | "
        + out["location"]
    )

    return out.sort_values(["year", "source_type", "conflict", "location"]).reset_index(drop=True)


def make_globe_figure(df, show_heatmap=True):
    fig = go.Figure()

    # Pseudo-heatmap: duże półprzezroczyste okręgi pod punktami.
    # To nie jest "true heatmap", ale działa stabilnie na globie Scattergeo.
    if show_heatmap and not df.empty:
        fig.add_trace(
            go.Scattergeo(
                lon=df["lon"],
                lat=df["lat"],
                mode="markers",
                text=df["label"],
                hoverinfo="skip",
                showlegend=True,
                name="Heat intensity",
                marker=dict(
                    size=(df["weight"] * 6).clip(lower=10, upper=45),
                    color=df["weight"],
                    cmin=1,
                    cmax=10,
                    colorscale="RdYlBu_r",
                    opacity=0.18,
                    line=dict(width=0),
                ),
            )
        )

    mw_points = df[df["source_type"] == "MW"]
    real_points = df[df["source_type"] == "REAL"]

    if not mw_points.empty:
        fig.add_trace(
            go.Scattergeo(
                lon=mw_points["lon"],
                lat=mw_points["lat"],
                mode="markers+text",
                text=mw_points["year"].astype(str),
                textposition="top center",
                customdata=mw_points[["conflict", "location", "year", "weight", "source_type"]],
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Lokalizacja: %{customdata[1]}<br>"
                    "Rok: %{customdata[2]}<br>"
                    "Typ: %{customdata[4]}<br>"
                    "Waga: %{customdata[3]}<extra></extra>"
                ),
                name="MW",
                marker=dict(
                    size=(mw_points["weight"] * 2.2 + 4).clip(lower=7, upper=24),
                    color="#ffcc00",
                    opacity=0.95,
                    line=dict(color="white", width=1),
                ),
            )
        )

    if not real_points.empty:
        fig.add_trace(
            go.Scattergeo(
                lon=real_points["lon"],
                lat=real_points["lat"],
                mode="markers+text",
                text=real_points["year"].astype(str),
                textposition="top center",
                customdata=real_points[["conflict", "location", "year", "weight", "source_type"]],
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Lokalizacja: %{customdata[1]}<br>"
                    "Rok: %{customdata[2]}<br>"
                    "Typ: %{customdata[4]}<br>"
                    "Waga: %{customdata[3]}<extra></extra>"
                ),
                name="REAL",
                marker=dict(
                    size=(real_points["weight"] * 2.2 + 4).clip(lower=7, upper=24),
                    color="#ff3b30",
                    opacity=0.95,
                    line=dict(color="white", width=1),
                ),
            )
        )

    fig.update_geos(
        projection_type="orthographic",
        showland=True,
        landcolor="rgb(28, 37, 54)",
        showocean=True,
        oceancolor="rgb(5, 12, 24)",
        showcountries=True,
        countrycolor="rgb(140, 160, 180)",
        coastlinecolor="rgb(180, 200, 220)",
        showcoastlines=True,
        showlakes=True,
        lakecolor="rgb(5, 12, 24)",
        bgcolor="rgb(2, 6, 16)",
    )

    fig.update_layout(
        title="Konflikty MW + realne konflikty (1999–2020)",
        paper_bgcolor="rgb(2, 6, 16)",
        plot_bgcolor="rgb(2, 6, 16)",
        font=dict(color="white"),
        legend=dict(
            bgcolor="rgba(0,0,0,0.25)",
            borderwidth=0,
            x=0.01,
            y=0.99,
        ),
        margin=dict(l=10, r=10, t=50, b=10),
        height=760,
    )

    return fig


# =========================================================
# 3) Aplikacja Dash
# =========================================================

app = Dash(__name__)
app.title = "Konflikty MW + realne konflikty"

initial_df = filter_df(1999, 2020, True, True)

app.layout = html.Div(
    style={
        "backgroundColor": "#08111f",
        "minHeight": "100vh",
        "padding": "18px",
        "fontFamily": "Arial, sans-serif",
        "color": "white",
    },
    children=[
        html.H2("Konflikty MW + realne konflikty (1999–2020)"),
        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr",
                "gap": "14px",
                "marginBottom": "12px",
            },
            children=[
                html.Div(
                    style={"maxWidth": "900px"},
                    children=[
                        html.Label("Zakres lat", style={"display": "block", "marginBottom": "8px"}),
                        dcc.RangeSlider(
                            id="year-range",
                            min=1999,
                            max=2020,
                            step=1,
                            value=[1999, 2020],
                            marks={y: str(y) for y in ALL_YEARS},
                            allowCross=False,
                            tooltip={"placement": "bottom", "always_visible": False},
                        ),
                    ],
                ),
                html.Div(
                    style={
                        "display": "flex",
                        "flexWrap": "wrap",
                        "gap": "28px",
                        "alignItems": "center",
                    },
                    children=[
                        html.Div(
                            children=[
                                html.Div("Źródła", style={"marginBottom": "6px"}),
                                dcc.Checklist(
                                    id="source-checklist",
                                    options=[
                                        {"label": " MW", "value": "MW"},
                                        {"label": " REAL", "value": "REAL"},
                                    ],
                                    value=["MW", "REAL"],
                                    inline=True,
                                    inputStyle={"marginRight": "6px", "marginLeft": "10px"},
                                ),
                            ]
                        ),
                        html.Div(
                            children=[
                                html.Div("Warstwy", style={"marginBottom": "6px"}),
                                dcc.Checklist(
                                    id="layer-checklist",
                                    options=[
                                        {"label": " pseudo-heatmap", "value": "HEAT"},
                                    ],
                                    value=["HEAT"],
                                    inline=True,
                                    inputStyle={"marginRight": "6px", "marginLeft": "10px"},
                                ),
                            ]
                        ),
                    ],
                ),
            ],
        ),
        dcc.Graph(
            id="globe-graph",
            figure=make_globe_figure(initial_df, show_heatmap=True),
            config={
                "displayModeBar": True,
                "scrollZoom": True,
            },
        ),
        html.H3("Tabela filtrowanych rekordów"),
        dash_table.DataTable(
            id="records-table",
            columns=[
                {"name": "year", "id": "year"},
                {"name": "source_type", "id": "source_type"},
                {"name": "conflict", "id": "conflict"},
                {"name": "location", "id": "location"},
                {"name": "lat", "id": "lat"},
                {"name": "lon", "id": "lon"},
                {"name": "weight", "id": "weight"},
            ],
            data=initial_df.to_dict("records"),
            page_size=15,
            sort_action="native",
            filter_action="native",
            style_as_list_view=False,
            style_table={"overflowX": "auto"},
            style_header={
                "backgroundColor": "#12233d",
                "color": "white",
                "fontWeight": "bold",
                "border": "1px solid #1f3557",
            },
            style_cell={
                "backgroundColor": "#0b1729",
                "color": "white",
                "textAlign": "left",
                "padding": "8px",
                "border": "1px solid #1f3557",
                "whiteSpace": "normal",
                "height": "auto",
            },
        ),
    ],
)


@app.callback(
    Output("globe-graph", "figure"),
    Output("records-table", "data"),
    Input("year-range", "value"),
    Input("source-checklist", "value"),
    Input("layer-checklist", "value"),
)
def update_view(year_range, source_values, layer_values):
    year_min, year_max = year_range

    show_mw = "MW" in source_values
    show_real = "REAL" in source_values
    show_heatmap = "HEAT" in layer_values

    df = filter_df(
        year_min=year_min,
        year_max=year_max,
        show_mw=show_mw,
        show_real=show_real,
    )

    fig = make_globe_figure(df, show_heatmap=show_heatmap)
    return fig, df.to_dict("records")


def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050")


if __name__ == "__main__":
    print("Uruchamianie aplikacji...")
    print("Otwórz w przeglądarce: http://127.0.0.1:8050")
    Timer(1.2, open_browser).start()
    app.run(debug=True)