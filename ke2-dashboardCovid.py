import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as  sns
import altair as alt
import matplotlib.ticker as mtick
import plotly.graph_objects as go

# Memanggil Dataset
df = pd.read_csv("data_covid19_clean.csv")
df.columns = df.columns.str.strip().str.lower()
df['date'] = pd.to_datetime(df['date'])

# Judul dashboard
st.markdown("<h2 style='text-align: center;'> Dashboard Pesebaran Kasus Covid-19 Di Indonesia</h2>", unsafe_allow_html=True)

# Sidebar Filter
st.sidebar.title("Filter Data")

# Fitur Tanggal
tanggal_min = df['date'].min()
tanggal_max = df['date'].max()

date_range = st.sidebar.date_input("Rentang Tanggal",
                                    [tanggal_min, tanggal_max],
                                    min_value=tanggal_min,
                                    max_value=tanggal_max)

#Fitur  Pilih Provinsi

provinsi_list = sorted(df['province'].unique())
selected_provinsi = st.sidebar.selectbox("Pilih Provinsi", provinsi_list)

filtered_df = df[(df['province'] == selected_provinsi) &
                (df['date'] >= pd.to_datetime(date_range[0])) &
                (df['date'] <= pd.to_datetime(date_range[1]))]


#  Fitur Status
statuses = ['Kasus Baru', 'Sembuh', 'Kematian']
selected_statuses = st.sidebar.multiselect("Pilih status yang ingin ditampilkan:", statuses, default=statuses)

# Filter dataframe untuk provinsi yang dipilih
filtered_df = df[df['province'] == selected_provinsi]


# fitur Penjelasan Kolom


# Dasboard
# Total kasus Seluruh Indonesia
st.subheader('Total Kasus Covid-19 Di Indonesia')
col1, col2, col3 = st.columns(3)
col1.metric("Total Kasus", int(df['total_cases'].max()))
col2.metric("Total Sembuh", int(df['total_recovered'].max()))
col3.metric("Total Meninggal", int(df['total_deaths'].max()))


# Visualisasi
st.subheader(f"📈 Perkembangan Kasus Harian {selected_provinsi}")

# Filter data untuk provinsi yang dipilih
provinsi_data = df[df['province'] == selected_provinsi]

# Group berdasarkan tanggal
line_data = provinsi_data[['date', 'new_cases', 'new_recovered', 'new_deaths']] \
    .groupby('date').sum().reset_index()

# Chart Altair
line_chart = alt.Chart(line_data).transform_fold(
    ['new_cases', 'new_recovered', 'new_deaths'],
    as_=['Kategori', 'Jumlah']
).mark_line().encode(
    x='date:T',
    y='Jumlah:Q',
    color=alt.Color('Kategori:N',
        scale=alt.Scale(
            domain=['new_cases', 'new_recovered', 'new_deaths'],
            range=['orange', 'green', 'red']  
        )
    )
).properties(
    width=800,
    height=400
)

st.altair_chart(line_chart, use_container_width=True)


# format angka
def ribuan_formatter(x, pos):
    if x >= 1_000_000:
        return f"{x/1_000_000:.0f} "
    elif x >= 1_000:
        return f"{x/1_0000:.0f} "
    else:
        return str(int(x))

# Layout 3 Kolom 

col1, col2, col3 = st.columns(3)

# PIE CHART 

with col1:
    st.subheader("📊 Persentase Total")

    total_all = filtered_df[['total_cases', 'total_recovered', 'total_deaths']].max()

    fig1, ax1 = plt.subplots(figsize=(4, 4))
    ax1.pie(
        total_all,
        labels=['Kasus', 'Sembuh', 'Meninggal'],
        autopct='%1.1f%%',
        startangle=90,
        colors=['orange', 'green', 'red']
    )
    ax1.axis("equal")
    st.pyplot(fig1, use_container_width=True)

# BAR CHART KASUS 
with col2:
    st.subheader("Top 5 Kasus Tertinggi")

    top_cases = df.groupby('province')['total_cases'].max().nlargest(5).reset_index()

    fig2, ax2 = plt.subplots(figsize=(6, 6))
    bars = ax2.barh(top_cases['province'], top_cases['total_cases'], color='orange')

    for bar in bars:
        width = bar.get_width()
        ax2.text(width + 100, bar.get_y() + bar.get_height()/2,
                f'{int(width):,}', va='center', fontsize=9)

    ax2.set_xlabel("Total Kasus")
    ax2.set_ylabel("Provinsi")
    st.pyplot(fig2, use_container_width=True)

# BAR CHART KEMATIAN
    with col3:
        st.subheader("5 Kematian Tertinggi")

        top_deaths = df.groupby('province')['total_deaths'].max().nlargest(5).reset_index()

        fig3, ax3 = plt.subplots(figsize=(6, 6))
        bars = ax3.barh(top_deaths['province'], top_deaths['total_deaths'], color='red')

        for bar in bars:
            width = bar.get_width()
            ax3.text(width + 1000, bar.get_y() + bar.get_height()/2,
            f'{int(width):,}', va='center', fontsize=8)

        # Format angka di sumbu X
        ax3.xaxis.set_major_formatter(mtick.FuncFormatter(ribuan_formatter))

        ax3.set_xlabel("Total Meninggal")
        ax3.set_ylabel("Provinsi")
        st.pyplot(fig3, use_container_width=True)


#BAR CHART
#Buat area chart
st.title("📈 Area Chart Pesebaran COVID-19")

# Mapping nama pilihan user ke kolom dan warna
kategori_mapping = {
    'Kasus Baru': 'total_cases',
    'Sembuh': 'total_recovered',
    'Kematian': 'total_deaths'
}

kategori_colors = {
    'Kasus Baru': 'orange',
    'Sembuh': 'green',
    'Kematian': 'red'
}

fig = go.Figure()

# Loop sesuai pilihan pengguna
for kategori in selected_statuses:
    kolom = kategori_mapping.get(kategori)
    if kolom and kolom in filtered_df.columns:
        fig.add_trace(go.Scatter(
            x=filtered_df['date'],
            y=filtered_df[kolom],
            mode='lines',
            stackgroup='one',
            name=kategori,
            line=dict(color=kategori_colors[kategori]),
            fill='tonexty'
        ))

# Tampilan chart
fig.update_layout(
    xaxis_title="Tanggal",
    yaxis_title="Jumlah Total",
    legend_title="Kategori",
    height=500
)

st.plotly_chart(fig, use_container_width=True)
