import math
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

BO_CSV = """year,conflict,location,lat,lon,source_type,weight
1961,Bay of Pigs operation,Havana; Cuba,23.1136,-82.3666,BO,8
1962,Vorkuta imprisonment / brainwashing,Vorkuta; Russia,67.4988,64.0525,BO,9
1963,Baikonur sabotage,Baikonur Cosmodrome; Kazakhstan,45.9200,63.3420,BO,7
1963,JFK-era covert crisis,Dallas; USA,32.7767,-96.7970,BO,5
1968,Siege of Khe Sanh,Khe Sanh; Vietnam,16.6273,106.7300,BO,8
1968,Escape from Hue,Hue; Vietnam,16.4637,107.5909,BO,9
1968,Nova-6 testing zone,Laos-Vietnam border,17.0000,106.0000,BO,8
1968,Kowloon pursuit,Hong Kong,22.3193,114.1694,BO,7
1986,Pyrrhic Victory / Angola,Huambo; Angola,-12.7761,15.7392,BO,8
1986,Old Wounds / Afghanistan,Khost; Afghanistan,33.3395,69.9204,BO,8
1986,Time and Fate / Nicaragua,Managua; Nicaragua,12.1140,-86.2362,BO,9
1989,Panama raid / Just Cause,Panama City; Panama,8.9824,-79.5199,BO,7
2025,Old Wounds debrief,The Vault; Afghanistan,33.9391,67.7100,BO,5
2025,Celerium raid,Myanmar,21.9162,95.9560,BO,8
2025,FOB defense,Odisha; India,20.9517,85.0985,BO,7
2025,Lahore negotiations,Lahore; Pakistan,31.5204,74.3587,BO,7
2025,Terminal strike,Singapore,1.2903,103.8519,BO,8
2025,President convoy attack,Sana'a; Yemen,15.3694,44.1910,BO,7
2025,Colossus infiltration,Cayman Islands,19.3133,-81.2546,BO,8
2025,Cordis Die global riots,Los Angeles; USA,34.0522,-118.2437,BO,7
2025,Cordis Die global riots,Paris; France,48.8566,2.3522,BO,7
"""

REAL_CONFLICTS_CSV = """year,conflict,location,lat,lon,source_type,weight
1961,Bay of Pigs Invasion,Havana; Cuba,23.1136,-82.3666,REAL,9
1962,Cuban Missile Crisis,Havana; Cuba,23.1136,-82.3666,REAL,9
1963,JFK assassination,Dallas; USA,32.7767,-96.7970,REAL,8
1968,Siege of Khe Sanh,Khe Sanh; Vietnam,16.6273,106.7300,REAL,9
1968,Battle of Hue,Hue; Vietnam,16.4637,107.5909,REAL,9
1968,Tet Offensive,Ho Chi Minh City; Vietnam,10.8231,106.6297,REAL,10
1979,Soviet-Afghan War,Kabul; Afghanistan,34.5553,69.2075,REAL,10
1986,Angolan Civil War,Huambo; Angola,-12.7761,15.7392,REAL,8
1986,Soviet-Afghan War,Khost; Afghanistan,33.3395,69.9204,REAL,9
1986,Contra War,Managua; Nicaragua,12.1140,-86.2362,REAL,8
1989,United States invasion of Panama,Panama City; Panama,8.9824,-79.5199,REAL,9
2011,Syrian Civil War,Damascus; Syria,33.5138,36.2765,REAL,10
2012,Battle of Aleppo,Aleppo; Syria,36.2021,37.1343,REAL,9
2014,War in Donbas,Donetsk; Ukraine,48.0159,37.8028,REAL,9
2015,Yemeni Civil War,Sana'a; Yemen,15.3694,44.1910,REAL,8
2019,Turkish offensive in northeast Syria,Ras al-Ayn; Syria,36.8486,40.0736,REAL,7
2020,Second Nagorno-Karabakh War,Shusha; Nagorno-Karabakh,39.7601,46.7499,REAL,8
2022,Russian invasion of Ukraine,Kyiv; Ukraine,50.4501,30.5234,REAL,10
2022,Myanmar civil conflict,Naypyidaw; Myanmar,19.7633,96.0785,REAL,6
2023,Red Sea crisis / Yemen spillover,Aden; Yemen,12.7855,45.0187,REAL,6
"""

TERROR_CSV = """year,conflict,location,lat,lon,source_type,weight
1993,World Trade Center bombing,New York City; USA,40.7128,-74.0060,TERROR,7
1995,Oklahoma City bombing,Oklahoma City; USA,35.4676,-97.5164,TERROR,8
1998,US embassy bombings,Nairobi; Kenya,-1.2864,36.8172,TERROR,8
2001,September 11 attacks,New York City; USA,40.7128,-74.0060,TERROR,10
2002,Bali bombings,Kuta; Indonesia,-8.7238,115.1726,TERROR,8
2004,Madrid train bombings,Madrid; Spain,40.4168,-3.7038,TERROR,9
2004,Beslan school siege,Beslan; Russia,43.1920,44.5431,TERROR,9
2005,7 July London bombings,London; United Kingdom,51.5074,-0.1278,TERROR,9
2008,Mumbai attacks,Mumbai; India,19.0760,72.8777,TERROR,9
2011,Domodedovo Airport bombing,Moscow; Russia,55.4103,37.9025,TERROR,7
2013,Westgate attack,Nairobi; Kenya,-1.2864,36.8172,TERROR,7
2015,Paris attacks,Paris; France,48.8566,2.3522,TERROR,9
2016,Brussels bombings,Brussels; Belgium,50.8503,4.3517,TERROR,8
2016,Ataturk Airport attack,Istanbul; Turkey,41.0082,28.9784,TERROR,8
2017,Manchester Arena bombing,Manchester; United Kingdom,53.4808,-2.2426,TERROR,7
2017,Las Vegas mass shooting,Las Vegas; USA,36.1699,-115.1398,TERROR,6
2019,Christchurch mosque attacks,Christchurch; New Zealand,-43.5321,172.6362,TERROR,8
2021,Kabul airport attack,Kabul; Afghanistan,34.5553,69.2075,TERROR,8
2024,Moscow Crocus City Hall attack,Krasnogorsk; Russia,55.8250,37.3250,TERROR,9
"""

mw_df = pd.read_csv(StringIO(MW_CSV))
bo_df = pd.read_csv(StringIO(BO_CSV))
real_df = pd.read_csv(StringIO(REAL_CONFLICTS_CSV))
terror_df = pd.read_csv(StringIO(TERROR_CSV))

for df in (mw_df, bo_df, real_df, terror_df):
    df["year"] = df["year"].astype(int)
    df["lat"] = df["lat"].astype(float)
    df["lon"] = df["lon"].astype(float)
    df["weight"] = df["weight"].astype(float)
    df["conflict"] = df["conflict"].astype(str)
    df["location"] = df["location"].astype(str)
    df["source_type"] = df["source_type"].astype(str)

MIN_YEAR = int(min(mw_df["year"].min(), bo_df["year"].min(), real_df["year"].min(), terror_df["year"].min()))
MAX_YEAR = int(max(mw_df["year"].max(), bo_df["year"].max(), real_df["year"].max(), terror_df["year"].max()))
ALL_YEARS = list(range(MIN_YEAR, MAX_YEAR + 1))


# =========================================================
# 2) Dane i pomocnicze funkcje
# =========================================================

def filter_df(year_min, year_max, show_mw=True, show_bo=True, show_real=True, show_terror=True):
    parts = []

    if show_mw:
        parts.append(mw_df[(mw_df["year"] >= year_min) & (mw_df["year"] <= year_max)])
    if show_bo:
        parts.append(bo_df[(bo_df["year"] >= year_min) & (bo_df["year"] <= year_max)])
    if show_real:
        parts.append(real_df[(real_df["year"] >= year_min) & (real_df["year"] <= year_max)])
    if show_terror:
        parts.append(terror_df[(terror_df["year"] >= year_min) & (terror_df["year"] <= year_max)])

    if not parts:
        return pd.DataFrame(
            columns=["year", "conflict", "location", "lat", "lon", "source_type", "weight", "label"]
        )

    out = pd.concat(parts, ignore_index=True).copy()
    out["label"] = (
        out["source_type"] + " | "
        + out["year"].astype(str) + " | "
        + out["conflict"] + " | "
        + out["location"]
    )
    return out.sort_values(["year", "source_type", "conflict", "location"]).reset_index(drop=True)


def geo_distance_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)

    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def build_overlap_heatmap_df(df, max_distance_km=800, max_year_diff=6):
    """
    Mocniejsza warstwa overlap:
    - referencje: REAL + TERROR
    - porównanie do GAME: MW + BO
    - im bliżej w przestrzeni i czasie, tym większa intensywność
    - wiele dopasowań kumuluje hotspot
    """
    if df.empty:
        return pd.DataFrame(columns=["lat", "lon", "intensity", "location", "year"])

    ref_df = df[df["source_type"].isin(["REAL", "TERROR"])].copy()
    game_df = df[df["source_type"].isin(["MW", "BO"])].copy()

    if ref_df.empty or game_df.empty:
        return pd.DataFrame(columns=["lat", "lon", "intensity", "location", "year"])

    overlap_rows = []

    for _, ref_row in ref_df.iterrows():
        total_intensity = 0.0
        matched_titles = []

        for _, game_row in game_df.iterrows():
            dist_km = geo_distance_km(
                ref_row["lat"], ref_row["lon"],
                game_row["lat"], game_row["lon"]
            )
            year_diff = abs(int(ref_row["year"]) - int(game_row["year"]))

            if dist_km <= max_distance_km and year_diff <= max_year_diff:
                geo_score = 1.0 - (dist_km / max_distance_km)
                time_score = 1.0 - (year_diff / max_year_diff)

                pair_intensity = (
                    (ref_row["weight"] * 0.65 + game_row["weight"] * 0.55)
                    * (0.72 * geo_score + 0.28 * time_score)
                )

                if ref_row["source_type"] == "TERROR":
                    pair_intensity *= 1.15

                if pair_intensity > 0:
                    total_intensity += pair_intensity
                    matched_titles.append(f'{game_row["source_type"]}: {game_row["conflict"]}')

        if total_intensity > 0:
            overlap_rows.append(
                {
                    "lat": float(ref_row["lat"]),
                    "lon": float(ref_row["lon"]),
                    "intensity": float(total_intensity),
                    "location": ref_row["location"],
                    "year": int(ref_row["year"]),
                    "conflict": ref_row["conflict"],
                    "source_type": ref_row["source_type"],
                    "matched_count": len(matched_titles),
                    "matched_titles": ", ".join(matched_titles[:5]),
                }
            )

    if not overlap_rows:
        return pd.DataFrame(columns=["lat", "lon", "intensity", "location", "year"])

    overlap_df = pd.DataFrame(overlap_rows)

    # mocniejsze podbicie kontrastu
    overlap_df["intensity"] = overlap_df["intensity"] ** 1.32

    return overlap_df.sort_values("intensity", ascending=False).reset_index(drop=True)


# =========================================================
# 3) Warstwy wizualne
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
                size=(df["weight"] * size_mul).clip(lower=20, upper=110),
                color=color,
                opacity=opacity,
                line=dict(width=0),
            ),
        )
    )


def add_overlap_heat_layer(fig, overlap_df):
    if overlap_df.empty:
        return

    cmin = float(overlap_df["intensity"].min())
    cmax = float(overlap_df["intensity"].max())

    # zewnętrzna fala
    fig.add_trace(
        go.Scattergeo(
            lon=overlap_df["lon"],
            lat=overlap_df["lat"],
            mode="markers",
            hoverinfo="skip",
            showlegend=False,
            marker=dict(
                size=(overlap_df["intensity"] * 8.8).clip(lower=34, upper=180),
                color=overlap_df["intensity"],
                cmin=cmin,
                cmax=cmax,
                colorscale=[
                    [0.00, "rgba(255,170,0,0.04)"],
                    [0.20, "rgba(255,120,0,0.08)"],
                    [0.45, "rgba(255,60,0,0.14)"],
                    [0.70, "rgba(255,20,0,0.20)"],
                    [1.00, "rgba(255,0,0,0.26)"],
                ],
                opacity=1.0,
                line=dict(width=0),
            ),
        )
    )

    # środkowy glow
    fig.add_trace(
        go.Scattergeo(
            lon=overlap_df["lon"],
            lat=overlap_df["lat"],
            mode="markers",
            hoverinfo="skip",
            showlegend=True,
            name="Overlap REAL/TERROR ↔ GAME",
            marker=dict(
                size=(overlap_df["intensity"] * 5.4).clip(lower=22, upper=120),
                color=overlap_df["intensity"],
                cmin=cmin,
                cmax=cmax,
                colorscale=[
                    [0.00, "rgba(255,220,80,0.10)"],
                    [0.25, "rgba(255,170,0,0.18)"],
                    [0.50, "rgba(255,110,0,0.28)"],
                    [0.75, "rgba(255,40,0,0.38)"],
                    [1.00, "rgba(255,0,0,0.52)"],
                ],
                opacity=1.0,
                line=dict(width=0),
            ),
            customdata=overlap_df[["source_type", "conflict", "location", "year", "matched_count", "matched_titles", "intensity"]],
            hovertemplate=(
                "<b>Overlap %{customdata[0]} ↔ GAME</b><br>"
                "Zdarzenie: %{customdata[1]}<br>"
                "Lokalizacja: %{customdata[2]}<br>"
                "Rok: %{customdata[3]}<br>"
                "Dopasowania: %{customdata[4]}<br>"
                "Przykłady: %{customdata[5]}<br>"
                "Intensywność: %{customdata[6]:.2f}<extra></extra>"
            ),
        )
    )

    # gorący rdzeń
    fig.add_trace(
        go.Scattergeo(
            lon=overlap_df["lon"],
            lat=overlap_df["lat"],
            mode="markers",
            hoverinfo="skip",
            showlegend=False,
            marker=dict(
                size=(overlap_df["intensity"] * 2.1).clip(lower=9, upper=36),
                color="rgba(255,245,180,0.80)",
                line=dict(width=0),
            ),
        )
    )


def add_points_layer(fig, df, name, color, text_color="rgba(255,220,160,0.95)"):
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
            textfont=dict(color=text_color, size=10),
            marker=dict(
                size=(df["weight"] * 2.2 + 5).clip(lower=7, upper=26),
                color=color,
                opacity=0.98,
                line=dict(color="rgba(255,245,220,0.9)", width=1),
            ),
        )
    )


def add_link_lines(fig, subdf, color, width=1.2):
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
            line=dict(width=width, color=color),
            opacity=0.45,
        )
    )


def make_globe_figure(df, show_glow=True, show_labels=True, show_overlap=True):
    fig = go.Figure()

    mw = df[df["source_type"] == "MW"]
    bo = df[df["source_type"] == "BO"]
    real = df[df["source_type"] == "REAL"]
    terror = df[df["source_type"] == "TERROR"]

    overlap_df = build_overlap_heatmap_df(df)

    if show_overlap:
        add_overlap_heat_layer(fig, overlap_df)

    if show_glow:
        add_glow_layer(fig, df, "Shockwave", "rgba(255,110,20,0.10)", 10.0, 0.10, False)
        add_glow_layer(fig, df, "Heat glow", "rgba(255,70,0,0.16)", 7.2, 0.16, False)
        add_glow_layer(fig, df, "Core glow", "rgba(255,180,50,0.22)", 4.6, 0.22, False)

    add_link_lines(fig, real, "rgba(255,70,40,0.55)", 1.4)
    add_link_lines(fig, terror, "rgba(255,0,80,0.45)", 1.2)
    add_link_lines(fig, bo, "rgba(255,170,40,0.42)", 1.2)
    add_link_lines(fig, mw, "rgba(255,220,90,0.35)", 1.2)

    add_points_layer(fig, mw, "MW", "#ffcf4a")
    add_points_layer(fig, bo, "BO", "#ff8a2a")
    add_points_layer(fig, real, "REAL", "#ff3b30")
    add_points_layer(fig, terror, "TERROR", "#ff00aa", "rgba(255,190,235,0.95)")

    # duża centralna poświata, żeby glob nie wyglądał zbyt płasko
    fig.add_trace(
        go.Scattergeo(
            lon=[25],
            lat=[20],
            mode="markers",
            hoverinfo="skip",
            showlegend=False,
            marker=dict(
                size=320,
                color="rgba(255,120,40,0.05)",
                line=dict(width=0),
            ),
        )
    )

    fig.update_geos(
        domain=dict(x=[0.01, 0.99], y=[0.01, 0.99]),
        projection_type="orthographic",
        projection_rotation=dict(lon=20, lat=15, roll=0),
        showframe=False,
        showcoastlines=False,
        showcountries=False,
        showland=True,
        landcolor="rgb(16, 19, 27)",
        showocean=True,
        oceancolor="rgb(5, 8, 15)",
        showlakes=False,
        bgcolor="rgba(0,0,0,0)",
        lataxis_showgrid=False,
        lonaxis_showgrid=False,
    )

    fig.update_layout(
        title=dict(
            text="Konflikty MW + Black Ops + realne wydarzenia + ataki terrorystyczne",
            x=0.5,
            xanchor="center",
            font=dict(size=24, color="rgba(255,220,170,0.95)")
        ),
        paper_bgcolor="#010101",
        plot_bgcolor="#010101",
        font=dict(color="white"),
        margin=dict(l=0, r=0, t=40, b=0),
        height=1040,
        legend=dict(
            bgcolor="rgba(0,0,0,0.35)",
            bordercolor="rgba(255,120,40,0.18)",
            borderwidth=1,
            x=0.01,
            y=0.98,
            font=dict(color="rgba(255,230,200,0.95)")
        ),
    )

    if not show_labels:
        for trace in fig.data:
            if getattr(trace, "mode", "") == "markers+text":
                trace.text = None

    return fig


# =========================================================
# 4) Dash
# =========================================================

app = Dash(__name__)
app.title = "MW + BO Globe"

initial_df = filter_df(MIN_YEAR, MAX_YEAR, True, True, True, True)

app.layout = html.Div(
    style={
        "background": "radial-gradient(circle at 30% 35%, #4a1f06 0%, #160a04 15%, #040404 42%, #010101 100%)",
        "minHeight": "100vh",
        "padding": "8px",
        "fontFamily": "Arial, sans-serif",
        "color": "white",
    },
    children=[
        html.Div(
            style={"maxWidth": "1880px", "width": "100%", "margin": "0 auto"},
            children=[
                html.Div(
                    style={
                        "padding": "14px 18px",
                        "marginBottom": "10px",
                        "border": "1px solid rgba(255,120,40,0.22)",
                        "backgroundColor": "rgba(0,0,0,0.28)",
                        "backdropFilter": "blur(2px)",
                        "boxShadow": "0 0 24px rgba(255,120,40,0.08)",
                    },
                    children=[
                        html.H2(
                            "Konflikty MW + Black Ops + realne wydarzenia + ataki terrorystyczne",
                            style={"margin": "0 0 12px 0", "color": "#ffd6a8"}
                        ),
                        html.Div(
                            style={"marginBottom": "10px"},
                            children=[
                                html.Label("Zakres lat", style={"display": "block", "marginBottom": "8px", "color": "#ffd6a8"}),
                                dcc.RangeSlider(
                                    id="year-range",
                                    min=MIN_YEAR,
                                    max=MAX_YEAR,
                                    step=1,
                                    value=[MIN_YEAR, MAX_YEAR],
                                    marks={y: str(y) for y in ALL_YEARS if y % 5 == 0 or y in (MIN_YEAR, MAX_YEAR)},
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
                                            {"label": " BO", "value": "BO"},
                                            {"label": " REAL", "value": "REAL"},
                                            {"label": " TERROR", "value": "TERROR"},
                                        ],
                                        value=["MW", "BO", "REAL", "TERROR"],
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
                                            {"label": " overlap heatmap", "value": "OVERLAP"},
                                        ],
                                        value=["GLOW", "LABELS", "OVERLAP"],
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
                    figure=make_globe_figure(initial_df, show_glow=True, show_labels=True, show_overlap=True),
                    config={"displayModeBar": True, "scrollZoom": True},
                    style={
                        "width": "100%",
                        "height": "100vh",
                        "margin": "0",
                        "padding": "0",
                        "border": "none",
                        "backgroundColor": "transparent",
                        "boxShadow": "none",
                    },
                ),
                html.Div(
                    style={
                        "marginTop": "12px",
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
                            page_size=20,
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
    show_bo = "BO" in source_values
    show_real = "REAL" in source_values
    show_terror = "TERROR" in source_values

    show_glow = "GLOW" in effect_values
    show_labels = "LABELS" in effect_values
    show_overlap = "OVERLAP" in effect_values

    df = filter_df(
        year_min=year_min,
        year_max=year_max,
        show_mw=show_mw,
        show_bo=show_bo,
        show_real=show_real,
        show_terror=show_terror,
    )

    fig = make_globe_figure(
        df,
        show_glow=show_glow,
        show_labels=show_labels,
        show_overlap=show_overlap,
    )
    return fig, df.to_dict("records")


def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050")


if __name__ == "__main__":
    print("Uruchamianie aplikacji...")
    print("Adres: http://127.0.0.1:8050")
    Timer(1.2, open_browser).start()
    app.run(debug=True)