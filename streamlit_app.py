import streamlit as st

import streamlit as st
import pandas as pd
import numpy as np
from datetime import date

st.set_page_config(page_title="Leasing Restværdi - Revisorværktøj", layout="wide")

st.title("Leasing Restværdi – Revisorværktøj")
st.caption("Prototype til vurdering af restværdi, leasingøkonomi og revisionsrisiko")

# -----------------------------
# Sidebar input
# -----------------------------
st.sidebar.header("Leasingaftale")

bil_model = st.sidebar.text_input("Bilmodel", "VW Golf 8 R")
anskaffelsespris = st.sidebar.number_input("Anskaffelsespris inkl. afgift", min_value=0, value=420000, step=10000)
førstegangsydelse = st.sidebar.number_input("Førstegangsydelse", min_value=0, value=35000, step=5000)
månedlig_ydelse = st.sidebar.number_input("Månedlig leasingydelse", min_value=0, value=4995, step=250)
løbetid = st.sidebar.slider("Løbetid i måneder", 3, 60, 12)
fastsat_restværdi = st.sidebar.number_input("Fastsat restværdi i aftalen", min_value=0, value=300000, step=10000)

st.sidebar.header("Markedsforudsætninger")

markedspris_i_dag = st.sidebar.number_input("Aktuel markedspris for sammenlignelige biler", min_value=0, value=390000, step=10000)
årligt_værditab_pct = st.sidebar.slider("Forventet årligt værditab (%)", 0.0, 40.0, 15.0, 0.5)
km_pr_år = st.sidebar.number_input("Forventet km pr. år", min_value=0, value=20000, step=1000)
stand_score = st.sidebar.slider("Bilens forventede stand ved udløb", 1, 10, 7)

st.sidebar.header("Revisorjusteringer")

markedsusikkerhed_pct = st.sidebar.slider("Markedsusikkerhed / buffer (%)", 0.0, 30.0, 10.0, 0.5)
elbilsrisiko = st.sidebar.selectbox("Teknologisk/markedsmæssig risiko", ["Lav", "Middel", "Høj"])
dokumentation = st.sidebar.selectbox("Dokumentation for restværdi", ["Stærk", "Middel", "Svag"])

# -----------------------------
# Beregninger
# -----------------------------

løbetid_år = løbetid / 12

forventet_restværdi = markedspris_i_dag * ((1 - årligt_værditab_pct / 100) ** løbetid_år)

# km justering
normal_km = 20000
km_afvigelse = km_pr_år - normal_km
km_justering = -(km_afvigelse / 1000) * 1500 * løbetid_år

# stand justering
stand_justering = (stand_score - 7) * 5000

justeret_restværdi = forventet_restværdi + km_justering + stand_justering

forsigtig_restværdi = justeret_restværdi * (1 - markedsusikkerhed_pct / 100)

afvigelse = fastsat_restværdi - forsigtig_restværdi
afvigelse_pct = afvigelse / forsigtig_restværdi * 100 if forsigtig_restværdi != 0 else 0

samlede_ydelser = førstegangsydelse + månedlig_ydelse * løbetid
samlet_kontraktværdi = samlede_ydelser + fastsat_restværdi

# Risiko score
risiko_score = 0

if afvigelse_pct > 15:
    risiko_score += 3
elif afvigelse_pct > 7:
    risiko_score += 2
elif afvigelse_pct > 0:
    risiko_score += 1

if elbilsrisiko == "Høj":
    risiko_score += 2
elif elbilsrisiko == "Middel":
    risiko_score += 1

if dokumentation == "Svag":
    risiko_score += 3
elif dokumentation == "Middel":
    risiko_score += 1

if risiko_score >= 6:
    risiko_niveau = "Høj"
elif risiko_score >= 3:
    risiko_niveau = "Middel"
else:
    risiko_niveau = "Lav"

# -----------------------------
# Output
# -----------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric("Fastsat restværdi", f"{fastsat_restværdi:,.0f} kr.".replace(",", "."))
col2.metric("Forsigtig beregnet restværdi", f"{forsigtig_restværdi:,.0f} kr.".replace(",", "."))
col3.metric("Afvigelse", f"{afvigelse:,.0f} kr.".replace(",", "."))
col4.metric("Revisionsrisiko", risiko_niveau)

st.divider()

st.subheader("Restværdiberegning")

beregning_df = pd.DataFrame({
    "Element": [
        "Aktuel markedspris",
        "Forventet restværdi før justering",
        "Km-justering",
        "Stand-justering",
        "Justeret restværdi",
        "Forsigtighedsbuffer",
        "Forsigtig restværdi",
        "Fastsat restværdi",
        "Afvigelse"
    ],
    "Beløb": [
        markedspris_i_dag,
        forventet_restværdi,
        km_justering,
        stand_justering,
        justeret_restværdi,
        -justeret_restværdi * markedsusikkerhed_pct / 100,
        forsigtig_restværdi,
        fastsat_restværdi,
        afvigelse
    ]
})

st.dataframe(beregning_df, use_container_width=True, hide_index=True)

st.subheader("Følsomhedsanalyse")

scenarier = []

for værditab in [årligt_værditab_pct - 5, årligt_værditab_pct, årligt_værditab_pct + 5]:
    for buffer in [5, 10, 15, 20]:
        rv = markedspris_i_dag * ((1 - værditab / 100) ** løbetid_år)
        rv = rv + km_justering + stand_justering
        rv_forsigtig = rv * (1 - buffer / 100)
        scenarier.append({
            "Årligt værditab": f"{værditab:.1f}%",
            "Buffer": f"{buffer}%",
            "Beregnet restværdi": round(rv_forsigtig, 0),
            "Afvigelse ift. aftale": round(fastsat_restværdi - rv_forsigtig, 0)
        })

scenarie_df = pd.DataFrame(scenarier)
st.dataframe(scenarie_df, use_container_width=True, hide_index=True)

st.subheader("Revisorens vurdering")

if risiko_niveau == "Høj":
    konklusion = f"""
Restværdien vurderes som væsentligt risikofyldt. Den fastsatte restværdi på {fastsat_restværdi:,.0f} kr. 
overstiger den forsigtige beregnede restværdi på {forsigtig_restværdi:,.0f} kr. med {afvigelse:,.0f} kr.

Dette kan indikere risiko for overvurdering af aktivet/restværdien og bør give anledning til yderligere revisionshandlinger.
Revisor bør indhente ekstern markedsdokumentation, sammenligne med konkrete annoncer/salgspriser og vurdere behovet for nedskrivning eller noteoplysning.
"""
elif risiko_niveau == "Middel":
    konklusion = f"""
Restværdien vurderes at have moderat revisionsrisiko. Der er en afvigelse mellem aftalens restværdi og den forsigtige modelberegning.

Revisor bør udføre supplerende substanshandlinger, herunder sammenholde restværdien med markedsdata, historiske realiserede restværdier og bilens forventede stand/kilometer.
"""
else:
    konklusion = f"""
Restværdien vurderes umiddelbart som rimelig i forhold til de indtastede forudsætninger.

Revisor bør dog stadig dokumentere vurderingen, herunder anvendte markedsdata, værditabsforudsætninger og eventuelle usikkerheder.
"""

st.write(konklusion)

st.subheader("Forslag til revisionshandlinger")

handlinger = [
    "Indhent sammenlignelige markedspriser fra Bilbasen, Mobile.de eller interne salgsdata.",
    "Sammenhold fastsat restværdi med historiske realiserede salgspriser.",
    "Vurder om kilometerstand og bilens stand er realistisk indregnet.",
    "Lav følsomhedsanalyse på værditab, markedspris og restværdi.",
    "Vurder om der foreligger indikation på nedskrivningsbehov.",
    "Dokumentér væsentlige skøn og ledelsens forudsætninger.",
    "Overvej om usikkerheden skal kommunikeres til ledelsen eller i revisionsprotokollen."
]

for h in handlinger:
    st.checkbox(h)

# -----------------------------
# Eksport
# -----------------------------

rapport = f"""
REVISIONSNOTAT - LEASING RESTVÆRDI

Dato: {date.today()}
Bilmodel: {bil_model}

Fastsat restværdi: {fastsat_restværdi:,.0f} kr.
Forsigtig beregnet restværdi: {forsigtig_restværdi:,.0f} kr.
Afvigelse: {afvigelse:,.0f} kr.
Afvigelse i procent: {afvigelse_pct:.2f}%

Samlede leasingydelser: {samlede_ydelser:,.0f} kr.
Samlet kontraktværdi inkl. restværdi: {samlet_kontraktværdi:,.0f} kr.

Risikoniveau: {risiko_niveau}

Revisorens vurdering:
{konklusion}

Væsentlige forudsætninger:
- Årligt værditab: {årligt_værditab_pct}%
- Løbetid: {løbetid} måneder
- Km pr. år: {km_pr_år}
- Standscore: {stand_score}/10
- Markedsusikkerhed: {markedsusikkerhed_pct}%
- Dokumentation: {dokumentation}
"""

st.download_button(
    label="Download revisionsnotat",
    data=rapport,
    file_name="leasing_restvaerdi_revisionsnotat.txt",
    mime="text/plain"
)
