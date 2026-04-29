import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(
    page_title="Revisorværktøj - Leasing Restværdi",
    layout="wide"
)

st.title("Revisorværktøj til vurdering af leasingrestværdi")
st.caption("Prototype til cand.merc.aud-speciale: restværdi, leasingøkonomi, skøn og revisionsrisiko")

# -----------------------------
# INPUT
# -----------------------------
st.sidebar.header("1. Leasingaftale")

bilmodel = st.sidebar.text_input("Bilmodel", "VW Golf 8 R")
anskaffelsespris = st.sidebar.number_input("Anskaffelsespris", value=420000, step=10000)
førstegangsydelse = st.sidebar.number_input("Førstegangsydelse", value=35000, step=5000)
månedlig_ydelse = st.sidebar.number_input("Månedlig ydelse", value=4995, step=250)
løbetid = st.sidebar.slider("Løbetid i måneder", 6, 60, 12)
aftalt_restværdi = st.sidebar.number_input("Aftalt restværdi", value=300000, step=10000)

st.sidebar.header("2. Markedsdata og skøn")

markedspris = st.sidebar.number_input("Markedspris i dag", value=390000, step=10000)
årligt_værditab = st.sidebar.slider("Forventet årligt værditab (%)", 0.0, 40.0, 15.0, 0.5)
km_pr_år = st.sidebar.number_input("Forventet km pr. år", value=20000, step=1000)
stand = st.sidebar.slider("Forventet stand ved udløb", 1, 10, 7)
buffer = st.sidebar.slider("Forsigtighedsbuffer (%)", 0.0, 30.0, 10.0, 0.5)

st.sidebar.header("3. Revisionsforhold")

dokumentation = st.sidebar.selectbox(
    "Dokumentation for restværdi",
    ["Stærk", "Middel", "Svag"]
)

marked = st.sidebar.selectbox(
    "Markedssituation",
    ["Stabilt", "Usikkert", "Meget usikkert"]
)

ledelsesskøn = st.sidebar.selectbox(
    "Ledelsens skøn virker",
    ["Konservativt", "Rimeligt", "Optimistisk"]
)

# -----------------------------
# BEREGNINGER
# -----------------------------
løbetid_år = løbetid / 12

model_restværdi = markedspris * ((1 - årligt_værditab / 100) ** løbetid_år)

# km-justering
normal_km = 20000
km_afvigelse = km_pr_år - normal_km
km_justering = -(km_afvigelse / 1000) * 1500 * løbetid_år

# stand-justering
stand_justering = (stand - 7) * 5000

justeret_restværdi = model_restværdi + km_justering + stand_justering
forsigtig_restværdi = justeret_restværdi * (1 - buffer / 100)

afvigelse = aftalt_restværdi - forsigtig_restværdi
afvigelse_pct = (afvigelse / forsigtig_restværdi * 100) if forsigtig_restværdi else 0

samlede_ydelser = førstegangsydelse + månedlig_ydelse * løbetid
samlet_leasingøkonomi = samlede_ydelser + aftalt_restværdi

# Risiko-score
risiko_score = 0

if afvigelse_pct > 20:
    risiko_score += 4
elif afvigelse_pct > 10:
    risiko_score += 3
elif afvigelse_pct > 5:
    risiko_score += 2
elif afvigelse_pct > 0:
    risiko_score += 1

if dokumentation == "Svag":
    risiko_score += 3
elif dokumentation == "Middel":
    risiko_score += 1

if marked == "Meget usikkert":
    risiko_score += 3
elif marked == "Usikkert":
    risiko_score += 1

if ledelsesskøn == "Optimistisk":
    risiko_score += 2
elif ledelsesskøn == "Konservativt":
    risiko_score -= 1

if risiko_score >= 7:
    risikoniveau = "Høj"
elif risiko_score >= 4:
    risikoniveau = "Middel"
else:
    risikoniveau = "Lav"

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overblik",
    "Restværdi",
    "Scenarier",
    "Revisorvurdering",
    "Bilag / rapport"
])

# -----------------------------
# TAB 1
# -----------------------------
with tab1:
    st.subheader("Overblik")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Aftalt restværdi", f"{aftalt_restværdi:,.0f} kr.".replace(",", "."))
    c2.metric("Forsigtig restværdi", f"{forsigtig_restværdi:,.0f} kr.".replace(",", "."))
    c3.metric("Afvigelse", f"{afvigelse:,.0f} kr.".replace(",", "."))
    c4.metric("Revisionsrisiko", risikoniveau)

    st.write("### Kort fortolkning")

    if risikoniveau == "Høj":
        st.error("Restværdien vurderes som højrisiko. Revisor bør udføre udvidede revisionshandlinger.")
    elif risikoniveau == "Middel":
        st.warning("Restværdien vurderes som moderat risikofyldt. Revisor bør indhente yderligere dokumentation.")
    else:
        st.success("Restværdien vurderes umiddelbart som rimelig ud fra de indtastede forudsætninger.")

    st.write("### Leasingøkonomi")

    økonomi_df = pd.DataFrame({
        "Post": [
            "Førstegangsydelse",
            "Månedlige ydelser i alt",
            "Samlede leasingydelser",
            "Aftalt restværdi",
            "Samlet økonomisk eksponering"
        ],
        "Beløb": [
            førstegangsydelse,
            månedlig_ydelse * løbetid,
            samlede_ydelser,
            aftalt_restværdi,
            samlet_leasingøkonomi
        ]
    })

    st.dataframe(økonomi_df, use_container_width=True, hide_index=True)

# -----------------------------
# TAB 2
# -----------------------------
with tab2:
    st.subheader("Restværdiberegning")

    rest_df = pd.DataFrame({
        "Element": [
            "Markedspris i dag",
            "Modelberegnet restværdi før justering",
            "Km-justering",
            "Stand-justering",
            "Justeret restværdi",
            "Forsigtighedsbuffer",
            "Forsigtig beregnet restværdi",
            "Aftalt restværdi",
            "Afvigelse"
        ],
        "Beløb": [
            markedspris,
            model_restværdi,
            km_justering,
            stand_justering,
            justeret_restværdi,
            -(justeret_restværdi * buffer / 100),
            forsigtig_restværdi,
            aftalt_restværdi,
            afvigelse
        ]
    })

    st.dataframe(rest_df, use_container_width=True, hide_index=True)

    st.write("### Værdifald over leasingperioden")

    udvikling = []
    for måned in range(0, løbetid + 1):
        år = måned / 12
        værdi = markedspris * ((1 - årligt_værditab / 100) ** år)
        udvikling.append({
            "Måned": måned,
            "Forventet markedsværdi": værdi
        })

    udvikling_df = pd.DataFrame(udvikling)
    st.line_chart(udvikling_df, x="Måned", y="Forventet markedsværdi")

# -----------------------------
# TAB 3
# -----------------------------
with tab3:
    st.subheader("Scenarieanalyse")

    scenarier = []

    for scenarie, ekstra_værditab, ekstra_buffer in [
        ("Optimistisk", -5, 5),
        ("Basis", 0, buffer),
        ("Forsigtig", 5, 15),
        ("Stress-test", 10, 25),
    ]:
        værditab_scenarie = max(0, årligt_værditab + ekstra_værditab)
        rv = markedspris * ((1 - værditab_scenarie / 100) ** løbetid_år)
        rv = rv + km_justering + stand_justering
        rv = rv * (1 - ekstra_buffer / 100)

        scenarier.append({
            "Scenarie": scenarie,
            "Årligt værditab": f"{værditab_scenarie:.1f}%",
            "Buffer": f"{ekstra_buffer:.1f}%",
            "Beregnet restværdi": round(rv, 0),
            "Afvigelse ift. aftale": round(aftalt_restværdi - rv, 0)
        })

    scenarie_df = pd.DataFrame(scenarier)
    st.dataframe(scenarie_df, use_container_width=True, hide_index=True)

    st.write("### Revisorens brug af scenarier")
    st.write("""
    Scenarieanalysen kan bruges til at vurdere, hvor følsom restværdien er over for ændringer i markedspris,
    værditab og forsigtighedsbuffer. Hvis restværdien kun fremstår rimelig i det optimistiske scenarie,
    kan det indikere øget risiko ved ledelsens skøn.
    """)

# -----------------------------
# TAB 4
# -----------------------------
with tab4:
    st.subheader("Revisorvurdering")

    st.write("### ISA-kobling")

    isa_df = pd.DataFrame({
        "Standard": [
            "ISA 315",
            "ISA 540",
            "ISA 500",
            "ISA 570"
        ],
        "Relevans": [
            "Identifikation og vurdering af risici for væsentlig fejlinformation.",
            "Revision af regnskabsmæssige skøn, herunder restværdier.",
            "Revisionsbevis for markedsdata, dokumentation og forudsætninger.",
            "Going concern kan være relevant, hvis fejlvurderede restværdier påvirker likviditet og kapitalgrundlag."
        ]
    })

    st.dataframe(isa_df, use_container_width=True, hide_index=True)

    st.write("### Automatisk revisionskonklusion")

    if risikoniveau == "Høj":
        konklusion = f"""
        Den aftalte restværdi vurderes at indebære høj revisionsrisiko. Den aftalte restværdi på 
        {aftalt_restværdi:,.0f} kr. overstiger den forsigtige modelberegnede restværdi på 
        {forsigtig_restværdi:,.0f} kr. med {afvigelse:,.0f} kr.

        Afvigelsen kan indikere, at ledelsens skøn er optimistisk, og at der kan være risiko for overvurdering.
        Revisor bør derfor udføre udvidede revisionshandlinger, herunder indhentelse af ekstern markedsdokumentation,
        følsomhedsanalyse og vurdering af behov for nedskrivning eller yderligere noteoplysninger.
        """
        st.error(konklusion)

    elif risikoniveau == "Middel":
        konklusion = f"""
        Den aftalte restværdi vurderes at indebære moderat revisionsrisiko. Der er en afvigelse mellem 
        den aftalte restværdi og den forsigtige modelberegning.

        Revisor bør indhente supplerende dokumentation, sammenholde restværdien med markedsdata og vurdere,
        om ledelsens forudsætninger er rimelige.
        """
        st.warning(konklusion)

    else:
        konklusion = f"""
        Den aftalte restværdi vurderes umiddelbart som rimelig i forhold til de indtastede forudsætninger.
        Revisor bør dog fortsat dokumentere de anvendte markedsdata og ledelsens centrale forudsætninger.
        """
        st.success(konklusion)

    st.write("### Foreslåede revisionshandlinger")

    handlinger = [
        "Indhent sammenlignelige markedspriser fra Bilbasen, Mobile.de eller interne salgsdata.",
        "Sammenhold aftalt restværdi med historisk realiserede restværdier.",
        "Vurder om kilometerstand og bilens stand er realistisk indregnet.",
        "Udfør følsomhedsanalyse på værditab, markedspris og restværdi.",
        "Vurder om der er indikation på nedskrivningsbehov.",
        "Dokumentér ledelsens forudsætninger og revisorens vurdering.",
        "Overvej kommunikation til ledelsen eller revisionsprotokollen ved væsentlig usikkerhed."
    ]

    for h in handlinger:
        st.checkbox(h)

# -----------------------------
# TAB 5
# -----------------------------
with tab5:
    st.subheader("Bilag / revisionsnotat")

    rapport = f"""
REVISIONSNOTAT - VURDERING AF LEASINGRESTVÆRDI

Dato: {date.today()}
Bilmodel: {bilmodel}

1. Leasingaftale
Anskaffelsespris: {anskaffelsespris:,.0f} kr.
Førstegangsydelse: {førstegangsydelse:,.0f} kr.
Månedlig ydelse: {månedlig_ydelse:,.0f} kr.
Løbetid: {løbetid} måneder
Aftalt restværdi: {aftalt_restværdi:,.0f} kr.

2. Modelberegning
Markedspris i dag: {markedspris:,.0f} kr.
Forventet årligt værditab: {årligt_værditab:.1f}%
Km pr. år: {km_pr_år:,.0f}
Standscore: {stand}/10
Forsigtighedsbuffer: {buffer:.1f}%

Modelberegnet restværdi før justering: {model_restværdi:,.0f} kr.
Justeret restværdi: {justeret_restværdi:,.0f} kr.
Forsigtig beregnet restværdi: {forsigtig_restværdi:,.0f} kr.
Afvigelse: {afvigelse:,.0f} kr.
Afvigelse i procent: {afvigelse_pct:.2f}%

3. Revisionsmæssig vurdering
Risikoniveau: {risikoniveau}
Dokumentation: {dokumentation}
Markedssituation: {marked}
Ledelsens skøn: {ledelsesskøn}

4. Revisorens konklusion
{konklusion}

5. Foreslåede revisionshandlinger
- Indhent eksterne markedsdata.
- Sammenhold med historiske realiserede salgspriser.
- Udfør følsomhedsanalyse.
- Vurder behov for nedskrivning eller noteoplysning.
- Dokumentér vurderingen som led i revisionen af regnskabsmæssige skøn.

Bemærkning:
Denne prototype er udarbejdet som et analytisk værktøj til specialeformål og kan ikke erstatte en egentlig revisionsmæssig vurdering.
"""

    st.text_area("Revisionsnotat", rapport, height=500)

    st.download_button(
        label="Download revisionsnotat",
        data=rapport,
        file_name="revisionsnotat_leasing_restvaerdi.txt",
        mime="text/plain"
    )
