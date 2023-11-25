from functools import partial
import os
from pathlib import Path

import pandas as pd
import streamlit as st
st.set_page_config(page_title='Cave Feucherolles', page_icon='data_local/wine_icon.png', layout="wide")


def homepage_content():
    st.header("Cave a Vin - Feucherolles")
    st.subheader("2023")

    df = pd.read_csv('data_local/vino_googledrive.csv', sep=';')

    # PREPROC
    # 1 - drop na
    df = df.dropna(subset=('Latitude', 'Longitude'), axis=0)
    df['Annee'] = df['Annee'].apply(lambda x: str(int(x)) if x > 0 else "NA")

    # 2 - demultiply for number of bottles
    delta_clone = 0.003
    order_to_clone = [
        (0, 0),  # center
        (0, 1), (1, 0), (0, -1), (-1, 0),  # +
        (1, 1), (-1, -1), (-1, 1), (1, -1),  # x
        (0, 2), (2, 0), (0, -2), (-2, 0),  # ++
        (2, 2), (-2, -2), (-2, 2), (2, -2),  # xxs
        (2, 1), (-2, -1), (-2, 1), (2, -1),  # xx
        (1, 2), (-1, -2), (-1, 2), (1, -2),  # xx
    ]
    acc = []
    for i, row in df.iterrows():
        for i_bottle in range(row.Quantite):
            series_clone = row.copy(deep=True)
            series_clone.Latitude += (order_to_clone[i_bottle][0] * delta_clone)
            series_clone.Longitude += (order_to_clone[i_bottle][1] * delta_clone)
            series_clone.Hex = series_clone.Hex.lower()
            acc.append(series_clone)

    data = pd.DataFrame(acc).reset_index(drop=True)
    data['Qté'] = data['Quantite']

    # TOTALS
    total = data['Qté'].count()
    total_chateaux = data.groupby(['ROUGES'])['Qté'].count()
    total_region = data.groupby(['Region'])['Qté'].count()
    total_sousregion = data.groupby(['Sous-Region'])['Qté'].count()
    total_aoc = data.groupby(['AOC/AOP'])['Qté'].count()
    total_year = data.groupby(['Annee'])['Qté'].count()

    a, b, c, d, e = st.columns([0.8, 0.5, 0.5, 0.8, 0.5])
    a.dataframe(total_chateaux.sort_values(ascending=False))
    b.dataframe(total_region.sort_values(ascending=False))
    c.dataframe(total_sousregion.sort_values(ascending=False))
    d.dataframe(total_aoc.sort_values(ascending=False))
    e.dataframe(total_year.sort_index(ascending=False))
    st.markdown(f'Total Bouteilles [{total}]')

    # MAP
    st.map(data=data, latitude='Latitude', longitude='Longitude', color='Hex')


    def color(s):
        return [f'background-color: white'] * 9 + [f'background-color: {s.Hex}'] + [f'background-color: white'] 

    st.dataframe(df.drop(columns=['Unnamed: 10'], errors='ignore').style.apply(color, axis=1))


if __name__ == "__main__":
    homepage_content()
