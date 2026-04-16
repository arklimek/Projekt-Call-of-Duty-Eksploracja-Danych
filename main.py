import webbrowser
from io import StringIO
from threading import Timer

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html, dash_table

# =========================================================
# 1) CSV
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
# 2) Dane
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


# =========================================================
# 3) Styl globu "jak na screenie"
# =========================================================

def add_glow_layer(fig, df, name, color, size_mul, opacity, showlegend=False):
    if df.empty:
        return

    fig.add_trace(
        go.Scattergeo(
            lon=df["lon"],
            lat=df["lat"],
            mode="markers",
            hoverinfo="skip",
            showlegend=showlegend,
            name=name,
            marker=dict(
                size=(df["weight"] * size_mul).clip(lower=14, upper=60),
                color=color,
                opacity=opacity,
                line=dict(width=0),
            ),
        )
    )


def add_points_layer(fig, df, name, color):
    if df.empty:
        return

    fig.add_trace(
        go.Scattergeo(
            lon=df["lon"],
            lat=df["lat"],
            mode="markers+text",
            text=df["year"].astype(str),
            textposition="top center",
            name=name,
            customdata=df[["conflict", "location", "year", "weight", "source_type"]],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Lokalizacja: %{customdata[1]}<br>"
                "Rok: %{customdata[2]}<br>"
                "Typ: %{customdata[4]}<br>"
                "Waga: %{customdata[3]}<extra></extra>"
            ),
            textfont=dict(color="rgba(255,220,160,0.95)", size=10),
            marker=dict(
                size=(df["weight"] * 1.9 + 4).clip(lower=6, upper=22),
                color=color,
                opacity=0.98,
                line=dict(color="rgba(255,245,220,0.9)", width=1),
            ),
        )
    )


def make_globe_figure(df, show_glow=True, show_labels=True):
    fig = go.Figure()

    mw = df[df["source_type"] == "MW"]
    real = df[df["source_type"] == "REAL"]

    # Warstwy glow - od największej i najbardziej przezroczystej
    if show_glow:
        add_glow_layer(fig, df, "Shockwave", "rgba(255,120,20,0.10)", 8.0, 0.10, False)
        add_glow_layer(fig, df, "Heat glow", "rgba(255,90,0,0.16)", 5.8, 0.16, False)
        add_glow_layer(fig, df, "Core glow", "rgba(255,180,60,0.20)", 3.8, 0.20, False)

    # Delikatne połączenia między punktami tego samego typu - daje efekt pęknięć/sieci
    def add_link_lines(subdf, color):
        if len(subdf) < 2:
            return

        subdf = subdf.sort_values(["year", "weight"], ascending=[True, False]).reset_index(drop=True)
        line_lons = []
        line_lats = []

        for i in range(len(subdf) - 1):
            line_lons.extend([subdf.loc[i, "lon"], subdf.loc[i + 1, "lon"], None])
            line_lats.extend([subdf.loc[i, "lat"], subdf.loc[i + 1, "lat"], None])

        fig.add_trace(
            go.Scattergeo(
                lon=line_lons,
                lat=line_lats,
                mode="lines",
                hoverinfo="skip",
                showlegend=False,
                line=dict(width=1.2, color=color),
                opacity=0.45,
            )
        )

    add_link_lines(real, "rgba(255,110,40,0.55)")
    add_link_lines(mw, "rgba(255,190,70,0.45)")

    # Właściwe punkty
    add_points_layer(fig, mw, "MW", "#ffcf4a")
    add_points_layer(fig, real, "REAL", "#ff5a1f")

    # Dodatkowa centralna poświata planety
    fig.add_trace(
        go.Scattergeo(
            lon=[25],
            lat=[20],
            mode="markers",
            hoverinfo="skip",
            showlegend=False,
            marker=dict(
                size=240,
                color="rgba(255,140,50,0.05)",
                line=dict(width=0),
            ),
        )
    )

    text_mode = "text" if show_labels else "none"

    fig.update_geos(
        projection_type="orthographic",
        projection_rotation=dict(lon=20, lat=15, roll=0),
        showframe=False,
        showcoastlines=False,
        showcountries=False,
        showland=True,
        landcolor="rgb(18, 22, 30)",
        showocean=True,
        oceancolor="rgb(8, 12, 20)",
        showlakes=False,
        bgcolor="rgba(0,0,0,0)",
        lataxis_showgrid=False,
        lonaxis_showgrid=False,
    )

    # "Gwiazdy" w tle jako adnotacje nie wyglądają dobrze,
    # więc tło robimy bardzo ciemne + radialny klimat przez papier/layout.
    fig.update_layout(
        title=dict(
            text="Konflikty MW + realne konflikty",
            x=0.5,
            xanchor="center",
            font=dict(size=24, color="rgba(255,220,170,0.95)")
        ),
        paper_bgcolor="#020202",
        plot_bgcolor="#020202",
        font=dict(color="white"),
        margin=dict(l=0, r=0, t=60, b=0),
        height=820,
        legend=dict(
            bgcolor="rgba(0,0,0,0.35)",
            bordercolor="rgba(255,120,40,0.18)",
            borderwidth=1,
            x=0.02,
            y=0.98,
            font=dict(color="rgba(255,230,200,0.95)")
        ),
    )

    # Ukrycie domyślnej warstwy tekstowej jeśli trzeba
    if not show_labels:
        for trace in fig.data:
            if getattr(trace, "mode", "") == "markers+text":
                trace.text = None

    return fig


# =========================================================
# 4) Dash
# =========================================================

app = Dash(__name__)
app.title = "MW Globe"

initial_df = filter_df(1999, 2020, True, True)

app.layout = html.Div(
    style={
        "background": "radial-gradient(circle at 30% 35%, #3a1d08 0%, #120a05 18%, #040404 42%, #010101 100%)",
        "minHeight": "100vh",
        "padding": "16px",
        "fontFamily": "Arial, sans-serif",
        "color": "white",
    },
    children=[
        html.Div(
            style={
                "maxWidth": "1400px",
                "margin": "0 auto",
            },
            children=[
                html.Div(
                    style={
                        "padding": "14px 18px",
                        "marginBottom": "14px",
                        "border": "1px solid rgba(255,120,40,0.22)",
                        "backgroundColor": "rgba(0,0,0,0.28)",
                        "backdropFilter": "blur(2px)",
                        "boxShadow": "0 0 24px rgba(255,120,40,0.08)",
                    },
                    children=[
                        html.H2(
                            "Konflikty MW + realne konflikty",
                            style={"margin": "0 0 12px 0", "color": "#ffd6a8"}
                        ),
                        html.Div(
                            style={"marginBottom": "10px"},
                            children=[
                                html.Label("Zakres lat", style={"display": "block", "marginBottom": "8px", "color": "#ffd6a8"}),
                                dcc.RangeSlider(
                                    id="year-range",
                                    min=1999,
                                    max=2020,
                                    step=1,
                                    value=[1999, 2020],
                                    marks={y: str(y) for y in ALL_YEARS},
                                    allowCross=False,
                                ),
                            ],
                        ),
                        html.Div(
                            style={"display": "flex", "gap": "30px", "flexWrap": "wrap"},
                            children=[
                                html.Div([
                                    html.Div("Źródła", style={"marginBottom": "6px", "color": "#ffd6a8"}),
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
                                ]),
                                html.Div([
                                    html.Div("Efekty", style={"marginBottom": "6px", "color": "#ffd6a8"}),
                                    dcc.Checklist(
                                        id="effects-checklist",
                                        options=[
                                            {"label": " glow", "value": "GLOW"},
                                            {"label": " lata nad punktami", "value": "LABELS"},
                                        ],
                                        value=["GLOW", "LABELS"],
                                        inline=True,
                                        inputStyle={"marginRight": "6px", "marginLeft": "10px"},
                                    ),
                                ]),
                            ],
                        ),
                    ],
                ),
                dcc.Graph(
                    id="globe-graph",
                    figure=make_globe_figure(initial_df, show_glow=True, show_labels=True),
                    config={
                        "displayModeBar": True,
                        "scrollZoom": True,
                    },
                    style={
                        "border": "1px solid rgba(255,120,40,0.18)",
                        "backgroundColor": "rgba(0,0,0,0.20)",
                        "boxShadow": "0 0 30px rgba(255,120,40,0.08)",
                    },
                ),
                html.Div(
                    style={
                        "marginTop": "16px",
                        "padding": "12px",
                        "border": "1px solid rgba(255,120,40,0.18)",
                        "backgroundColor": "rgba(0,0,0,0.28)",
                    },
                    children=[
                        html.H3("Tabela filtrowanych rekordów", style={"color": "#ffd6a8"}),
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
                            style_table={"overflowX": "auto"},
                            style_header={
                                "backgroundColor": "#2a140b",
                                "color": "#ffd6a8",
                                "fontWeight": "bold",
                                "border": "1px solid #5a2b14",
                            },
                            style_cell={
                                "backgroundColor": "#0a0a0a",
                                "color": "white",
                                "textAlign": "left",
                                "padding": "8px",
                                "border": "1px solid #2a140b",
                                "whiteSpace": "normal",
                                "height": "auto",
                            },
                        ),
                    ],
                ),
            ],
        )
    ],
)


@app.callback(
    Output("globe-graph", "figure"),
    Output("records-table", "data"),
    Input("year-range", "value"),
    Input("source-checklist", "value"),
    Input("effects-checklist", "value"),
)
def update_view(year_range, source_values, effect_values):
    year_min, year_max = year_range
    show_mw = "MW" in source_values
    show_real = "REAL" in source_values
    show_glow = "GLOW" in effect_values
    show_labels = "LABELS" in effect_values

    df = filter_df(year_min, year_max, show_mw=show_mw, show_real=show_real)
    fig = make_globe_figure(df, show_glow=show_glow, show_labels=show_labels)
    return fig, df.to_dict("records")


def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050")


if __name__ == "__main__":
    print("Uruchamianie aplikacji...")
    print("Adres: http://127.0.0.1:8050")
    Timer(1.2, open_browser).start()
    app.run(debug=True)